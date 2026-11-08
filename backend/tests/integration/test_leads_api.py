import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.model.lead import LeadModel

VALID = {"name": "Анна", "phone": "+996555123456"}


async def count_leads(session: AsyncSession) -> int:
    return (await session.execute(select(func.count()).select_from(LeadModel))).scalar_one()


async def test_create_lead_returns_201_with_only_the_id(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    response = await client.post("/leads", json=VALID)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id"}  # персональные данные в ответ не возвращаем
    row = (await session.execute(select(LeadModel))).scalar_one()
    assert row.id == body["id"]
    assert row.status == "new"


async def test_create_lead_with_all_fields(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    response = await client.post(
        "/leads",
        json=VALID
        | {
            "email": " anna@example.com ",
            "comment": "Без орехов",
            "desired_date": "2099-01-01",
            "servings": 12,
            "budget": "7500.50",
            "decor": "Ягоды",
            "design_description": "Двухъярусный торт",
        },
    )

    assert response.status_code == 201
    row = (await session.execute(select(LeadModel))).scalar_one()
    assert row.email == "anna@example.com"  # пробелы по краям убраны
    assert row.servings == 12
    assert str(row.budget) == "7500.50"


async def test_national_phone_is_normalized_with_default_country_code(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    response = await client.post("/leads", json={"name": "Анна", "phone": "0555 123 456"})

    assert response.status_code == 201
    row = (await session.execute(select(LeadModel))).scalar_one()
    assert row.phone == "+996555123456"  # в тестовых настройках код страны 996


async def test_blank_optional_strings_are_saved_as_null(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    response = await client.post("/leads", json=VALID | {"email": "  ", "comment": ""})

    assert response.status_code == 201
    row = (await session.execute(select(LeadModel))).scalar_one()
    assert row.email is None
    assert row.comment is None


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"phone": "+996555123456"}, "name"),  # нет имени
        ({"name": "   ", "phone": "+996555123456"}, "name"),  # одни пробелы
        ({"name": "А", "phone": "+996555123456"}, "name"),  # слишком короткое
        ({"name": "А" * 101, "phone": "+996555123456"}, "name"),
        ({"name": "Анна"}, "phone"),  # нет телефона
        ({"name": "Анна", "phone": "abc"}, "phone"),
        ({"name": "Анна", "phone": "+996555123456", "email": "no-at-sign"}, "email"),
        ({"name": "Анна", "phone": "+996555123456", "servings": 0}, "servings"),
        ({"name": "Анна", "phone": "+996555123456", "servings": 1001}, "servings"),
        ({"name": "Анна", "phone": "+996555123456", "budget": "-1"}, "budget"),
        ({"name": "Анна", "phone": "+996555123456", "budget": "123456789012.00"}, "budget"),
        ({"name": "Анна", "phone": "+996555123456", "comment": "x" * 2001}, "comment"),
        ({"name": "Анна", "phone": "+996555123456", "desired_date": "не дата"}, "desired_date"),
    ],
)
async def test_invalid_input_gives_422_for_the_right_field_and_saves_nothing(
    client: httpx.AsyncClient, session: AsyncSession, payload: dict[str, object], field: str
) -> None:
    response = await client.post("/leads", json=payload)

    assert response.status_code == 422
    assert field in {item["loc"][-1] for item in response.json()["detail"]}
    assert await count_leads(session) == 0


async def test_past_date_gives_422_in_the_same_format(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    response = await client.post("/leads", json=VALID | {"desired_date": "2000-01-01"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "desired_date"]
    assert await count_leads(session) == 0


async def test_client_cannot_choose_status_or_customer(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    response = await client.post("/leads", json=VALID | {"status": "converted", "customer_id": 1})

    assert response.status_code == 201
    row = (await session.execute(select(LeadModel))).scalar_one()
    assert row.status == "new"
    assert row.customer_id is None


async def test_health_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_leads_endpoint_is_in_openapi(client: httpx.AsyncClient) -> None:
    schema = (await client.get("/openapi.json")).json()

    assert "post" in schema["paths"]["/leads"]
