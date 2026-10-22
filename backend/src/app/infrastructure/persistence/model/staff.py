from datetime import datetime

from sqlalchemy import Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.staff import StaffRole
from app.infrastructure.database.base import Base, BigIntPk, CreatedAt, IsActive
from app.infrastructure.database.types import email_check, str_enum


class StaffUserModel(Base):
    __tablename__ = "staff_user"

    __table_args__ = (
        email_check(),
        Index("uq_staff_user_email_lower", func.lower(text("email")), unique=True),
    )

    id: Mapped[BigIntPk]
    email: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[StaffRole] = mapped_column(
        str_enum(StaffRole, "role"), server_default=StaffRole.ADMIN.value
    )
    is_active: Mapped[IsActive]
    created_at: Mapped[CreatedAt]
    last_login_at: Mapped[datetime | None]
