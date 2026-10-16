from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class StaffRole(StrEnum):
    ADMIN = "admin"
    BAKER = "baker"


@dataclass(frozen=True, slots=True)
class StaffUser:
    id: int
    email: str
    password_hash: str
    name: str
    role: StaffRole
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
