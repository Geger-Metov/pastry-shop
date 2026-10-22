from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.lead import LeadStatus
from app.infrastructure.database.base import Amount, Base, BigInt, BigIntPk, CreatedAt, UpdatedAt
from app.infrastructure.database.types import email_check, enum_check, phone_check, str_enum


class LeadModel(Base):
    """Заявка на индивидуальный заказ. После согласования превращается в заказ."""

    __tablename__ = "lead"

    __table_args__ = (
        enum_check("status", LeadStatus),
        phone_check(),
        email_check(),
        CheckConstraint("servings > 0", name="servings_positive"),
        CheckConstraint("budget >= 0", name="budget_non_negative"),
        Index("ix_lead_status_created_at", "status", "created_at"),
    )

    id: Mapped[BigIntPk]
    status: Mapped[LeadStatus] = mapped_column(
        str_enum(LeadStatus), server_default=LeadStatus.NEW.value
    )
    customer_id: Mapped[BigInt | None] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), index=True
    )
    converted_order_id: Mapped[BigInt | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(16), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(Text)
    # поля индивидуального заказа
    desired_date: Mapped[date | None] = mapped_column(Date)
    servings: Mapped[int | None]
    budget: Mapped[Amount | None]
    decor: Mapped[str | None] = mapped_column(String(200))
    design_description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]


class LeadAttachmentModel(Base):
    """Референсы-картинки, которые клиент прикрепил к заявке."""

    __tablename__ = "lead_attachment"

    id: Mapped[BigIntPk]
    lead_id: Mapped[BigInt] = mapped_column(ForeignKey("lead.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(Text)
    original_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[CreatedAt]
