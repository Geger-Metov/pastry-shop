from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repository.category import CategoryRepository
from app.infrastructure.persistence.repositories.category_repo import SqlCategoryRepository
from tests.integration.factories import add_category


def make_repository(session: AsyncSession) -> CategoryRepository:
    # аннотация проверяет (mypy), что реализация соответствует контракту
    return SqlCategoryRepository(session)


async def test_returns_name_in_requested_locale(session: AsyncSession) -> None:
    await add_category(session, "cakes", {"ru": "Торты", "en": "Cakes", "fr": "Gâteaux"})

    result = await make_repository(session).list_active("fr")

    assert [(c.category.slug, c.locale, c.name) for c in result] == [("cakes", "fr", "Gâteaux")]
    assert result[0].description == "Gâteaux (description)"


async def test_falls_back_to_default_locale(session: AsyncSession) -> None:
    await add_category(session, "cakes", {"ru": "Торты"})  # нет en

    (item,) = await make_repository(session).list_active("en")

    assert item.name == "Торты"
    assert item.locale == "ru"  # реальный язык ответа, а не запрошенный


async def test_skips_category_without_usable_translation(session: AsyncSession) -> None:
    await add_category(session, "only-english", {"en": "Only English"})  # нет ru (по умолчанию)

    assert await make_repository(session).list_active("fr") == []


async def test_skips_inactive_categories(session: AsyncSession) -> None:
    await add_category(session, "visible", {"ru": "Видимая"})
    await add_category(session, "hidden", {"ru": "Скрытая"}, is_active=False)

    result = await make_repository(session).list_active("ru")

    assert [c.category.slug for c in result] == ["visible"]


async def test_orders_by_sort_order_then_id(session: AsyncSession) -> None:
    await add_category(session, "c", {"ru": "C"}, sort_order=2)
    await add_category(session, "a", {"ru": "A"}, sort_order=1)
    await add_category(session, "b", {"ru": "B"}, sort_order=1)

    result = await make_repository(session).list_active("ru")

    assert [c.category.slug for c in result] == ["a", "b", "c"]


async def test_maps_parent_id(session: AsyncSession) -> None:
    parent = await add_category(session, "cakes", {"ru": "Торты"})
    await add_category(session, "bento", {"ru": "Бенто"}, parent_id=parent.id)

    result = {c.category.slug: c.category for c in await make_repository(session).list_active("ru")}

    assert result["cakes"].parent_id is None
    assert result["bento"].parent_id == parent.id


async def test_get_active_by_slug(session: AsyncSession) -> None:
    await add_category(session, "cakes", {"ru": "Торты", "en": "Cakes"})
    await add_category(session, "hidden", {"ru": "Скрытая"}, is_active=False)
    repository = make_repository(session)

    found = await repository.get_active_by_slug("cakes", "en")
    assert found is not None
    assert (found.category.slug, found.name, found.locale) == ("cakes", "Cakes", "en")

    assert await repository.get_active_by_slug("unknown", "en") is None
    assert await repository.get_active_by_slug("hidden", "ru") is None
