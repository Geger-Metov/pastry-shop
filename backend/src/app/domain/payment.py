from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.domain.money import Money


class PaymentMethod(StrEnum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    QR = "qr"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass(frozen=True, slots=True)
class Payment:
    id: int
    order_id: int
    amount: Money
    method: PaymentMethod
    status: PaymentStatus
    external_id: str | None  # id транзакции у платёжного провайдера
    paid_at: datetime | None
    created_at: datetime

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount должен быть > 0")
        if self.status is PaymentStatus.PAID and self.paid_at is None:
            raise ValueError("у оплаченного платежа должна быть дата paid_at")
