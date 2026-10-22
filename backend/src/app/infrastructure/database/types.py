"""Общие типы колонок и CHECK-ограничения для моделей."""

from enum import StrEnum

from sqlalchemy import CheckConstraint, Enum

E164_REGEX = r"^\+[1-9][0-9]{7,14}$"
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+$"


def str_enum[E: StrEnum](enum_cls: type[E], name: str, length: int = 20) -> Enum:
    """Колонка varchar + CHECK, значения берутся из StrEnum домена.

    По умолчанию SQLAlchemy сохраняет ИМЕНА членов enum ("NEW"), а не значения ("new"),
    поэтому values_callable обязателен. create_constraint=True создаёт CHECK, name -
    суффикс его имени (ck_<таблица>_<name>).
    """
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        length=length,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )


def phone_check(column: str = "phone") -> CheckConstraint:
    return CheckConstraint(f"{column} ~ '{E164_REGEX}'", name="phone_format")


def email_check(column: str = "email") -> CheckConstraint:
    return CheckConstraint(f"{column} ~ '{EMAIL_REGEX}'", name="email_format")
