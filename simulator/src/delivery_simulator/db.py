import psycopg

POSTGRES_DSN = (
    "host=localhost "
    "port=5432 "
    "dbname=food_delivery "
    "user=food_delivery_user "
    "password=food_delivery_password"
)

def connect() -> psycopg.Connection:
    return psycopg.connect(POSTGRES_DSN)