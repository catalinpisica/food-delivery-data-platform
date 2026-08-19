CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.zones (
    zone_id INTEGER PRIMARY KEY,
    zone_name TEXT NOT NULL,
    city TEXT NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
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