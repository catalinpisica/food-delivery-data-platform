from datetime import timedelta

from delivery_simulator.generate_orders import (
    BASE_ORDER_TIME,
    DELIVERY_FEE_CENTS,
    DELIVERY_STATUS_ASSIGNED,
    DELIVERY_STATUS_DELIVERED,
    DELIVERY_STATUS_PICKED_UP,
    MAX_ITEMS_PER_ORDER,
    MIN_ITEMS_PER_ORDER,
    ORDER_STATUS_ACCEPTED,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_COURIER_ASSIGNED,
    ORDER_STATUS_CREATED,
    ORDER_STATUS_DELIVERED,
    ORDER_STATUS_PICKED_UP,
    choose_delivery_status,
    choose_order_status,
    generate_orders,
)
from delivery_simulator.models import Courier, Customer, MenuItem, Restaurant


def make_customers() -> list[Customer]:
    return [
        Customer(customer_id=1, zone_id=1, signup_channel="organic", is_active=True),
        Customer(customer_id=2, zone_id=2, signup_channel="referral", is_active=True),
    ]


def make_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            restaurant_id=1,
            restaurant_name="Restaurant 1",
            zone_id=1,
            cuisine_type="pizza",
            price_category="$",
            is_active=True,
        ),
        Restaurant(
            restaurant_id=2,
            restaurant_name="Restaurant 2",
            zone_id=2,
            cuisine_type="sushi",
            price_category="$$",
            is_active=True,
        ),
    ]


def make_menu_items() -> list[MenuItem]:
    return [
        MenuItem(
            menu_item_id=1,
            restaurant_id=1,
            item_name="Pizza",
            category="main",
            price_cents=1000,
            is_available=True,
        ),
        MenuItem(
            menu_item_id=2,
            restaurant_id=1,
            item_name="Salad",
            category="side",
            price_cents=500,
            is_available=True,
        ),
        MenuItem(
            menu_item_id=3,
            restaurant_id=2,
            item_name="Sushi",
            category="main",
            price_cents=1200,
            is_available=True,
        ),
        MenuItem(
            menu_item_id=4,
            restaurant_id=2,
            item_name="Soup",
            category="side",
            price_cents=400,
            is_available=True,
        ),
    ]


def make_couriers() -> list[Courier]:
    return [
        Courier(courier_id=1, home_zone_id=1, vehicle_type="bike", status="available"),
        Courier(courier_id=2, home_zone_id=2, vehicle_type="car", status="available"),
    ]


def test_choose_order_status() -> None:
    assert choose_order_status(20) == ORDER_STATUS_CREATED
    assert choose_order_status(1) == ORDER_STATUS_ACCEPTED
    assert choose_order_status(2) == ORDER_STATUS_COURIER_ASSIGNED
    assert choose_order_status(3) == ORDER_STATUS_PICKED_UP
    assert choose_order_status(4) == ORDER_STATUS_CANCELLED
    assert choose_order_status(5) == ORDER_STATUS_DELIVERED


def test_choose_delivery_status() -> None:
    assert choose_delivery_status(ORDER_STATUS_CREATED) is None
    assert choose_delivery_status(ORDER_STATUS_ACCEPTED) is None
    assert choose_delivery_status(ORDER_STATUS_CANCELLED) is None
    assert choose_delivery_status(ORDER_STATUS_COURIER_ASSIGNED) == DELIVERY_STATUS_ASSIGNED
    assert choose_delivery_status(ORDER_STATUS_PICKED_UP) == DELIVERY_STATUS_PICKED_UP
    assert choose_delivery_status(ORDER_STATUS_DELIVERED) == DELIVERY_STATUS_DELIVERED


def test_generate_orders_creates_expected_counts() -> None:
    orders, order_items, deliveries = generate_orders(
        customers=make_customers(),
        restaurants=make_restaurants(),
        menu_items=make_menu_items(),
        couriers=make_couriers(),
        order_count=20,
    )

    assert len(orders) == 20
    assert len(order_items) >= 20 * MIN_ITEMS_PER_ORDER
    assert len(order_items) <= 20 * MAX_ITEMS_PER_ORDER    
    assert len(deliveries) == 17


def test_orders_without_delivery_do_not_have_couriers() -> None:
    orders, _order_items, _deliveries = generate_orders(
        customers=make_customers(),
        restaurants=make_restaurants(),
        menu_items=make_menu_items(),
        couriers=make_couriers(),
        order_count=20,
    )

    for order in orders:
        if order.status in (
            ORDER_STATUS_CREATED,
            ORDER_STATUS_ACCEPTED,
            ORDER_STATUS_CANCELLED,
        ):
            assert order.courier_id is None
        else:
            assert order.courier_id is not None


def test_order_totals_match_order_items() -> None:
    orders, order_items, _deliveries = generate_orders(
        customers=make_customers(),
        restaurants=make_restaurants(),
        menu_items=make_menu_items(),
        couriers=make_couriers(),
        order_count=2,
    )

    for order in orders:
        subtotal_cents = 0

        for order_item in order_items:
            if order_item.order_id == order.order_id:
                subtotal_cents = subtotal_cents + order_item.total_price_cents

        assert order.subtotal_cents == subtotal_cents
        assert order.total_amount_cents == subtotal_cents + DELIVERY_FEE_CENTS


def test_order_timestamps_follow_status() -> None:
    orders, _order_items, _deliveries = generate_orders(
        customers=make_customers(),
        restaurants=make_restaurants(),
        menu_items=make_menu_items(),
        couriers=make_couriers(),
        order_count=5,
    )

    assert orders[0].created_at == BASE_ORDER_TIME
    assert orders[0].updated_at == BASE_ORDER_TIME + timedelta(minutes=2)
    assert orders[1].updated_at == orders[1].created_at + timedelta(minutes=5)
    assert orders[2].updated_at == orders[2].created_at + timedelta(minutes=20)
    assert orders[3].updated_at == orders[3].created_at + timedelta(minutes=3)
    assert orders[4].updated_at == orders[4].created_at + timedelta(minutes=40)


def test_delivery_timestamps_follow_status() -> None:
    _orders, _order_items, deliveries = generate_orders(
        customers=make_customers(),
        restaurants=make_restaurants(),
        menu_items=make_menu_items(),
        couriers=make_couriers(),
        order_count=5,
    )

    assigned_delivery = deliveries[0]
    picked_up_delivery = deliveries[1]
    delivered_delivery = deliveries[2]

    assert assigned_delivery.status == DELIVERY_STATUS_ASSIGNED
    assert assigned_delivery.assigned_at is not None
    assert assigned_delivery.picked_up_at is None
    assert assigned_delivery.delivered_at is None
    assert assigned_delivery.updated_at == assigned_delivery.assigned_at

    assert picked_up_delivery.status == DELIVERY_STATUS_PICKED_UP
    assert picked_up_delivery.assigned_at is not None
    assert picked_up_delivery.picked_up_at is not None
    assert picked_up_delivery.delivered_at is None
    assert picked_up_delivery.assigned_at < picked_up_delivery.picked_up_at
    assert picked_up_delivery.updated_at == picked_up_delivery.picked_up_at

    assert delivered_delivery.status == DELIVERY_STATUS_DELIVERED
    assert delivered_delivery.assigned_at is not None
    assert delivered_delivery.picked_up_at is not None
    assert delivered_delivery.delivered_at is not None
    assert delivered_delivery.assigned_at < delivered_delivery.picked_up_at
    assert delivered_delivery.picked_up_at < delivered_delivery.delivered_at
    assert delivered_delivery.updated_at == delivered_delivery.delivered_at

def test_order_items_have_variable_quantities() -> None:
    _orders, order_items, _deliveries = generate_orders(
        customers=make_customers(),
        restaurants=make_restaurants(),
        menu_items=make_menu_items(),
        couriers=make_couriers(),
        order_count=20,
    )

    quantities = []

    for order_item in order_items:
        quantities.append(order_item.quantity)

    assert 1 in quantities
    assert 2 in quantities
    assert 3 in quantities