from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.delivery import DeliveryType
from app.domain.order import OrderStatus
from app.infrastructure.database.base import (
    Amount,
    Base,
    BigInt,
    BigIntPk,
    CreatedAt,
    UpdatedAt,
)
from app.infrastructure.database.types import enum_check, str_enum


class OrderModel(Base):
    __tablename__ = "orders"

    __table_args__ = (
        enum_check("status", OrderStatus),
        enum_check("delivery_type", DeliveryType),
        CheckConstraint("total_amount >= 0", name="total_amount_non_negative"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="currency_format"),
        # доска кондитера: заказы по статусу и сроку
        Index("ix_orders_status_desired_at", "status", "desired_at"),
    )

    id: Mapped[BigIntPk]
    # публичный идентификатор для ссылок "отследить заказ": id перебирать нельзя
    public_id: Mapped[UUID] = mapped_column(unique=True, server_default=func.gen_random_uuid())
    customer_id: Mapped[BigInt] = mapped_column(
        ForeignKey("customer.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        str_enum(OrderStatus), server_default=OrderStatus.NEW.value
    )
    delivery_type: Mapped[DeliveryType] = mapped_column(str_enum(DeliveryType))
    # снимок итога: сумма позиций + доставка (см. Order.calculate_total)
    total_amount: Mapped[Amount]
    currency: Mapped[str] = mapped_column(CHAR(3))  # ISO 4217, из настроек магазина
    desired_at: Mapped[datetime]
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]


class OrderItemModel(Base):
    __tablename__ = "order_item"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("price_at_order >= 0", name="price_at_order_non_negative"),
        UniqueConstraint("order_id", "variant_id"),
    )

    id: Mapped[BigIntPk]
    order_id: Mapped[BigInt] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    variant_id: Mapped[BigInt] = mapped_column(
        ForeignKey("product_variant.id", ondelete="RESTRICT"), index=True
    )
    quantity: Mapped[int]
    price_at_order: Mapped[Amount]
    # снимки названий: товар могут переименовать, а в старом заказе должно остаться как было
    product_name: Mapped[str] = mapped_column(String(150))
    variant_label: Mapped[str | None] = mapped_column(String(100))
    comment: Mapped[str | None] = mapped_column(Text)  # надпись на торте, пожелания


class OrderStatusHistoryModel(Base):
    __tablename__ = "order_status_history"

    __table_args__ = (
        enum_check("status", OrderStatus),
        Index("ix_order_status_history_order_id_changed_at", "order_id", "changed_at"),
    )

    id: Mapped[BigIntPk]
    order_id: Mapped[BigInt] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    status: Mapped[OrderStatus] = mapped_column(str_enum(OrderStatus))
    # None - система или клиент
    changed_by: Mapped[BigInt | None] = mapped_column(
        ForeignKey("staff_user.id", ondelete="SET NULL")
    )
    comment: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[CreatedAt]
