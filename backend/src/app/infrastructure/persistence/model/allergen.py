from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BigIntPk


class AllergenModel(Base):
    __tablename__ = "allergen"

    id: Mapped[BigIntPk]
    code: Mapped[str] = mapped_column(String(50), unique=True)
