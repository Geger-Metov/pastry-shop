from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class Customer:
    id: int
    name: str
    phone: str
    email: str
    preferred_contact: str
    birthday: date
    notes: str
    is_active: bool
    created_at: datetime
