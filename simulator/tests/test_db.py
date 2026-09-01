from delivery_simulator.db import (
    build_dsn,
    get_database_config,
    get_safe_database_config,
)


def clear_postgres_environment(monkeypatch) -> None:
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)


def test_database_config_uses_local_defaults(monkeypatch) -> None:
    clear_postgres_environment(monkeypatch)

    config = get_database_config()

    assert config["host"] == "localhost"
    assert config["port"] == "5432"
    assert config["dbname"] == "food_delivery"
    assert config["user"] == "food_delivery_user"
    assert config["password"] == "food_delivery_password"


def test_database_config_can_use_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_HOST", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "15432")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")

    config = get_database_config()

    assert config["host"] == "postgres"
    assert config["port"] == "15432"
    assert config["dbname"] == "test_db"
    assert config["user"] == "test_user"
    assert config["password"] == "test_password"


def test_build_dsn_uses_database_config(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_HOST", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "15432")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")

    dsn = build_dsn()

    assert dsn == (
        "host=postgres "
        "port=15432 "
        "dbname=test_db "
        "user=test_user "
        "password=test_password"
    )


def test_safe_database_config_hides_password(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret_password")

    config = get_safe_database_config()

    assert config["password"] == "***"
