from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Lead:
    id: int
    lead_status_id: int
    customer_id: int
    converted_order_id: int
    name: str
    phone: str
    email: str
    comment: str
    # поля индивидуального заказа
    decor: str
    design_description: str
    reference_url: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class LeadStatus:
    id: int
    code: str
