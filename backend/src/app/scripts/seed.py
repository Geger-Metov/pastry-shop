"""Заполняет БД демо-данными. Можно запускать сколько угодно раз: дублей не будет.

uv run python -m app.scripts.seed
docker compose run --rm backend python -m app.scripts.seed
"""

import asyncio

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_engine, get_sessionmaker
from app.infrastructure.persistence.model.allergen import AllergenModel
from app.infrastructure.persistence.model.category import CategoryModel, CategoryTranslationModel
from app.infrastructure.persistence.model.product import (
    ProductAllergenModel,
    ProductImageModel,
    ProductModel,
    ProductTranslationModel,
    ProductVariantModel,
)
from app.scripts.seed_data import (
    ALLERGEN_CODES,
    CATEGORIES,
    PRODUCTS,
    CategorySeed,
    ProductSeed,
    Texts,
)


async def seed(session: AsyncSession) -> None:
    """Записывает демо-данные в сессию. НЕ коммитит: коммитит вызывающий код.

    Везде INSERT ... ON CONFLICT DO UPDATE: повторный запуск обновляет строки, а не дублирует.
    Справочник locale здесь не трогаем: его заполняет миграция.
    """
    allergen_ids = {code: await _upsert_allergen(session, code) for code in ALLERGEN_CODES}
    category_ids = {seed.slug: await _upsert_category(session, seed) for seed in CATEGORIES}
    for product in PRODUCTS:
        await _upsert_product(session, product, category_ids[product.category], allergen_ids)


async def _upsert_allergen(session: AsyncSession, code: str) -> int:
    stmt = (
        insert(AllergenModel)
        .values(code=code)
        .on_conflict_do_update(index_elements=["code"], set_={"code": code})
        .returning(AllergenModel.id)
    )
    return (await session.execute(stmt)).scalar_one()


async def _upsert_category(session: AsyncSession, seed: CategorySeed) -> int:
    stmt = (
        insert(CategoryModel)
        .values(slug=seed.slug, sort_order=seed.sort_order, is_active=True)
        .on_conflict_do_update(
            index_elements=["slug"], set_={"sort_order": seed.sort_order, "is_active": True}
        )
        .returning(CategoryModel.id)
    )
    category_id = (await session.execute(stmt)).scalar_one()
    await _upsert_translations(
        session, CategoryTranslationModel, "category_id", category_id, seed.texts
    )
    return category_id


async def _upsert_product(
    session: AsyncSession,
    seed: ProductSeed,
    category_id: int,
    allergen_ids: dict[str, int],
) -> None:
    stmt = (
        insert(ProductModel)
        .values(category_id=category_id, slug=seed.slug, sort_order=seed.sort_order, is_active=True)
        .on_conflict_do_update(
            index_elements=["slug"],
            set_={"category_id": category_id, "sort_order": seed.sort_order, "is_active": True},
        )
        .returning(ProductModel.id)
    )
    product_id = (await session.execute(stmt)).scalar_one()
    await _upsert_translations(
        session, ProductTranslationModel, "product_id", product_id, seed.texts
    )

    for order, variant in enumerate(seed.variants, start=1):
        stmt_variant = insert(ProductVariantModel).values(
            product_id=product_id,
            weight_g=variant.weight_g,
            pieces=variant.pieces,
            price=variant.price,
            sort_order=order,
            is_active=True,
        )
        await session.execute(
            stmt_variant.on_conflict_do_update(
                index_elements=["product_id", "weight_g", "pieces"],
                set_={"price": variant.price, "sort_order": order, "is_active": True},
            )
        )

    # у картинок нет естественного ключа: заменяем набор целиком
    await session.execute(
        delete(ProductImageModel).where(ProductImageModel.product_id == product_id)
    )
    for order, path in enumerate(seed.images, start=1):
        session.add(ProductImageModel(product_id=product_id, path=path, sort_order=order))

    for code in seed.allergens:
        await session.execute(
            insert(ProductAllergenModel)
            .values(product_id=product_id, allergen_id=allergen_ids[code])
            .on_conflict_do_nothing()
        )
    await session.flush()


async def _upsert_translations(
    session: AsyncSession,
    model: type[CategoryTranslationModel] | type[ProductTranslationModel],
    owner_column: str,
    owner_id: int,
    texts: Texts,
) -> None:
    stmt = insert(model).values(
        [
            {owner_column: owner_id, "locale": locale, "name": name, "description": description}
            for locale, (name, description) in texts.items()
        ]
    )
    await session.execute(
        stmt.on_conflict_do_update(
            index_elements=[owner_column, "locale"],
            set_={"name": stmt.excluded.name, "description": stmt.excluded.description},
        )
    )


async def main() -> None:
    async with get_sessionmaker()() as session:
        await seed(session)
        await session.commit()
    await get_engine().dispose()
    print("Seed done.")


if __name__ == "__main__":
    asyncio.run(main())
