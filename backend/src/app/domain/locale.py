from typing import Final, Literal

Locale = Literal["ru", "ky"]

SUPPORTED_LOCALES: Final[tuple[Locale, ...]] = ("ru", "ky")
DEFAULT_LOCALE: Final[Locale] = "ru"
