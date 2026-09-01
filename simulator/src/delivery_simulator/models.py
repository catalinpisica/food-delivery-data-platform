from dataclasses import dataclass

@dataclass(frozen=True)
class Zone:
    zone_id: int
    zone_name: str

@dataclass(frozen=True)
class Restaurant:
    restaurant_id: int
    restaurant_name: str
    zone_id: int
    cuisine_type: str
    price_category: str
    is_active: bool

@dataclass(frozen=True)
class MenuItem:
    menu_item_id: int
    restaurant_id: int
    item_name: str
    category: str
    price_cents: int
    is_available: bool

@dataclass(frozen=True)
class Courier:
    courier_id: int
    home_zone_id: int
    vehicle_type: str
    status: str

@dataclass(frozen=True)
class Customer:
    customer_id: int
    zone_id: int
    signup_channel: str
    is_active: bool

@dataclass(frozen=True)
class Order:
    order_id: int
    customer_id: int
    restaurant_id: int
    courier_id: int | None
    customer_zone_id: int
    restaurant_zone_id: int
    status: str
    subtotal_cents: int
    delivery_fee_cents: int
    total_amount_cents: int


@dataclass(frozen=True)
class OrderItem:
    order_item_id: int
    order_id: int
    menu_item_id: int
    quantity: int
    unit_price_cents: int
    total_price_cents: int


@dataclass(frozen=True)
class Delivery:
    delivery_id: int
    order_id: int
    courier_id: int
    status: str