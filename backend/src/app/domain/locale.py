from typing import Final, Literal

Locale = Literal["ru", "en", "fr"]

SUPPORTED_LOCALES: Final[tuple[Locale, ...]] = ("ru", "en", "fr")
DEFAULT_LOCALE: Final[Locale] = "ru"
