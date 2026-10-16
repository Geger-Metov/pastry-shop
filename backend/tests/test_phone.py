import pytest

from app.domain.phone import is_valid_phone, normalize_phone


@pytest.mark.parametrize(
    "raw",
    ["+996555123456", "+996 555 12-34-56", "0555 123 456", "555123456", "996555123456"],
)
def test_normalize_kyrgyz_formats(raw: str) -> None:
    assert normalize_phone(raw) == "+996555123456"


def test_normalize_keeps_foreign_e164() -> None:
    assert normalize_phone("+7 (701) 123-45-67") == "+77011234567"


@pytest.mark.parametrize("raw", ["", "abc", "123", "+0123456789"])
def test_normalize_rejects_garbage(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_phone(raw)


def test_is_valid_phone() -> None:
    assert is_valid_phone("+996555123456")
    assert not is_valid_phone("0555123456")
