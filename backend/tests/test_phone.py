import pytest

from app.domain.phone import is_valid_phone, normalize_phone


@pytest.mark.parametrize(
    "raw",
    ["+996555123456", "+996 555 12-34-56", "0555 123 456", "555123456", "996555123456"],
)
def test_normalize_with_default_country_code(raw: str) -> None:
    assert normalize_phone(raw, default_country_code="996") == "+996555123456"


def test_normalize_other_country() -> None:
    assert normalize_phone("06 12 34 56 78", default_country_code="33") == "+33612345678"


def test_international_format_ignores_default() -> None:
    assert normalize_phone("+7 (701) 123-45-67", default_country_code="996") == "+77011234567"


def test_national_number_without_country_code_is_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_phone("0555 123 456")


@pytest.mark.parametrize("raw", ["", "abc", "123", "+0123456789"])
def test_normalize_rejects_garbage(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_phone(raw, default_country_code="996")


def test_is_valid_phone() -> None:
    assert is_valid_phone("+996555123456")
    assert not is_valid_phone("0555123456")
