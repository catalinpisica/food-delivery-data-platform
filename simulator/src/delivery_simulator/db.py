import os

import psycopg

DEFAULT_POSTGRES_HOST = "localhost"
DEFAULT_POSTGRES_PORT = "5432"
DEFAULT_POSTGRES_DB = "food_delivery"
DEFAULT_POSTGRES_USER = "food_delivery_user"
DEFAULT_POSTGRES_PASSWORD = "food_delivery_password"


def get_database_config() -> dict[str, str]:
    return {
        "host": os.getenv("POSTGRES_HOST", DEFAULT_POSTGRES_HOST),
        "port": os.getenv("POSTGRES_PORT", DEFAULT_POSTGRES_PORT),
        "dbname": os.getenv("POSTGRES_DB", DEFAULT_POSTGRES_DB),
        "user": os.getenv("POSTGRES_USER", DEFAULT_POSTGRES_USER),
        "password": os.getenv("POSTGRES_PASSWORD", DEFAULT_POSTGRES_PASSWORD),
    }


def get_safe_database_config() -> dict[str, str]:
    config = get_database_config()

    return {
        "host": config["host"],
        "port": config["port"],
        "dbname": config["dbname"],
        "user": config["user"],
        "password": "***",
    }


def build_dsn() -> str:
    config = get_database_config()

    return (
        f"host={config['host']} "
        f"port={config['port']} "
        f"dbname={config['dbname']} "
        f"user={config['user']} "
        f"password={config['password']}"
    )


def connect() -> psycopg.Connection:
    return psycopg.connect(build_dsn())
