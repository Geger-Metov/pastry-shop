from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Final
from uuid import UUID

from app.domain.delivery import DeliveryType
from app.domain.money import Money


class OrderStatus(StrEnum):
    NEW = "new"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Общие переходы. Зависящие от типа получения (самовывоз/доставка) уточняет
# Order.allowed_next_statuses().
_TRANSITIONS: Final[Mapping[OrderStatus, frozenset[OrderStatus]]] = {
    OrderStatus.NEW: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.IN_PRODUCTION, OrderStatus.CANCELLED}),
    OrderStatus.IN_PRODUCTION: frozenset({OrderStatus.READY, OrderStatus.CANCELLED}),
    OrderStatus.READY: frozenset(
        {OrderStatus.OUT_FOR_DELIVERY, OrderStatus.COMPLETED, OrderStatus.CANCELLED}
    ),
    OrderStatus.OUT_FOR_DELIVERY: frozenset({OrderStatus.COMPLETED, OrderStatus.CANCELLED}),
    OrderStatus.COMPLETED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class OrderItem:
    id: int
    order_id: int
    variant_id: int
    quantity: int
    price_at_order: Money
    product_name: str  # снимок названия на момент заказа
    variant_label: str | None  # снимок размера: "1 кг"
    comment: str | None  # надпись на торте, пожелания

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity должен быть > 0")
        if self.price_at_order < 0:
            raise ValueError("price_at_order не может быть отрицательной")

    @property
    def line_total(self) -> Money:
        return self.price_at_order * self.quantity


@dataclass(frozen=True, slots=True)
class Order:
    id: int
    public_id: UUID
    customer_id: int
    status: OrderStatus
    delivery_type: DeliveryType
    total_amount: Money
    currency: str  # ISO 4217, например "KGS", "EUR"
    desired_at: datetime
    comment: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not (len(self.currency) == 3 and self.currency.isascii() and self.currency.isupper()):
            raise ValueError(f"currency должен быть кодом ISO 4217: {self.currency!r}")

    def allowed_next_statuses(self) -> frozenset[OrderStatus]:
        """В какие статусы заказ можно перевести прямо сейчас."""
        allowed = _TRANSITIONS[self.status]
        if self.status is OrderStatus.READY:
            # самовывоз: готов -> выдан; доставка: готов -> передан курьеру
            skipped = (
                OrderStatus.OUT_FOR_DELIVERY
                if self.delivery_type is DeliveryType.PICKUP
                else OrderStatus.COMPLETED
            )
            allowed = allowed - {skipped}
        return allowed

    def can_transition_to(self, new_status: OrderStatus) -> bool:
        return new_status in self.allowed_next_statuses()

    @staticmethod
    def calculate_total(items: Iterable[OrderItem], delivery_cost: Money = Decimal(0)) -> Money:
        """Итог заказа: сумма позиций + доставка. Единое место расчёта total_amount."""
        return sum((item.line_total for item in items), start=Decimal(0)) + delivery_cost


@dataclass(frozen=True, slots=True)
class OrderStatusHistory:
    id: int
    order_id: int
    status: OrderStatus
    changed_by: int | None  # staff_user.id; None - система или клиент
    comment: str | None
    changed_at: datetime
