import re
from typing import Final

_E164: Final = re.compile(r"^\+[1-9][0-9]{7,14}$")


def is_valid_phone(value: str) -> bool:
    """Телефон в формате E.164, как требует CHECK в БД: +996555123456."""
    return _E164.fullmatch(value) is not None


def normalize_phone(raw: str, default_country_code: str | None = None) -> str:
    """Приводит ввод пользователя к E.164.

    Номер с "+" считается международным и берётся как есть. Для национального ввода
    нужен default_country_code (цифры без "+", например "996" или "33"; значение берётся
    из настроек магазина): ведущий 0 отбрасывается, код страны добавляется.
    Бросает ValueError, если распознать номер не удалось.
    """
    digits = re.sub(r"\D", "", raw)
    if raw.strip().startswith("+"):
        candidate = f"+{digits}"
    elif default_country_code is None:
        raise ValueError(f"Номер без кода страны, укажите его с '+': {raw!r}")
    elif digits.startswith(default_country_code) and len(digits) > len(default_country_code) + 7:
        candidate = f"+{digits}"  # "996555123456" - код страны уже есть
    else:
        candidate = f"+{default_country_code}{digits.removeprefix('0')}"

    if not is_valid_phone(candidate):
        raise ValueError(f"Некорректный номер телефона: {raw!r}")
    return candidate
