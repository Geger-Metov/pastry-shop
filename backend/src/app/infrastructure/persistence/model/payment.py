from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.payment import PaymentMethod, PaymentStatus
from app.infrastructure.database.base import Amount, Base, BigInt, BigIntPk, CreatedAt
from app.infrastructure.database.types import str_enum


class PaymentModel(Base):
    """Платежей у заказа может быть несколько (предоплата + остаток, возврат)."""

    __tablename__ = "payment"

    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("status <> 'paid' OR paid_at IS NOT NULL", name="paid_has_date"),
        # защита от двойной обработки одного и того же вебхука
        Index(
            "uq_payment_method_external_id",
            "method",
            "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    id: Mapped[BigIntPk]
    order_id: Mapped[BigInt] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"), index=True
    )
    amount: Mapped[Amount]
    method: Mapped[PaymentMethod] = mapped_column(str_enum(PaymentMethod, "method"))
    status: Mapped[PaymentStatus] = mapped_column(
        str_enum(PaymentStatus, "status"), server_default=PaymentStatus.PENDING.value
    )
    external_id: Mapped[str | None] = mapped_column(String(100))  # id у платёжного провайдера
    paid_at: Mapped[datetime | None]
    created_at: Mapped[CreatedAt]
