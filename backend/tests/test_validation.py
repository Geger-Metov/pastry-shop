from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.customer import Customer
from app.domain.payment import Payment, PaymentMethod, PaymentStatus
from app.domain.product import ProductVariant
from app.domain.review import Review

NOW = datetime(2026, 10, 16, 12, 0, tzinfo=UTC)


def test_customer_requires_e164_phone() -> None:
    with pytest.raises(ValueError):
        Customer(1, "Дана", "0555123456", None, None, "ru", None, None, True, NOW, NOW)


def test_variant_rejects_negative_price() -> None:
    with pytest.raises(ValueError):
        ProductVariant(1, 1, 1000, None, Decimal("-1"), 0, True)


def test_paid_payment_needs_paid_at() -> None:
    with pytest.raises(ValueError):
        Payment(1, 1, Decimal("100"), PaymentMethod.CASH, PaymentStatus.PAID, None, None, NOW)


@pytest.mark.parametrize("rating", [0, 6])
def test_review_rating_range(rating: int) -> None:
    with pytest.raises(ValueError):
        Review(1, None, None, None, "Аня", rating, "ок", False, NOW)
