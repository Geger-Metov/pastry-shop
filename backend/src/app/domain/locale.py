from typing import Final, Literal

Locale = Literal["ru", "en", "fr"]

SUPPORTED_LOCALES: Final[tuple[Locale, ...]] = ("ru", "en", "fr")
DEFAULT_LOCALE: Final[Locale] = "ru"


def parse_locale(value: str) -> Locale:
    """Строка из БД или запроса -> Locale. ValueError, если язык не поддерживается."""

    for locale in SUPPORTED_LOCALES:
        if locale == value:
            return locale
    raise ValueError(f"Unsupported locale: {value!r}")
