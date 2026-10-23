from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repository.product import ProductRepository
from app.infrastructure.persistence.repositories.product_repo import SqlProductRepository
from tests.integration.factories import (
    add_allergen,
    add_category,
    add_image,
    add_product,
    add_variant,
    link_allergen,
)


def make_repository(session: AsyncSession) -> ProductRepository:
    # аннотация проверяет (mypy), что реализация соответствует контракту
    return SqlProductRepository(session)


async def test_returns_name_in_requested_locale(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "napoleon", {"ru": "Наполеон", "en": "Napoleon"})

    (item,) = await make_repository(session).list_active("en")

    assert (item.product.slug, item.locale, item.name) == ("napoleon", "en", "Napoleon")
    assert item.description == "Napoleon (description)"


async def test_falls_back_to_default_locale(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "napoleon", {"ru": "Наполеон"})  # нет fr

    (item,) = await make_repository(session).list_active("fr")

    assert item.name == "Наполеон"
    assert item.locale == "ru"  # реальный язык ответа, а не запрошенный


async def test_skips_product_without_usable_translation(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "only-english", {"en": "Only English"})  # нет ru

    assert await make_repository(session).list_active("fr") == []


async def test_skips_inactive_product(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "hidden", {"ru": "Скрытый"}, is_active=False)

    assert await make_repository(session).list_active("ru") == []


async def test_skips_product_in_inactive_category(session: AsyncSession) -> None:
    archive = await add_category(session, "archive", {"ru": "Архив"}, is_active=False)
    await add_product(session, archive, "old", {"ru": "Старый"})

    assert await make_repository(session).list_active("ru") == []


async def test_skips_product_without_active_variant(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "no-variant", {"ru": "Без цены"}, with_variant=False)
    only_inactive = await add_product(
        session, cakes, "inactive-variant", {"ru": "Неактивный"}, with_variant=False
    )
    await add_variant(session, only_inactive, price="50.00", is_active=False)

    assert await make_repository(session).list_active("ru") == []


async def test_orders_by_sort_order_then_id(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "c", {"ru": "C"}, sort_order=2)
    await add_product(session, cakes, "a", {"ru": "A"}, sort_order=1)
    await add_product(session, cakes, "b", {"ru": "B"}, sort_order=1)

    result = await make_repository(session).list_active("ru")

    assert [p.product.slug for p in result] == ["a", "b", "c"]


async def test_loads_active_variants_in_order(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    product = await add_product(session, cakes, "napoleon", {"ru": "Наполеон"}, with_variant=False)
    await add_variant(session, product, price="2500.00", weight_g=2000, sort_order=2)
    await add_variant(session, product, price="1300.50", weight_g=1000, sort_order=1)
    await add_variant(session, product, price="1.00", weight_g=500, is_active=False)

    (item,) = await make_repository(session).list_active("ru")

    assert [(v.weight_g, v.price) for v in item.variants] == [
        (1000, Decimal("1300.50")),
        (2000, Decimal("2500.00")),
    ]
    assert all(v.product_id == product.id for v in item.variants)


async def test_loads_images_in_order(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    product = await add_product(session, cakes, "napoleon", {"ru": "Наполеон"})
    await add_image(session, product, "/img/second.jpg", sort_order=2)
    await add_image(session, product, "/img/first.jpg", sort_order=1)

    (item,) = await make_repository(session).list_active("ru")

    assert [i.path for i in item.images] == ["/img/first.jpg", "/img/second.jpg"]


async def test_loads_allergens(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    product = await add_product(session, cakes, "napoleon", {"ru": "Наполеон"})
    nuts = await add_allergen(session, "nuts")
    gluten = await add_allergen(session, "gluten")
    await link_allergen(session, product, nuts)
    await link_allergen(session, product, gluten)

    (item,) = await make_repository(session).list_active("ru")

    assert [a.code for a in item.allergens] == ["gluten", "nuts"]  # по code


async def test_relations_are_attached_to_the_right_product(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    first = await add_product(session, cakes, "first", {"ru": "Первый"}, sort_order=1)
    second = await add_product(session, cakes, "second", {"ru": "Второй"}, sort_order=2)
    await add_image(session, first, "/img/first.jpg")
    await add_variant(session, second, price="777.00", weight_g=300)
    nuts = await add_allergen(session, "nuts")
    await link_allergen(session, second, nuts)

    a, b = await make_repository(session).list_active("ru")

    assert [i.path for i in a.images] == ["/img/first.jpg"]
    assert a.allergens == ()
    assert [v.price for v in b.variants] == [Decimal("100.00"), Decimal("777.00")]
    assert b.images == ()
    assert [x.code for x in b.allergens] == ["nuts"]


async def test_product_without_images_and_allergens_has_empty_tuples(
    session: AsyncSession,
) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "plain", {"ru": "Простой"})

    (item,) = await make_repository(session).list_active("ru")

    assert item.images == ()
    assert item.allergens == ()
    assert len(item.variants) == 1


async def test_list_active_by_category(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    cookies = await add_category(session, "cookies", {"ru": "Печенье"})
    await add_product(session, cakes, "napoleon", {"ru": "Наполеон"})
    await add_product(session, cookies, "oatmeal", {"ru": "Овсяное"})

    result = await make_repository(session).list_active_by_category("cookies", "ru")

    assert [p.product.slug for p in result] == ["oatmeal"]


async def test_list_active_by_unknown_or_inactive_category_is_empty(
    session: AsyncSession,
) -> None:
    archive = await add_category(session, "archive", {"ru": "Архив"}, is_active=False)
    await add_product(session, archive, "old", {"ru": "Старый"})
    repository = make_repository(session)

    assert await repository.list_active_by_category("archive", "ru") == []
    assert await repository.list_active_by_category("does-not-exist", "ru") == []


async def test_get_active_by_slug(session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "napoleon", {"ru": "Наполеон", "en": "Napoleon"})
    await add_product(session, cakes, "hidden", {"ru": "Скрытый"}, is_active=False)
    repository = make_repository(session)

    found = await repository.get_active_by_slug("napoleon", "en")
    assert found is not None
    assert found.name == "Napoleon"
    assert len(found.variants) == 1
    assert await repository.get_active_by_slug("hidden", "ru") is None
    assert await repository.get_active_by_slug("missing", "ru") is None
