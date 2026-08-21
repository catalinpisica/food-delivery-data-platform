from delivery_simulator.db import connect
from delivery_simulator.models import Courier, Customer, MenuItem, Restaurant, Zone


CUISINE_TYPES = [
    "Italian",
    "Indian",
    "Japanese",
    "Turkish",
    "Chinese",
    "Dutch",
    "Thai",
    "Mexican",
    "Burgers",
    "Healthy",
]

PRICE_CATEGORIES = [
    "budget",
    "mid_range",
    "premium",
]

MENU_ITEM_CATEGORIES = [
    "main",
    "side",
    "drink",
    "dessert",
    "starter"
]

MENU_ITEM_NAMES = [
    "Signature Bowl",
    "House Special",
    "Classic Plate",
    "Fresh Salad",
    "Spiced Wrap",
]

VEHICLE_TYPES = [
    "bike",
    "ebike",
    "scooter",
    "car",
]

COURIER_STATUSES = [
    "offline",
    "available",
    "delivering",
]

INITIAL_COURIER_STATUS = "available"

SIGNUP_CHANNELS = [
    "organic",
    "paid_search",
    "referral",
    "social",
]

def list_zones() -> list[Zone]:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    zone_id,
                    zone_name
                FROM app.zones
                ORDER BY zone_id;
                """
            )
            rows = cur.fetchall()

    return [
        Zone(zone_id=zone_id, zone_name=zone_name)
        for zone_id, zone_name in rows
    ]

def generate_restaurants(
        zones: list[Zone],
        restaurant_count: int,
) -> list[Restaurant]:
    restaurants = []

    zone_index = 0
    cuisine_index = 0
    price_index = 0

    for restaurant_id in range(1, restaurant_count + 1):
        zone = zones[zone_index]
        cuisine_type = CUISINE_TYPES[cuisine_index]
        price_category = PRICE_CATEGORIES[price_index]

        restaurant = Restaurant(
            restaurant_id=restaurant_id,
            restaurant_name=f"{cuisine_type} Kitchen {restaurant_id}",
            zone_id=zone.zone_id,
            cuisine_type=cuisine_type,
            price_category=price_category,
            is_active=True,
        )

        restaurants.append(restaurant)

        zone_index = zone_index + 1
        cuisine_index = cuisine_index + 1
        price_index = price_index + 1

        if zone_index == len(zones):
            zone_index = 0

        if cuisine_index == len(CUISINE_TYPES):
            cuisine_index = 0

        if price_index == len(PRICE_CATEGORIES):
            price_index = 0

    return restaurants

def insert_restaurants(restaurants: list[Restaurant]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for restaurant in restaurants:
                cur.execute(
                    """
                    INSERT INTO app.restaurants (
                        restaurant_id,
                        restaurant_name,
                        zone_id,
                        cuisine_type,
                        price_category,
                        created_at,
                        updated_at,
                        is_active)
                    
                    VALUES(
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NOW(),
                        NOW(),
                        %s
                    )
                    ON CONFLICT (restaurant_id) DO UPDATE
                    SET 
                        restaurant_name = EXCLUDED.restaurant_name,
                        zone_id = EXCLUDED.zone_id,
                        cuisine_type = EXCLUDED.cuisine_type,
                        price_category = EXCLUDED.price_category,
                        updated_at = NOW(),
                        is_active = EXCLUDED.is_active;
                    """,
                    (
                        restaurant.restaurant_id,
                        restaurant.restaurant_name,
                        restaurant.zone_id,
                        restaurant.cuisine_type,
                        restaurant.price_category,
                        restaurant.is_active
                    ),
                )

def generate_menu_items(
    restaurants: list[Restaurant],
    items_per_restaurant: int,
) -> list[MenuItem]:
    menu_items = []

    menu_item_id = 1
    category_index = 0
    name_index = 0

    for restaurant in restaurants:
        for item_number in range(1, items_per_restaurant + 1):
            category = MENU_ITEM_CATEGORIES[category_index]
            base_name = MENU_ITEM_NAMES[name_index]

            menu_item = MenuItem(
                menu_item_id=menu_item_id,
                restaurant_id=restaurant.restaurant_id,
                item_name=f"{base_name} {item_number}",
                category=category,
                price_cents=800 + (item_number * 150),
                is_available=True,
            )

            menu_items.append(menu_item)

            menu_item_id = menu_item_id + 1
            category_index = category_index + 1
            name_index = name_index + 1

            if category_index == len(MENU_ITEM_CATEGORIES):
                category_index = 0

            if name_index == len(MENU_ITEM_NAMES):
                name_index = 0

    return menu_items

def insert_menu_items(menu_items: list[MenuItem]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for menu_item in menu_items:
                cur.execute(
                    """
                    INSERT INTO app.menu_items (
                        menu_item_id,
                        restaurant_id,
                        item_name,
                        category,
                        price_cents,
                        created_at,
                        updated_at,
                        is_available
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NOW(),
                        NOW(),
                        %s
                    )
                    ON CONFLICT (menu_item_id) DO UPDATE
                    SET
                        restaurant_id = EXCLUDED.restaurant_id,
                        item_name = EXCLUDED.item_name,
                        category = EXCLUDED.category,
                        price_cents = EXCLUDED.price_cents,
                        updated_at = NOW(),
                        is_available = EXCLUDED.is_available;
                    """,
                    (
                        menu_item.menu_item_id,
                        menu_item.restaurant_id,
                        menu_item.item_name,
                        menu_item.category,
                        menu_item.price_cents,
                        menu_item.is_available,
                    ),
                )

def generate_couriers(
        zones: list[Zone], 
        courier_count: int
) -> list[Courier]:
    couriers=[]

    zone_index = 0
    vehicle_index = 0

    for courier_id in range(1, courier_count + 1):
        zone = zones[zone_index]
        vehicle_type = VEHICLE_TYPES[vehicle_index]

        courier = Courier(
            courier_id=courier_id,
            home_zone_id=zone.zone_id,
            vehicle_type=vehicle_type,
            status=INITIAL_COURIER_STATUS,
        )

        couriers.append(courier)

        zone_index = zone_index + 1
        vehicle_index = vehicle_index + 1

        if zone_index == len(zones):
            zone_index = 0

        if vehicle_index == len(VEHICLE_TYPES):
            vehicle_index = 0

    return couriers

def insert_couriers(couriers: list[Courier]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for courier in couriers:
                cur.execute(
                    """
                    INSERT INTO app.couriers (
                        courier_id,
                        home_zone_id,
                        vehicle_type,
                        created_at,
                        updated_at,
                        status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        NOW(),
                        NOW(),
                        %s
                    )
                    ON CONFLICT (courier_id) DO UPDATE
                    SET
                        home_zone_id = EXCLUDED.home_zone_id,
                        vehicle_type = EXCLUDED.vehicle_type,
                        updated_at = NOW(),
                        status = EXCLUDED.status;
                    """,
                    (
                        courier.courier_id,
                        courier.home_zone_id,
                        courier.vehicle_type,
                        courier.status,
                    ),
                )

def generate_customers(
        zones: list[Zone],
        customer_count: int,
) -> list[Customer]:
    customers = []

    zone_index = 0
    signup_channel_index = 0

    for customer_id in range(1, customer_count + 1):
        zone = zones[zone_index]
        signup_channel = SIGNUP_CHANNELS[signup_channel_index]

        customer = Customer(
            customer_id=customer_id,
            zone_id=zone.zone_id,
            signup_channel=signup_channel,
            is_active=True,
        )

        customers.append(customer)

        zone_index = zone_index + 1
        signup_channel_index = signup_channel_index + 1

        if zone_index == len(zones):
            zone_index = 0

        if signup_channel_index == len(SIGNUP_CHANNELS):
            signup_channel_index = 0

    return customers

def insert_customers(customers: list[Customer]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for customer in customers:
                cur.execute(
                    """
                    INSERT INTO app.customers (
                        customer_id,
                        zone_id,
                        signup_channel,
                        created_at,
                        updated_at,
                        is_active
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        NOW(),
                        NOW(),
                        %s
                    )
                    ON CONFLICT (customer_id) DO UPDATE
                    SET
                        zone_id = EXCLUDED.zone_id,
                        signup_channel = EXCLUDED.signup_channel,
                        updated_at = NOW(),
                        is_active = EXCLUDED.is_active;
                    """,
                    (
                        customer.customer_id,
                        customer.zone_id,
                        customer.signup_channel,
                        customer.is_active,
                    ),
                )
