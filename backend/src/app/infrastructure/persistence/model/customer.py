from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.customer import ContactMethod
from app.domain.locale import DEFAULT_LOCALE
from app.infrastructure.database.base import Base, BigIntPk, CreatedAt, IsActive, UpdatedAt
from app.infrastructure.database.types import email_check, enum_check, phone_check, str_enum


class CustomerModel(Base):
    __tablename__ = "customer"

    __table_args__ = (
        enum_check("preferred_contact", ContactMethod),
        phone_check(),
        email_check(),
        # уникальный email без учёта регистра; NULL-ы друг другу не мешают
        Index("uq_customer_email_lower", func.lower(text("email")), unique=True),
    )

    id: Mapped[BigIntPk]
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(16), unique=True)
    email: Mapped[str | None] = mapped_column(String(255))
    preferred_contact: Mapped[ContactMethod | None] = mapped_column(str_enum(ContactMethod))
    locale: Mapped[str] = mapped_column(
        String(5), ForeignKey("locale.code"), server_default=DEFAULT_LOCALE
    )
    birthday: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[IsActive]
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
