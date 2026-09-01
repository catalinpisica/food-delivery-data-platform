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

DELIVERED_ORDER_STATUS = "DELIVERED"
DELIVERED_DELIVERY_STATUS = "DELIVERED"
DELIVERY_FEE_CENTS = 299
ITEMS_PER_ORDER = 2

def generate_delivered_orders(
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
            courier_id=courier.courier_id,
            customer_zone_id=customer.zone_id,
            restaurant_zone_id=restaurant.zone_id,
            status=DELIVERED_ORDER_STATUS,
            subtotal_cents=subtotal_cents,
            delivery_fee_cents=DELIVERY_FEE_CENTS,
            total_amount_cents=total_amount_cents,
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

        delivery = Delivery(
            delivery_id=delivery_id,
            order_id=order_id,
            courier_id=courier.courier_id,
            status=DELIVERED_DELIVERY_STATUS,
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
                        NOW(),
                        NOW()
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
                        updated_at = NOW();
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
                        NOW(),
                        NOW(),
                        NOW(),
                        NOW(),
                        NOW()
                    )
                    ON CONFLICT (delivery_id) DO UPDATE
                    SET
                        order_id = EXCLUDED.order_id,
                        courier_id = EXCLUDED.courier_id,
                        status = EXCLUDED.status,
                        assigned_at = EXCLUDED.assigned_at,
                        picked_up_at = EXCLUDED.picked_up_at,
                        delivered_at = EXCLUDED.delivered_at,
                        updated_at = NOW();
                    """,
                    (
                        delivery.delivery_id,
                        delivery.order_id,
                        delivery.courier_id,
                        delivery.status,
                    ),
                )