from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Orders:
    id: int
    customer_id: int
    status_id: int
    delivery_type_id: int
    amount: float
    comment: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class OrderStatus:
    id: int
    code: str


@dataclass(frozen=True, slots=True)
class OrderDetail:
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_order: float


@dataclass(frozen=True, slots=True)
class OrderStatusHistory:
    id: int
    order_id: int
    status_id: int
    changed_at: datetime
