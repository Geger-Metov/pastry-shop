from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class LocaleModel(Base):
    __tablename__ = "locale"

    code: Mapped[str] = mapped_column(String(5), primary_key=True)
