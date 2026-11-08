from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.domain.lead import Lead, LeadStatus, NewLead

PHONE = "+996555123456"


def make_lead(**overrides: object) -> Lead:
    fields: dict[str, object] = {
        "id": 1,
        "status": LeadStatus.NEW,
        "customer_id": None,
        "converted_order_id": None,
        "name": "Анна",
        "phone": PHONE,
        "email": None,
        "comment": None,
        "desired_date": None,
        "servings": None,
        "budget": None,
        "decor": None,
        "design_description": None,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    fields.update(overrides)
    return Lead(**fields)  # type: ignore[arg-type]


def test_new_lead_minimum_is_name_and_phone() -> None:
    lead = NewLead(name="Анна", phone=PHONE)

    assert lead.email is None
    assert lead.servings is None


def test_new_lead_accepts_all_fields() -> None:
    lead = NewLead(
        name="Анна",
        phone=PHONE,
        email="anna@example.com",
        desired_date=date(2030, 1, 1),
        servings=10,
        budget=Decimal("5000.00"),
    )

    assert lead.servings == 10


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": ""},
        {"name": "   "},
        {"phone": "0555123456"},
        {"phone": "+996"},
        {"email": "not-an-email"},
        {"email": "a b@example.com"},
        {"servings": 0},
        {"servings": -1},
        {"budget": Decimal("-0.01")},
    ],
)
def test_new_lead_rejects_invalid_values(overrides: dict[str, object]) -> None:
    fields: dict[str, object] = {"name": "Анна", "phone": PHONE} | overrides

    with pytest.raises(ValueError):
        NewLead(**fields)  # type: ignore[arg-type]


def test_lead_shares_the_same_rules_as_new_lead() -> None:
    make_lead()  # корректная заявка создаётся

    for overrides in ({"name": "  "}, {"email": "bad"}, {"servings": 0}, {"phone": "123"}):
        with pytest.raises(ValueError):
            make_lead(**overrides)


def test_zero_budget_is_allowed() -> None:
    assert NewLead(name="Анна", phone=PHONE, budget=Decimal("0")).budget == 0
