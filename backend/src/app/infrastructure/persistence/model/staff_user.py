from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.staff import StaffRole
from app.infrastructure.database.base import Base, BigIntPk, CreatedAt, IsActive


class StaffUserModel(Base):
    __tablename__ = "staff_user"

    __table_args__ = (
        CheckConstraint(
            r"email ~ '^[^@\s]+@[^@\s]+$'",
            name="email_format",
        ),
        Index("uq_staff_user_email_lower", func.lower(text("email")), unique=True),
    )

    id: Mapped[BigIntPk]
    email: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[StaffRole] = mapped_column(
        Enum(
            StaffRole,
            native_enum=False,
            lenght=20,
            name="staff_role",
            create_constraint=True,
        )
    )
    is_active: Mapped[IsActive]
    created_at: Mapped[CreatedAt]
    last_login_at: Mapped[datetime]
