import re
from typing import Final

# Строка (а не только compiled) нужна и CHECK-ограничению в БД: оба места используют одно правило.
EMAIL_REGEX: Final = r"^[^@\s]+@[^@\s]+$"
_EMAIL: Final = re.compile(EMAIL_REGEX)


def is_valid_email(value: str) -> bool:
    """Грубая проверка формата "что-то@что-то": настоящая проверка - письмо на этот адрес."""
    return _EMAIL.fullmatch(value) is not None
