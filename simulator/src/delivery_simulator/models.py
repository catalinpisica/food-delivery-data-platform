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
