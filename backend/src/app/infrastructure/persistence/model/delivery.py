from sqlalchemy import CheckConstraint, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Amount, Base, BigInt, BigIntPk
from app.infrastructure.database.types import phone_check


class DeliveryModel(Base):
    """Данные доставки: строка есть только у заказов с delivery_type = 'delivery'."""

    __tablename__ = "delivery"

    __table_args__ = (
        phone_check(),
        CheckConstraint("cost >= 0", name="cost_non_negative"),
    )

    id: Mapped[BigIntPk]
    order_id: Mapped[BigInt] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), unique=True
    )
    address: Mapped[str] = mapped_column(Text)
    recipient: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(16))
    cost: Mapped[Amount] = mapped_column(server_default=text("0"))
    comment: Mapped[str | None] = mapped_column(Text)  # подъезд, этаж, домофон
