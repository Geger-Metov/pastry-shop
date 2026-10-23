"""Помощники для интеграционных тестов: создают строки в БД через сессию теста."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.locale import Locale
from app.infrastructure.persistence.model.allergen import AllergenModel
from app.infrastructure.persistence.model.category import CategoryModel, CategoryTranslationModel
from app.infrastructure.persistence.model.product import (
    ProductAllergenModel,
    ProductImageModel,
    ProductModel,
    ProductTranslationModel,
    ProductVariantModel,
)


async def add_category(
    session: AsyncSession,
    slug: str,
    names: dict[Locale, str],
    *,
    sort_order: int = 0,
    is_active: bool = True,
    parent_id: int | None = None,
) -> CategoryModel:
    category = CategoryModel(
        slug=slug, sort_order=sort_order, is_active=is_active, parent_id=parent_id
    )
    session.add(category)
    await session.flush()  # получаем id
    session.add_all(
        CategoryTranslationModel(
            category_id=category.id, locale=locale, name=name, description=f"{name} (description)"
        )
        for locale, name in names.items()
    )
    await session.flush()
    return category


async def add_product(
    session: AsyncSession,
    category: CategoryModel,
    slug: str,
    names: dict[Locale, str],
    *,
    sort_order: int = 0,
    is_active: bool = True,
    with_variant: bool = True,
) -> ProductModel:
    """Товар с переводами и (по умолчанию) одним активным вариантом за 100.00."""
    product = ProductModel(
        category_id=category.id, slug=slug, sort_order=sort_order, is_active=is_active
    )
    session.add(product)
    await session.flush()
    session.add_all(
        ProductTranslationModel(
            product_id=product.id, locale=locale, name=name, description=f"{name} (description)"
        )
        for locale, name in names.items()
    )
    if with_variant:
        await add_variant(session, product, price="100.00")
    await session.flush()
    return product


async def add_variant(
    session: AsyncSession,
    product: ProductModel,
    *,
    price: str,
    weight_g: int | None = None,
    pieces: int | None = None,
    sort_order: int = 0,
    is_active: bool = True,
) -> ProductVariantModel:
    variant = ProductVariantModel(
        product_id=product.id,
        weight_g=weight_g,
        pieces=pieces,
        price=Decimal(price),
        sort_order=sort_order,
        is_active=is_active,
    )
    session.add(variant)
    await session.flush()
    return variant


async def add_image(
    session: AsyncSession, product: ProductModel, path: str, *, sort_order: int = 0
) -> ProductImageModel:
    image = ProductImageModel(product_id=product.id, path=path, sort_order=sort_order)
    session.add(image)
    await session.flush()
    return image


async def add_allergen(session: AsyncSession, code: str) -> AllergenModel:
    allergen = AllergenModel(code=code)
    session.add(allergen)
    await session.flush()
    return allergen


async def link_allergen(
    session: AsyncSession, product: ProductModel, allergen: AllergenModel
) -> None:
    session.add(ProductAllergenModel(product_id=product.id, allergen_id=allergen.id))
    await session.flush()
