"""Проверки ORM-метаданных без подключения к БД: ловят классические ошибки в моделях."""

from enum import StrEnum

import pytest
from sqlalchemy import BigInteger, DateTime, Enum, Table

import app.infrastructure.persistence.model  # noqa: F401  (регистрирует модели)
from app.infrastructure.database.base import Base

TABLES = sorted(Base.metadata.tables.values(), key=lambda t: t.name)


def test_all_tables_registered() -> None:
    assert len(TABLES) == 21


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_table_has_primary_key(table: Table) -> None:
    assert table.primary_key.columns


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_foreign_key_type_matches_referenced_column(table: Table) -> None:
    """integer-внешний ключ на bigint-первичный - типичная ошибка Mapped[int]."""
    for fk in table.foreign_keys:
        assert type(fk.parent.type) is type(fk.column.type), f"{table.name}.{fk.parent.name}"
        if isinstance(fk.column.type, BigInteger):
            assert isinstance(fk.parent.type, BigInteger)


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_datetime_columns_are_timestamptz(table: Table) -> None:
    for column in table.columns:
        if isinstance(column.type, DateTime):
            assert column.type.timezone, f"{table.name}.{column.name}"


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_column_names_are_snake_case(table: Table) -> None:
    for column in table.columns:
        assert column.name == column.name.lower(), f"{table.name}.{column.name}"


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_enum_columns_store_values_not_names(table: Table) -> None:
    """По умолчанию SQLAlchemy пишет в БД имена членов enum (NEW), а CHECK ждёт значения (new)."""
    for column in table.columns:
        if not isinstance(column.type, Enum):
            continue
        enum_cls = column.type.enum_class
        assert enum_cls is not None and issubclass(enum_cls, StrEnum)
        assert column.type.enums == [member.value for member in enum_cls], (
            f"{table.name}.{column.name}"
        )
