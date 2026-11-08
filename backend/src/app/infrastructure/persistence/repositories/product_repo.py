from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.allergen import Allergen
from app.domain.locale import DEFAULT_LOCALE, Locale, parse_locale
from app.domain.product import (
    LocalizedProduct,
    Product,
    ProductImage,
    ProductVariant,
)
from app.infrastructure.persistence.model.allergen import AllergenModel
from app.infrastructure.persistence.model.category import CategoryModel
from app.infrastructure.persistence.model.product import (
    ProductAllergenModel,
    ProductImageModel,
    ProductModel,
    ProductTranslationModel,
    ProductVariantModel,
)


def _to_product(product: ProductModel) -> Product:
    return Product(
        id=product.id,
        category_id=product.category_id,
        slug=product.slug,
        sort_order=product.sort_order,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def _to_variant(variant: ProductVariantModel) -> ProductVariant:
    return ProductVariant(
        id=variant.id,
        product_id=variant.product_id,
        weight_g=variant.weight_g,
        pieces=variant.pieces,
        price=variant.price,
        sort_order=variant.sort_order,
        is_active=variant.is_active,
    )


def _to_image(image: ProductImageModel) -> ProductImage:
    return ProductImage(
        id=image.id,
        product_id=image.product_id,
        path=image.path,
        sort_order=image.sort_order,
    )


def _to_allergen(allergen: AllergenModel) -> Allergen:
    return Allergen(id=allergen.id, code=allergen.code)


def _to_localized(
    product: ProductModel,
    requested: ProductTranslationModel | None,
    fallback: ProductTranslationModel | None,
    variants: Sequence[ProductVariant],
    images: Sequence[ProductImage],
    allergens: Sequence[Allergen],
) -> LocalizedProduct:
    # перевод на запрошенный язык важнее; иначе язык по умолчанию
    translation = requested or fallback
    if translation is None:  # SQL это уже отфильтровал; защита от будущих правок запроса
        raise LookupError(f"Product {product.id} has no usable translation")
    return LocalizedProduct(
        product=_to_product(product),
        locale=parse_locale(translation.locale),
        name=translation.name,
        description=translation.description,
        variants=tuple(variants),
        images=tuple(images),
        allergens=tuple(allergens),
    )


def _visible_products_select(
    locale: Locale,
) -> Select[ProductModel, ProductTranslationModel, ProductTranslationModel]:
    """Товары витрины + перевод на нужный язык + перевод на язык по умолчанию (оба LEFT JOIN).

    Видимый товар: активный, в активной категории, с переводом и хотя бы одним активным
    вариантом (без варианта нет цены).
    """
    requested = aliased(ProductTranslationModel)
    fallback = aliased(ProductTranslationModel)
    has_active_variant = (
        select(ProductVariantModel.id)
        .where(
            ProductVariantModel.product_id == ProductModel.id,
            ProductVariantModel.is_active,
        )
        .exists()
    )
    return (
        select(ProductModel, requested, fallback)
        .join(CategoryModel, CategoryModel.id == ProductModel.category_id)
        .outerjoin(
            requested,
            and_(requested.product_id == ProductModel.id, requested.locale == locale),
        )
        .outerjoin(
            fallback,
            and_(fallback.product_id == ProductModel.id, fallback.locale == DEFAULT_LOCALE),
        )
        .where(
            ProductModel.is_active,
            CategoryModel.is_active,
            or_(requested.product_id.is_not(None), fallback.product_id.is_not(None)),
            has_active_variant,
        )
    )


class SqlProductRepository:
    """Реализация ProductRepository (domain/repository/product.py) на SQLAlchemy.

    Сессию получает снаружи и НЕ коммитит. Загрузка - 4 запроса независимо от числа товаров:
    основной (товары + переводы) и по одному на варианты, картинки и аллергены
    (`WHERE product_id IN (...)`). JOIN всех связей в один запрос размножил бы строки
    (3 варианта x 4 картинки x 2 аллергена = 24 строки на товар).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self, locale: Locale) -> list[LocalizedProduct]:
        stmt = _visible_products_select(locale).order_by(ProductModel.sort_order, ProductModel.id)
        return await self._load(stmt)

    async def list_active_by_category(
        self, category_slug: str, locale: Locale
    ) -> list[LocalizedProduct]:
        stmt = (
            _visible_products_select(locale)
            .where(CategoryModel.slug == category_slug)
            .order_by(ProductModel.sort_order, ProductModel.id)
        )
        return await self._load(stmt)

    async def get_active_by_slug(self, slug: str, locale: Locale) -> LocalizedProduct | None:
        stmt = _visible_products_select(locale).where(ProductModel.slug == slug)
        items = await self._load(stmt)
        return items[0] if items else None

    async def _load(
        self,
        stmt: Select[ProductModel, ProductTranslationModel, ProductTranslationModel],
    ) -> list[LocalizedProduct]:

        result = await self._session.execute(stmt)
        rows = result.all()  # list[tuple[ProductModel, Translation, Translation]]
        if not rows:
            return []
        ids = [product.id for product, _, _ in rows]
        variants = await self._variants(ids)
        images = await self._images(ids)
        allergens = await self._allergens(ids)
        return [
            _to_localized(
                product,
                requested,
                fallback,
                variants[product.id],
                images[product.id],
                allergens[product.id],
            )
            for product, requested, fallback in rows
        ]

    async def _variants(self, product_ids: list[int]) -> defaultdict[int, list[ProductVariant]]:
        stmt = (
            select(ProductVariantModel)
            .where(ProductVariantModel.product_id.in_(product_ids), ProductVariantModel.is_active)
            .order_by(ProductVariantModel.sort_order, ProductVariantModel.id)
        )
        result: defaultdict[int, list[ProductVariant]] = defaultdict(list)
        for model in await self._session.scalars(stmt):
            result[model.product_id].append(_to_variant(model))
        return result

    async def _images(self, product_ids: list[int]) -> defaultdict[int, list[ProductImage]]:
        stmt = (
            select(ProductImageModel)
            .where(ProductImageModel.product_id.in_(product_ids))
            .order_by(ProductImageModel.sort_order, ProductImageModel.id)
        )
        result: defaultdict[int, list[ProductImage]] = defaultdict(list)
        for model in await self._session.scalars(stmt):
            result[model.product_id].append(_to_image(model))
        return result

    async def _allergens(self, product_ids: list[int]) -> defaultdict[int, list[Allergen]]:
        stmt = (
            select(ProductAllergenModel.product_id, AllergenModel)
            .join(AllergenModel, AllergenModel.id == ProductAllergenModel.allergen_id)
            .where(ProductAllergenModel.product_id.in_(product_ids))
            .order_by(AllergenModel.code)
        )
        result: defaultdict[int, list[Allergen]] = defaultdict(list)
        for product_id, model in await self._session.execute(stmt):
            result[product_id].append(_to_allergen(model))
        return result
