from sqlalchemy.orm import Mapped

from app.infrastructure.database.base import Base, BigIntPk


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[BigIntPk]
