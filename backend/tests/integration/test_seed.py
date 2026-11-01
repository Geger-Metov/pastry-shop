from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.model.allergen import AllergenModel
from app.infrastructure.persistence.model.category import CategoryModel
from app.infrastructure.persistence.model.product import (
    ProductImageModel,
    ProductModel,
    ProductVariantModel,
)
from app.infrastructure.persistence.repositories.category_repo import SqlCategoryRepository
from app.infrastructure.persistence.repositories.product_repo import SqlProductRepository
from app.scripts.seed import seed
from app.scripts.seed_data import ALLERGEN_CODES, CATEGORIES, PRODUCTS


async def _count(session: AsyncSession, model: type) -> int:
    return (await session.execute(select(func.count()).select_from(model))).scalar_one()


async def test_seed_creates_expected_rows(session: AsyncSession) -> None:
    await seed(session)

    assert await _count(session, CategoryModel) == len(CATEGORIES)
    assert await _count(session, ProductModel) == len(PRODUCTS)
    assert await _count(session, AllergenModel) == len(ALLERGEN_CODES)
    assert await _count(session, ProductVariantModel) == sum(len(p.variants) for p in PRODUCTS)
    assert await _count(session, ProductImageModel) == sum(len(p.images) for p in PRODUCTS)


async def test_seed_is_idempotent(session: AsyncSession) -> None:
    await seed(session)
    await seed(session)  # второй запуск не должен ничего дублировать

    assert await _count(session, CategoryModel) == len(CATEGORIES)
    assert await _count(session, ProductModel) == len(PRODUCTS)
    assert await _count(session, ProductVariantModel) == sum(len(p.variants) for p in PRODUCTS)
    assert await _count(session, ProductImageModel) == sum(len(p.images) for p in PRODUCTS)


async def test_seeded_data_is_visible_through_repositories_in_every_locale(
    session: AsyncSession,
) -> None:
    await seed(session)

    for locale in ("ru", "en", "fr"):
        categories = await SqlCategoryRepository(session).list_active(locale)
        products = await SqlProductRepository(session).list_active(locale)
        assert len(categories) == len(CATEGORIES)
        assert len(products) == len(PRODUCTS)
        assert all(c.locale == locale for c in categories)
        assert all(p.locale == locale for p in products)
        assert all(p.variants for p in products)
