from delivery_simulator.models import (
    Courier,
    Customer,
    Delivery,
    MenuItem,
    Order,
    OrderItem,
    Restaurant,
)
from delivery_simulator.db import connect
from datetime import datetime, timedelta, timezone

ORDER_STATUS_CREATED = "CREATED"
ORDER_STATUS_ACCEPTED = "ACCEPTED"
ORDER_STATUS_COURIER_ASSIGNED = "COURIER_ASSIGNED"
ORDER_STATUS_PICKED_UP = "PICKED_UP"
ORDER_STATUS_DELIVERED = "DELIVERED"
ORDER_STATUS_CANCELLED = "CANCELLED"

DELIVERY_STATUS_ASSIGNED = "ASSIGNED"
DELIVERY_STATUS_PICKED_UP = "PICKED_UP"
DELIVERY_STATUS_DELIVERED = "DELIVERED"
DELIVERY_STATUS_CANCELLED = "CANCELLED"

DELIVERY_FEE_CENTS = 299
ITEMS_PER_ORDER = 2

BASE_ORDER_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def choose_order_status(order_id: int) -> str:
    if order_id % 20 == 0:
        return ORDER_STATUS_CREATED

    if order_id % 20 == 1:
        return ORDER_STATUS_ACCEPTED

    if order_id % 20 == 2:
        return ORDER_STATUS_COURIER_ASSIGNED

    if order_id % 20 == 3:
        return ORDER_STATUS_PICKED_UP

    if order_id % 20 == 4:
        return ORDER_STATUS_CANCELLED

    return ORDER_STATUS_DELIVERED


def choose_delivery_status(order_status: str) -> str | None:
    if order_status == ORDER_STATUS_COURIER_ASSIGNED:
        return DELIVERY_STATUS_ASSIGNED

    if order_status == ORDER_STATUS_PICKED_UP:
        return DELIVERY_STATUS_PICKED_UP

    if order_status == ORDER_STATUS_DELIVERED:
        return DELIVERY_STATUS_DELIVERED

    return None


def order_has_assigned_courier(order_status: str) -> bool:
    return order_status in (
        ORDER_STATUS_COURIER_ASSIGNED,
        ORDER_STATUS_PICKED_UP,
        ORDER_STATUS_DELIVERED,
    )

def calculate_order_updated_at(order_status: str, created_at: datetime) -> datetime:
    if order_status == ORDER_STATUS_CREATED:
        return created_at

    if order_status == ORDER_STATUS_ACCEPTED:
        return created_at + timedelta(minutes=2)

    if order_status == ORDER_STATUS_COURIER_ASSIGNED:
        return created_at + timedelta(minutes=5)

    if order_status == ORDER_STATUS_PICKED_UP:
        return created_at + timedelta(minutes=20)

    if order_status == ORDER_STATUS_CANCELLED:
        return created_at + timedelta(minutes=3)

    return created_at + timedelta(minutes=40)

def calculate_delivery_timestamps(
    delivery_status: str,
    order_created_at: datetime,
) -> tuple[datetime, datetime | None, datetime | None, datetime]:
    assigned_at = order_created_at + timedelta(minutes=5)
    picked_up_at = None
    delivered_at = None

    if delivery_status in (
        DELIVERY_STATUS_PICKED_UP,
        DELIVERY_STATUS_DELIVERED,
    ):
        picked_up_at = order_created_at + timedelta(minutes=20)

    if delivery_status == DELIVERY_STATUS_DELIVERED:
        delivered_at = order_created_at + timedelta(minutes=40)

    updated_at = assigned_at

    if picked_up_at is not None:
        updated_at = picked_up_at

    if delivered_at is not None:
        updated_at = delivered_at

    return assigned_at, picked_up_at, delivered_at, updated_at

def generate_orders(
    customers: list[Customer],
    restaurants: list[Restaurant],
    menu_items: list[MenuItem],
    couriers: list[Courier],
    order_count: int,
) -> tuple[list[Order], list[OrderItem], list[Delivery]]:
    orders = []
    order_items = []
    deliveries = []
    customer_index = 0
    restaurant_index = 0
    courier_index = 0
    order_item_id = 1
    delivery_id = 1

    for order_id in range(1, order_count + 1):
        customer = customers[customer_index]
        restaurant = restaurants[restaurant_index]
        courier = couriers[courier_index]
        order_status = choose_order_status(order_id)
        order_created_at = BASE_ORDER_TIME + timedelta(minutes=order_id - 1)
        order_updated_at = calculate_order_updated_at(
            order_status=order_status,
            created_at=order_created_at,
        )
        assigned_courier_id = None

        if order_has_assigned_courier(order_status):
            assigned_courier_id = courier.courier_id

        restaurant_menu_items = []

        for menu_item in menu_items:
            if menu_item.restaurant_id == restaurant.restaurant_id:
                restaurant_menu_items.append(menu_item)

        selected_menu_items = restaurant_menu_items[:ITEMS_PER_ORDER]

        subtotal_cents = 0

        for menu_item in selected_menu_items:
            subtotal_cents = subtotal_cents + menu_item.price_cents

        total_amount_cents = subtotal_cents + DELIVERY_FEE_CENTS

        order = Order(
            order_id=order_id,
            customer_id=customer.customer_id,
            restaurant_id=restaurant.restaurant_id,
            courier_id=assigned_courier_id,
            customer_zone_id=customer.zone_id,
            restaurant_zone_id=restaurant.zone_id,
            status=order_status,
            subtotal_cents=subtotal_cents,
            delivery_fee_cents=DELIVERY_FEE_CENTS,
            total_amount_cents=total_amount_cents,
            created_at=order_created_at,
            updated_at=order_updated_at,
        )

        orders.append(order)

        for menu_item in selected_menu_items:
            order_item = OrderItem(
                order_item_id=order_item_id,
                order_id=order_id,
                menu_item_id=menu_item.menu_item_id,
                quantity=1,
                unit_price_cents=menu_item.price_cents,
                total_price_cents=menu_item.price_cents,
            )

            order_items.append(order_item)

            order_item_id = order_item_id + 1

        delivery_status = choose_delivery_status(order_status)

        if delivery_status is not None:
            assigned_at, picked_up_at, delivered_at, delivery_updated_at = (
                calculate_delivery_timestamps(
                        delivery_status=delivery_status,
                        order_created_at=order_created_at,
                    )
            )
            delivery = Delivery(
                delivery_id=delivery_id,
                order_id=order_id,
                courier_id=courier.courier_id,
                status=delivery_status,
                assigned_at=assigned_at,
                picked_up_at=picked_up_at,
                delivered_at=delivered_at,
                created_at=assigned_at,
                updated_at=delivery_updated_at,
            )

            deliveries.append(delivery)

            delivery_id = delivery_id + 1

        customer_index = customer_index + 1
        restaurant_index = restaurant_index + 1
        courier_index = courier_index + 1

        if customer_index == len(customers):
            customer_index = 0

        if restaurant_index == len(restaurants):
            restaurant_index = 0

        if courier_index == len(couriers):
            courier_index = 0

    return orders, order_items, deliveries

def delete_existing_order_data() -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM app.order_items;")
            cur.execute("DELETE FROM app.deliveries;")
            cur.execute("DELETE FROM app.orders;")

def insert_orders(orders: list[Order]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for order in orders:
                cur.execute(
                    """
                    INSERT INTO app.orders (
                        order_id,
                        customer_id,
                        restaurant_id,
                        courier_id,
                        customer_zone_id,
                        restaurant_zone_id,
                        status,
                        subtotal_cents,
                        delivery_fee_cents,
                        total_amount_cents,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (order_id) DO UPDATE
                    SET
                        customer_id = EXCLUDED.customer_id,
                        restaurant_id = EXCLUDED.restaurant_id,
                        courier_id = EXCLUDED.courier_id,
                        customer_zone_id = EXCLUDED.customer_zone_id,
                        restaurant_zone_id = EXCLUDED.restaurant_zone_id,
                        status = EXCLUDED.status,
                        subtotal_cents = EXCLUDED.subtotal_cents,
                        delivery_fee_cents = EXCLUDED.delivery_fee_cents,
                        total_amount_cents = EXCLUDED.total_amount_cents,
                        updated_at = EXCLUDED.updated_at;
                    """,
                    (
                        order.order_id,
                        order.customer_id,
                        order.restaurant_id,
                        order.courier_id,
                        order.customer_zone_id,
                        order.restaurant_zone_id,
                        order.status,
                        order.subtotal_cents,
                        order.delivery_fee_cents,
                        order.total_amount_cents,
                        order.created_at,
                        order.updated_at,
                    ),
                )


def insert_order_items(order_items: list[OrderItem]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for order_item in order_items:
                cur.execute(
                    """
                    INSERT INTO app.order_items (
                        order_item_id,
                        order_id,
                        menu_item_id,
                        quantity,
                        unit_price_cents,
                        total_price_cents,
                        created_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NOW()
                    )
                    ON CONFLICT (order_item_id) DO UPDATE
                    SET
                        order_id = EXCLUDED.order_id,
                        menu_item_id = EXCLUDED.menu_item_id,
                        quantity = EXCLUDED.quantity,
                        unit_price_cents = EXCLUDED.unit_price_cents,
                        total_price_cents = EXCLUDED.total_price_cents;
                    """,
                    (
                        order_item.order_item_id,
                        order_item.order_id,
                        order_item.menu_item_id,
                        order_item.quantity,
                        order_item.unit_price_cents,
                        order_item.total_price_cents,
                    ),
                )


def insert_deliveries(deliveries: list[Delivery]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for delivery in deliveries:
                cur.execute(
                    """
                    INSERT INTO app.deliveries (
                        delivery_id,
                        order_id,
                        courier_id,
                        status,
                        assigned_at,
                        picked_up_at,
                        delivered_at,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (delivery_id) DO UPDATE
                    SET
                        order_id = EXCLUDED.order_id,
                        courier_id = EXCLUDED.courier_id,
                        status = EXCLUDED.status,
                        assigned_at = EXCLUDED.assigned_at,
                        picked_up_at = EXCLUDED.picked_up_at,
                        delivered_at = EXCLUDED.delivered_at,
                        updated_at = EXCLUDED.updated_at;
                    """,
                    (
                        delivery.delivery_id,
                        delivery.order_id,
                        delivery.courier_id,
                        delivery.status,
                        delivery.assigned_at,
                        delivery.picked_up_at,
                        delivery.delivered_at,
                        delivery.created_at,
                        delivery.updated_at
                    ),
                )
