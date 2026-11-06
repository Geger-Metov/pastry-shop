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


@pytest.mark.parametrize("raw", ["89161234567", "8 (916) 123-45-67", "9161234567", "79161234567"])
def test_normalize_russian_trunk_prefix(raw: str) -> None:
    # в России и Казахстане (код 7) внутри страны перед номером набирают 8, а не 0
    assert normalize_phone(raw, default_country_code="7") == "+79161234567"


def test_kazakh_national_number_starting_with_country_digit() -> None:
    # национальный номер сам начинается с 7: код страны добавляем, а не считаем его уже набранным
    assert normalize_phone("7771234567", default_country_code="7") == "+77771234567"


def test_double_zero_is_international_prefix() -> None:
    assert normalize_phone("00 996 555 123 456", default_country_code="7") == "+996555123456"


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
