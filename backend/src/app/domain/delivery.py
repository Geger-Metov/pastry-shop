from dataclasses import dataclass
from enum import StrEnum

from app.domain.money import Money
from app.domain.phone import is_valid_phone


class DeliveryType(StrEnum):
    PICKUP = "pickup"
    DELIVERY = "delivery"


@dataclass(frozen=True, slots=True)
class Delivery:
    """Данные доставки. Существует только у заказов с DeliveryType.DELIVERY."""

    id: int
    order_id: int
    address: str
    recipient: str
    phone: str
    cost: Money
    comment: str | None

    def __post_init__(self) -> None:
        if self.cost < 0:
            raise ValueError("cost не может быть отрицательной")
        if not is_valid_phone(self.phone):
            raise ValueError(f"phone должен быть в формате E.164: {self.phone!r}")
