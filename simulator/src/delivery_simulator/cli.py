import argparse
from delivery_simulator.config import get_profile
from delivery_simulator.db import connect
from delivery_simulator.seed_reference_data import (
    generate_couriers,
    generate_customers,
    generate_menu_items,
    generate_restaurants,
    insert_couriers,
    insert_customers,
    insert_menu_items,
    insert_restaurants,
    list_couriers,
    list_customers,
    list_menu_items,
    list_restaurants,
    list_zones,
)
from delivery_simulator.generate_orders import (
    generate_orders,
    insert_deliveries,
    insert_order_items,
    insert_orders,
    delete_existing_order_data

)
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="delivery-simulator",
        description="Synthetic data simulator for the food delivery data platform"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    seed_parser = subparsers.add_parser(
        "seed",
        help="Seed reference entities such as restaurants, menu items, couriers, and customers."
    )

    seed_parser.add_argument(
        "--profile",
        choices=["tiny", "dev", "demo"],
        default="tiny",
        help="Dataset size profile to generate.",
    )

    subparsers.add_parser(
        "check-db",
        help="Check that the simulator can connect to PostgreSQL."
    )

    subparsers.add_parser(
        "list-zones",
        help="List delivery zones from PostgreSQL",
    )

    preview_restaurants_parser = subparsers.add_parser(
        "preview-restaurants",
        help="Preview generated restaurants without inserting them.",
    )

    preview_restaurants_parser.add_argument(
        "--profile",
        choices=["tiny", "dev", "demo"],
        default="tiny",
        help="Dataset size profile to generate."
    )

    preview_menu_items_parser = subparsers.add_parser(
        "preview-menu-items",
        help="Preview generated menu items without inserting them",
    )

    preview_menu_items_parser.add_argument(
        "--profile",
        choices=["tiny", "dev", "demo"],
        default="tiny",
        help="Dataset size profile to generate.",
    )

    preview_couriers_parser = subparsers.add_parser(
        "preview-couriers",
        help="Preview generated couriers without inserting them."
    )

    preview_couriers_parser.add_argument(
        "--profile",
        choices=["tiny", "dev", "demo"],
        default="tiny",
        help="Dataset size profile to generate.",
    )
    preview_orders_parser = subparsers.add_parser(
        "preview-orders",
        help="Preview generated orders without inserting them.",
    )
    preview_orders_parser.add_argument(
        "--profile",
        choices=["tiny", "dev", "demo"],
        default="tiny",
        help="Dataset size profile to generate.",
    )
    generate_orders_parser = subparsers.add_parser(
        "generate-orders",
        help="Generate and insert orders.",
    )
    generate_orders_parser.add_argument(
        "--profile",
        choices=["tiny", "dev", "demo"],
        default="tiny",
        help="Dataset size profile to generate.",
    )

    return parser



def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "seed":
        profile = get_profile(args.profile)
        zones = list_zones()
        restaurants = generate_restaurants(
            zones=zones,
            restaurant_count=profile.restaurant_count,
        )
        menu_items = generate_menu_items(
            restaurants=restaurants,
            items_per_restaurant=5
        )
        couriers = generate_couriers(
            zones=zones,
            courier_count=profile.courier_count,
        )
        customers = generate_customers(
            zones=zones,
            customer_count=profile.customer_count,
        )

        insert_customers(customers)
        insert_restaurants(restaurants)
        insert_menu_items(menu_items)
        insert_couriers(couriers)

        print(f"seed profile: {profile.name}")
        print(f"customers inserted/updated: {len(customers)}")
        print(f"restaurants inserted/updated: {len(restaurants)}")
        print(f"menu items inserted/updated: {len(menu_items)}")
        print(f"couriers inserted/updated: {len(couriers)}")
        return

    if args.command == "check-db":
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user;")
                database_name, user_name = cur.fetchone()

        print(f"database: {database_name}")
        print(f"user: {user_name}")
        return

    if args.command == "list-zones":
        zones = list_zones()

        for zone in zones:
            print(f"{zone.zone_id}: {zone.zone_name}")

        return

    if args.command == "preview-restaurants":
        profile = get_profile(args.profile)
        zones = list_zones()
        restaurants = generate_restaurants(
            zones=zones,
            restaurant_count=profile.restaurant_count,
        )

        for restaurant in restaurants[:10]:
            print(
                f"{restaurant.restaurant_id}: "
                f"{restaurant.restaurant_name}, "
                f"zone_id={restaurant.zone_id}, "
                f"cuisine={restaurant.cuisine_type}, "
                f"price={restaurant.price_category}"
            )

        print(f"generated restaurants: {len(restaurants)}")
        return

    if args.command == "preview-menu-items":
        profile = get_profile(args.profile)
        zones = list_zones()
        restaurants = generate_restaurants(
            zones=zones,
            restaurant_count=profile.restaurant_count,
        )
        menu_items = generate_menu_items(
            restaurants=restaurants,
            items_per_restaurant=5
        )

        for menu_item in menu_items[:10]:
            print(
                f"{menu_item.menu_item_id}: "
                f"restaurant_id={menu_item.restaurant_id}, "
                f"{menu_item.item_name}, "
                f"category={menu_item.category}, "
                f"price_cents={menu_item.price_cents}"
            )

        print(f"generated menu items: {len(menu_items)}")
        return

    if args.command == "preview-couriers":
        profile = get_profile(args.profile)
        zones = list_zones()
        couriers = generate_couriers(
            zones=zones,
            courier_count=profile.courier_count,
        )

        for courier in couriers[:10]:
            print(
                f"{courier.courier_id}: "
                f"home_zone_id={courier.home_zone_id}, "
                f"vehicle={courier.vehicle_type}, "
                f"status={courier.status}"
            )

        print(f"generated couriers: {len(couriers)}")
        return

    if args.command == "preview-orders":
        profile = get_profile(args.profile)
        customers = list_customers()
        restaurants = list_restaurants()
        menu_items = list_menu_items()
        couriers = list_couriers()

        orders, order_items, deliveries = generate_orders(
            customers=customers,
            restaurants=restaurants,
            menu_items=menu_items,
            couriers=couriers,
            order_count=profile.orders_count,
        )

        for order in orders[:10]:
            print(
                f"{order.order_id}: "
                f"customer_id={order.customer_id}, "
                f"restaurant_id={order.restaurant_id}, "
                f"courier_id={order.courier_id}, "
                f"total_cents={order.total_amount_cents}"
            )

        print(f"generated orders: {len(orders)}")
        print(f"generated order items: {len(order_items)}")
        print(f"generated deliveries: {len(deliveries)}")
        return

    if args.command == "generate-orders":
        profile = get_profile(args.profile)
        customers = list_customers()
        restaurants = list_restaurants()
        menu_items = list_menu_items()
        couriers = list_couriers()

        orders, order_items, deliveries = generate_orders(
            customers=customers,
            restaurants=restaurants,
            menu_items=menu_items,
            couriers=couriers,
            order_count=profile.orders_count,
        )

        delete_existing_order_data()
        insert_orders(orders)
        insert_order_items(order_items)
        insert_deliveries(deliveries)

        print(f"generated profile: {profile.name}")
        print(f"orders inserted/updated: {len(orders)}")
        print(f"order items inserted/updated: {len(order_items)}")
        print(f"deliveries inserted/updated: {len(deliveries)}")
        return
