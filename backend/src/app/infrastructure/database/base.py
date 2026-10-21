from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, Identity, MetaData, func, text
from sqlalchemy.orm import DeclarativeBase, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


BigIntPk = Annotated[int, mapped_column(BigInteger, Identity(always=True), primary_key=True)]
BigInt = Annotated[int, mapped_column(BigInteger)]  # для внешних ключей
CreatedAt = Annotated[datetime, mapped_column(server_default=func.now(), nullable=False)]
UpdatedAt = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)
]
SortOrder = Annotated[int, mapped_column(server_default=text("0"))]
IsActive = Annotated[bool, mapped_column(server_default=text("true"))]


class Base(DeclarativeBase):
    """Общий declarative base для всех SQLAlchemy-моделей проекта."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    type_annotation_map = {datetime: DateTime(timezone=True)}
