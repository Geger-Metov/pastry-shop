from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from app.domain.locale import Locale
from app.domain.phone import is_valid_phone


class ContactMethod(StrEnum):
    PHONE = "phone"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    EMAIL = "email"


@dataclass(frozen=True, slots=True)
class Customer:
    id: int
    name: str
    phone: str
    email: str | None
    preferred_contact: ContactMethod | None
    locale: Locale
    birthday: date | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not is_valid_phone(self.phone):
            raise ValueError(f"phone должен быть в формате E.164: {self.phone!r}")
