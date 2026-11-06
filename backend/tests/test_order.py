from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from itertools import pairwise
from uuid import uuid4

import pytest

from app.domain.delivery import DeliveryType
from app.domain.order import Order, OrderItem, OrderStatus

NOW = datetime(2026, 10, 16, 12, 0, tzinfo=UTC)


def make_order(status: OrderStatus, delivery_type: DeliveryType) -> Order:
    return Order(
        id=1,
        public_id=uuid4(),
        customer_id=1,
        status=status,
        delivery_type=delivery_type,
        total_amount=Decimal("0"),
        currency="KGS",
        desired_at=NOW,
        comment=None,
        created_at=NOW,
        updated_at=NOW,
    )


def make_item(quantity: int, price: str) -> OrderItem:
    return OrderItem(
        id=1,
        order_id=1,
        variant_id=1,
        quantity=quantity,
        price_at_order=Decimal(price),
        product_name="Наполеон",
        variant_label="1 кг",
        comment=None,
    )


def test_line_total_and_order_total() -> None:
    items = [make_item(2, "1500.00"), make_item(1, "250.50")]
    assert items[0].line_total == Decimal("3000.00")
    assert Order.calculate_total(items, Decimal("200")) == Decimal("3450.50")


def test_total_of_empty_order_is_delivery_only() -> None:
    assert Order.calculate_total([], Decimal("100")) == Decimal("100")


def test_money_has_no_float_error() -> None:
    items = [make_item(3, "0.10")]
    assert Order.calculate_total(items) == Decimal("0.30")


@pytest.mark.parametrize("quantity", [0, -1])
def test_item_rejects_bad_quantity(quantity: int) -> None:
    with pytest.raises(ValueError):
        make_item(quantity, "100")


@pytest.mark.parametrize("currency", ["", "kgs", "KG", "EURO"])
def test_order_rejects_bad_currency(currency: str) -> None:
    with pytest.raises(ValueError):
        replace(make_order(OrderStatus.NEW, DeliveryType.PICKUP), currency=currency)


def test_happy_path_pickup() -> None:
    chain = [
        OrderStatus.NEW,
        OrderStatus.CONFIRMED,
        OrderStatus.IN_PRODUCTION,
        OrderStatus.READY,
        OrderStatus.COMPLETED,
    ]
    for current, nxt in pairwise(chain):
        assert make_order(current, DeliveryType.PICKUP).can_transition_to(nxt)


def test_pickup_cannot_go_out_for_delivery() -> None:
    order = make_order(OrderStatus.READY, DeliveryType.PICKUP)
    assert not order.can_transition_to(OrderStatus.OUT_FOR_DELIVERY)


def test_delivery_must_go_through_courier() -> None:
    order = make_order(OrderStatus.READY, DeliveryType.DELIVERY)
    assert order.can_transition_to(OrderStatus.OUT_FOR_DELIVERY)
    assert not order.can_transition_to(OrderStatus.COMPLETED)


@pytest.mark.parametrize("final", [OrderStatus.COMPLETED, OrderStatus.CANCELLED])
def test_final_statuses_are_terminal(final: OrderStatus) -> None:
    assert make_order(final, DeliveryType.PICKUP).allowed_next_statuses() == frozenset()


def test_cannot_skip_production() -> None:
    assert not make_order(OrderStatus.NEW, DeliveryType.PICKUP).can_transition_to(OrderStatus.READY)
