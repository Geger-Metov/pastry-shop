from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Delivery:
    id: int
    order_id: int
    address: str
    recipient: str
    phone: str
    delivery_at: datetime
    cost: float
    comment: str


@dataclass(frozen=True, slots=True)
class DeliveryType:
    id: int
    code: str
