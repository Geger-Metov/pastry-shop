import re
from typing import Final

_E164: Final = re.compile(r"^\+[1-9][0-9]{7,14}$")


def is_valid_phone(value: str) -> bool:
    """Телефон в формате E.164, как требует CHECK в БД: +996555123456."""
    return _E164.fullmatch(value) is not None


# Национальный "магистральный" префикс, который набирают перед номером внутри страны.
# По умолчанию "0" (Кыргызстан, Франция...). Россия и Казахстан (код 7) - "8".
_TRUNK_PREFIXES: Final = {"7": "8"}

# Длина национальной части номера (без кода страны и магистрального префикса) для известных
# стран. Нужна, чтобы отличить "7771234567" (казахстанский номер без кода) от "7" + номер.
_NATIONAL_LENGTH: Final = {"7": 10, "996": 9, "33": 9}


def _has_country_code(digits: str, country_code: str) -> bool:
    if not digits.startswith(country_code):
        return False
    national = _NATIONAL_LENGTH.get(country_code)
    if national is not None:
        return len(digits) == len(country_code) + national
    return len(digits) > len(country_code) + 7  # неизвестная страна: грубая оценка


def normalize_phone(raw: str, default_country_code: str | None = None) -> str:
    """Приводит ввод пользователя к E.164.

    Номер с "+" или с "00" считается международным и берётся как есть. Для национального
    ввода нужен default_country_code (цифры без "+", например "996" или "33"; значение
    берётся из настроек магазина): магистральный префикс ("0", для кода 7 - "8") отбрасывается,
    код страны добавляется. Бросает ValueError, если распознать номер не удалось.

    Это эвристика без таблицы длин номеров по странам. Для разных стран сразу и для
    проверки существования номера используйте библиотеку `phonenumbers`.
    """
    stripped = raw.strip()
    digits = re.sub(r"\D", "", raw)
    if stripped.startswith("+"):
        candidate = f"+{digits}"
    elif stripped.startswith("00"):
        candidate = f"+{digits.removeprefix('00')}"
    elif default_country_code is None:
        raise ValueError(f"Номер без кода страны, укажите его с '+': {raw!r}")
    else:
        trunk = _TRUNK_PREFIXES.get(default_country_code, "0")
        if digits.startswith(trunk):
            candidate = f"+{default_country_code}{digits.removeprefix(trunk)}"
        elif _has_country_code(digits, default_country_code):
            candidate = f"+{digits}"  # "996555123456" - код страны уже есть
        else:
            candidate = f"+{default_country_code}{digits}"

    if not is_valid_phone(candidate):
        raise ValueError(f"Некорректный номер телефона: {raw!r}")
    return candidate
