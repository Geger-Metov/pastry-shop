from datetime import date

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.customer import ContactMethod
from app.infrastructure.database.base import Base, BigIntPk, CreatedAt, IsActive, UpdatedAt


class CustomerModel(Base):
    __tablename__ = "customer"

    __table_args__ = (
        CheckConstraint(
            r"phone ~ '^\+[1-9][0-9]{7,14}$'",
            name="phone_format",
        ),
        CheckConstraint(
            r"email ~ '^[^@\s]+@[^@\s]+$'",
            name="email_format",
        ),
        Index("uq_customer_email_lower", func.lower(text("email")), unique=True),
    )

    id: Mapped[BigIntPk]
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(16), unique=True)
    email: Mapped[str | None] = mapped_column(String(255))
    preferred_contact: Mapped[ContactMethod | None] = mapped_column(
        Enum(
            ContactMethod,
            native_enum=False,
            length=20,
            name="preferred_contact",
            create_constraint=True,
        ),
    )
    locale: Mapped[str] = mapped_column(
        String(5), ForeignKey("locale.code"), default="ru", server_default="ru"
    )
    birthday: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[IsActive]
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
