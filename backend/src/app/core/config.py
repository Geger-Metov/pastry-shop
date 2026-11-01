from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Только подключение к БД. Нужны Alembic и контейнеру migrate: им магазин не важен."""

    # env_ignore_empty: пустая переменная (FOO=) считается незаданной, а не пустой строкой
    model_config = SettingsConfigDict(env_file=".env.local", env_ignore_empty=True, extra="ignore")

    # postgresql+asyncpg://user:password@localhost:5432/dbname
    database_url: str


class Settings(DatabaseSettings):
    """Настройки приложения. Значения берутся из переменных окружения."""

    # Валюта магазина (ISO 4217) и код страны для национальных номеров телефона.
    # Никуда не вшиты: смена языка интерфейса на них не влияет.
    shop_currency: str
    phone_default_country_code: str | None = None
    cors_origins: list[str] = []

    # Уведомления о заявках в Telegram. Если не заданы — заявка только сохраняется в БД
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Уведомления о заявках на почту (SMTP). Включаются, когда заданы smtp_user и smtp_password.
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    # От кого и кому. Если не заданы, письмо уходит с адреса smtp_user на него же.
    mail_from: str | None = None
    # Несколько получателей через запятую
    mail_to: str | None = None


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()  # type: ignore[call-arg]


@lru_cache
def get_settings() -> Settings:
    # database_url and shop_currency are loaded from the environment / .env.local
    # at runtime; mypy only sees them as required __init__ arguments.
    return Settings()  # type: ignore[call-arg]
