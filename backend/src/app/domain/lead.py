from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from app.domain.money import Money
from app.domain.phone import is_valid_phone


class LeadStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CONVERTED = "converted"
    REJECTED = "rejected"


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
        if not is_valid_phone(self.phone):
            raise ValueError(f"phone должен быть в формате E.164: {self.phone!r}")
        if self.servings is not None and self.servings <= 0:
            raise ValueError("servings должен быть > 0")
        if self.budget is not None and self.budget < 0:
            raise ValueError("budget не может быть отрицательным")


@dataclass(frozen=True, slots=True)
class LeadAttachment:
    id: int
    lead_id: int
    path: str
    original_name: str | None
    created_at: datetime
