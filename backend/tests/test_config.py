import pytest

from app.core.config import DatabaseSettings, Settings

DATABASE_URL = "postgresql+asyncpg://user:pass@db:5432/shop"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DATABASE_URL", "SHOP_CURRENCY", "PHONE_DEFAULT_COUNTRY_CODE", "SMTP_USER"):
        monkeypatch.delenv(name, raising=False)


def test_database_settings_need_only_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    # так видит окружение контейнер migrate: валюты там нет
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    settings = DatabaseSettings(_env_file=None)  # type: ignore[call-arg]

    assert settings.database_url == DATABASE_URL


def test_full_settings_still_require_shop_currency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)

    with pytest.raises(ValueError, match="shop_currency"):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_empty_variables_are_treated_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    # compose передаёт пустые строки для необязательных переменных: `FOO: ${FOO:-}`
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("SHOP_CURRENCY", "RUB")
    monkeypatch.setenv("PHONE_DEFAULT_COUNTRY_CODE", "")
    monkeypatch.setenv("SMTP_USER", "")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.phone_default_country_code is None
    assert settings.smtp_user is None
