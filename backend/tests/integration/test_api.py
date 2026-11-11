"""Тесты HTTP-слоя: приложение + реальная БД (сессия теста откатывается после каждого теста)."""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.conftest import ORIGIN
from tests.integration.factories import (
    add_allergen,
    add_category,
    add_image,
    add_product,
    add_variant,
    link_allergen,
)


async def test_list_categories_uses_default_locale(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await add_category(session, "cakes", {"ru": "Торты", "en": "Cakes"})

    response = await client.get("/categories")

    assert response.status_code == 200
    (item,) = response.json()
    assert (item["slug"], item["name"], item["locale"]) == ("cakes", "Торты", "ru")


async def test_list_categories_in_requested_locale(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await add_category(session, "cakes", {"ru": "Торты", "en": "Cakes"})

    response = await client.get("/categories", params={"locale": "en"})

    assert [(c["name"], c["locale"]) for c in response.json()] == [("Cakes", "en")]


async def test_unsupported_locale_falls_back_to_default(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await add_category(session, "cakes", {"ru": "Торты", "en": "Cakes"})

    response = await client.get("/categories", params={"locale": "de"})

    assert response.status_code == 200
    assert [c["locale"] for c in response.json()] == ["ru"]


async def test_list_categories_hides_inactive(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await add_category(session, "visible", {"ru": "Виден"})
    await add_category(session, "hidden", {"ru": "Скрыт"}, is_active=False)

    response = await client.get("/categories")

    assert [c["slug"] for c in response.json()] == ["visible"]


async def test_list_products_has_full_shape(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    product = await add_product(session, cakes, "napoleon", {"ru": "Наполеон"}, with_variant=False)
    await add_variant(session, product, price="1300.50", weight_g=1000)
    await add_image(session, product, "/img/napoleon.jpg")
    await link_allergen(session, product, await add_allergen(session, "gluten"))

    response = await client.get("/products")

    assert response.status_code == 200
    (item,) = response.json()
    assert item["slug"] == "napoleon"
    assert item["category_id"] == cakes.id
    assert item["name"] == "Наполеон"
    assert item["locale"] == "ru"
    assert item["variants"][0]["weight_g"] == 1000
    assert item["images"][0]["path"] == "/img/napoleon.jpg"
    assert item["allergens"][0]["code"] == "gluten"


async def test_price_is_serialized_as_string(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    product = await add_product(session, cakes, "napoleon", {"ru": "Наполеон"}, with_variant=False)
    await add_variant(session, product, price="1300.50")

    response = await client.get("/products")

    assert response.json()[0]["variants"][0]["price"] == "1300.50"  # не число: без потери точности


async def test_list_products_filtered_by_category(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    cookies = await add_category(session, "cookies", {"ru": "Печенье"})
    await add_product(session, cakes, "napoleon", {"ru": "Наполеон"})
    await add_product(session, cookies, "oatmeal", {"ru": "Овсяное"})

    response = await client.get("/products", params={"category": "cookies"})

    assert [p["slug"] for p in response.json()] == ["oatmeal"]


async def test_unknown_category_gives_empty_list(client: httpx.AsyncClient) -> None:
    response = await client.get("/products", params={"category": "nope"})

    assert response.status_code == 200
    assert response.json() == []


async def test_get_shop_currency(client: httpx.AsyncClient) -> None:
    response = await client.get("/shop")
    assert response.status_code == 200
    assert response.json()["currency"] == "RUB"


async def test_get_product_by_slug(client: httpx.AsyncClient, session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "napoleon", {"ru": "Наполеон", "fr": "Napoléon"})

    response = await client.get("/products/napoleon", params={"locale": "fr"})

    assert response.status_code == 200
    assert response.json()["name"] == "Napoléon"


async def test_get_missing_product_is_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/products/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


async def test_get_hidden_product_is_404(client: httpx.AsyncClient, session: AsyncSession) -> None:
    cakes = await add_category(session, "cakes", {"ru": "Торты"})
    await add_product(session, cakes, "hidden", {"ru": "Скрытый"}, is_active=False)

    assert (await client.get("/products/hidden")).status_code == 404


async def test_health_checks_database(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_is_not_in_openapi(client: httpx.AsyncClient) -> None:
    # служебный эндпоинт: без него сгенерированные типы фронтенда не меняются
    assert "/health" not in (await client.get("/openapi.json")).json()["paths"]


async def test_openapi_schema_is_generated(client: httpx.AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    assert {"/categories", "/products", "/products/{slug}"} <= set(response.json()["paths"])


async def test_cors_allows_configured_origin_only(client: httpx.AsyncClient) -> None:
    allowed = await client.get("/categories", headers={"Origin": ORIGIN})
    other = await client.get("/categories", headers={"Origin": "http://evil.example"})

    assert allowed.headers["access-control-allow-origin"] == ORIGIN
    assert "access-control-allow-origin" not in other.headers
