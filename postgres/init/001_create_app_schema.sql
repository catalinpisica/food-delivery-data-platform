CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.zones (
    zone_id INTEGER PRIMARY KEY,
    zone_name TEXT NOT NULL,
    city TEXT NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS app.customers (
    customer_id INTEGER PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES app.zones(zone_id),
    signup_channel TEXT NOT NULL CHECK (
        signup_channel IN ('organic', 'paid_search', 'referral', 'social')
    ),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS app.restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    restaurant_name TEXT NOT NULL,
    zone_id INTEGER NOT NULL REFERENCES app.zones(zone_id),
    cuisine_type TEXT NOT NULL CHECK (
        cuisine_type IN (
            'Italian',
            'Indian',
            'Japanese',
            'Turkish',
            'Chinese',
            'Dutch',
            'Thai',
            'Mexican',
            'Burgers',
            'Healthy'
        )
    ),
    price_category TEXT NOT NULL CHECK (
        price_category IN (
            'budget',
            'mid_range',
            'premium'
        )
    ),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS app.menu_items (
    menu_item_id INTEGER PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES app.restaurants(restaurant_id),
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (
        price_cents >= 0
    ),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    is_available BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS app.couriers (
    courier_id INTEGER PRIMARY KEY,
    home_zone_id INTEGER NOT NULL REFERENCES app.zones(zone_id),
    vehicle_type TEXT NOT NULL CHECK (
        vehicle_type IN (
            'bike',
            'ebike',
            'scooter',
            'car'
        )
    ),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN (
            'offline',
            'available',
            'delivering'
        )
    )
);

CREATE TABLE IF NOT EXISTS app.orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES app.customers(customer_id),
    restaurant_id INTEGER NOT NULL REFERENCES app.restaurants(restaurant_id),
    courier_id INTEGER REFERENCES app.couriers(courier_id),
    customer_zone_id INTEGER NOT NULL REFERENCES app.zones(zone_id),
    restaurant_zone_id INTEGER NOT NULL REFERENCES app.zones(zone_id),
    status TEXT NOT NULL CHECK (
        status IN (
            'CREATED',
            'ACCEPTED',
            'COURIER_ASSIGNED',
            'PICKED_UP',
            'DELIVERED',
            'CANCELLED'
        )
    ),
    subtotal_cents INTEGER NOT NULL CHECK (
        subtotal_cents >= 0
    ),
    delivery_fee_cents INTEGER NOT NULL CHECK (
        delivery_fee_cents >= 0
    ),
    total_amount_cents INTEGER NOT NULL CHECK (
        total_amount_cents >= 0
    ),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS app.order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES app.orders(order_id),
    menu_item_id INTEGER NOT NULL REFERENCES app.menu_items(menu_item_id),
    quantity INTEGER NOT NULL CHECK (
        quantity > 0
    ),
    unit_price_cents INTEGER NOT NULL CHECK (
        unit_price_cents >= 0
    ),
    total_price_cents INTEGER NOT NULL CHECK (
        total_price_cents >= 0
    ),
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS app.deliveries (
    delivery_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES app.orders(order_id),
    courier_id INTEGER NOT NULL REFERENCES app.couriers(courier_id),
    status TEXT NOT NULL CHECK (
        status IN (
            'ASSIGNED',
            'PICKED_UP',
            'DELIVERED',
            'CANCELLED'
        )
    ),
    assigned_at TIMESTAMPTZ,
    picked_up_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

INSERT INTO app.zones (
    zone_id,
    zone_name,
    city,
    latitude,
    longitude,
    created_at
)
VALUES
    (1, 'Amsterdam Centrum', 'Amsterdam', 52.373079, 4.892453, NOW()),
    (2, 'Amsterdam West', 'Amsterdam', 52.370216, 4.852650, NOW()),
    (3, 'Amsterdam Zuid', 'Amsterdam', 52.341438, 4.877260, NOW()),
    (4, 'Amsterdam Oost', 'Amsterdam', 52.355549, 4.934670, NOW()),
    (5, 'Amsterdam Noord', 'Amsterdam', 52.399510, 4.935180, NOW())
ON CONFLICT (zone_id) DO NOTHING;
