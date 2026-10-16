from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Payment:
    id: int
    order_id: int
    amount: int
    payment_method_id: int
    payment_status_id: int
    paid_at: datetime
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PaymentStatus:
    id: int
    code: str


@dataclass(frozen=True, slots=True)
class PaymentMethod:
    id: int
    code: str
