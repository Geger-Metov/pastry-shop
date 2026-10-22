from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, Identity, MetaData, Numeric, func, text
from sqlalchemy.orm import DeclarativeBase, mapped_column

# Имена ограничений и индексов генерируются по шаблонам: миграции получаются
# детерминированными. column_0_N - это ВСЕ колонки ограничения (важно для составных).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# --- Повторяющиеся типы колонок -------------------------------------------------
# Nullable определяется аннотацией: Mapped[X] -> NOT NULL, Mapped[X | None] -> NULL.

# первичный ключ: bigint GENERATED ALWAYS AS IDENTITY
BigIntPk = Annotated[int, mapped_column(BigInteger, Identity(always=True), primary_key=True)]
# внешние ключи на BigIntPk должны быть bigint, а не integer
BigInt = Annotated[int, mapped_column(BigInteger)]

# деньги: numeric(10, 2); тип в Python - Decimal
Amount = Annotated[Decimal, mapped_column(Numeric(10, 2))]

CreatedAt = Annotated[datetime, mapped_column(server_default=func.now())]
UpdatedAt = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]

SortOrder = Annotated[int, mapped_column(server_default=text("0"))]
IsActive = Annotated[bool, mapped_column(server_default=text("true"))]


class Base(DeclarativeBase):
    """Общий declarative base для всех SQLAlchemy-моделей проекта."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # любой Mapped[datetime] - это timestamptz (в схеме везде timestamptz)
    type_annotation_map = {datetime: DateTime(timezone=True)}

    # после INSERT/UPDATE значения, которые выставила БД (created_at, updated_at),
    # возвращаются через RETURNING, а не лениво - иначе в async будет MissingGreenlet
    __mapper_args__ = {"eager_defaults": True}
