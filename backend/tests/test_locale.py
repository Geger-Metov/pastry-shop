import pytest

from app.domain.locale import SUPPORTED_LOCALES, parse_locale


@pytest.mark.parametrize("value", SUPPORTED_LOCALES)
def test_parse_supported_locale(value: str) -> None:
    assert parse_locale(value) == value


@pytest.mark.parametrize("value", ["", "de", "RU", "ky"])
def test_parse_rejects_unsupported_locale(value: str) -> None:
    with pytest.raises(ValueError):
        parse_locale(value)
