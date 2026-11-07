from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from app.domain.email import is_valid_email
from app.domain.money import Money
from app.domain.phone import is_valid_phone


class LeadStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CONVERTED = "converted"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class NewLead:
    name: str
    phone: str
    email: str | None = None
    comment: str | None = None
    # поля индивидуального заказа
    desired_date: date | None = None
    servings: int | None = None
    budget: Money | None = None
    decor: str | None = None
    design_description: str | None = None

    def __post_init__(self) -> None:
        _validate_lead_fields(self.name, self.phone, self.email, self.servings, self.budget)


@dataclass(frozen=True, slots=True)
class Lead:
    """Заявка на индивидуальный заказ. После согласования превращается в Order."""

    id: int
    status: LeadStatus
    customer_id: int | None
    converted_order_id: int | None
    name: str
    phone: str
    email: str | None
    comment: str | None
    # поля индивидуального заказа
    desired_date: date | None
    servings: int | None
    budget: Money | None
    decor: str | None
    design_description: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        _validate_lead_fields(self.name, self.phone, self.email, self.servings, self.budget)


@dataclass(frozen=True, slots=True)
class LeadAttachment:
    id: int
    lead_id: int
    path: str
    original_name: str | None
    created_at: datetime


def _validate_lead_fields(
    name: str, phone: str, email: str | None, servings: int | None, budget: Money | None
) -> None:
    if not name.strip():
        raise ValueError("некорректное имя")
    if not is_valid_phone(phone):
        raise ValueError(f"phone должен быть в формате E.164: {phone!r}")
    if email is not None and not is_valid_email(email):
        raise ValueError("неправильный формат почты")
    if servings is not None and servings <= 0:
        raise ValueError("servings должен быть > 0")
    if budget is not None and budget < 0:
        raise ValueError("budget не может быть отрицательным")
