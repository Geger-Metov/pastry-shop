"""Общие типы колонок и CHECK-ограничения для моделей."""

from enum import StrEnum

from sqlalchemy import CheckConstraint, Enum

from app.domain.email import EMAIL_REGEX
from app.domain.phone import E164_REGEX


def str_enum[E: StrEnum](enum_cls: type[E], length: int = 20) -> Enum:
    """Колонка varchar, значения берутся из StrEnum домена. БЕЗ собственного CHECK.

    По умолчанию SQLAlchemy сохраняет ИМЕНА членов enum ("NEW"), а не значения ("new"),
    поэтому values_callable обязателен.

    CHECK здесь намеренно не создаётся (create_constraint=False): Alembic autogenerate
    рендерит CHECK, привязанный к типу, дважды, и миграция падает с "constraint already
    exists". Вместо этого CHECK объявляется явно в __table_args__ через enum_check().
    """
    return Enum(
        enum_cls,
        native_enum=False,
        length=length,
        create_constraint=False,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )


def enum_check[E: StrEnum](column: str, enum_cls: type[E]) -> CheckConstraint:
    """CHECK (<column> IN ('a', 'b', ...)) со значениями из StrEnum домена."""
    values = ", ".join(f"'{member.value}'" for member in enum_cls)
    return CheckConstraint(f"{column} IN ({values})", name=column)


def phone_check(column: str = "phone") -> CheckConstraint:
    return CheckConstraint(f"{column} ~ '{E164_REGEX}'", name="phone_format")


def email_check(column: str = "email") -> CheckConstraint:
    return CheckConstraint(f"{column} ~ '{EMAIL_REGEX}'", name="email_format")
