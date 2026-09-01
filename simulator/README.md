# Delivery Simulator

Generates synthetic OLTP data for the food delivery platform.

The simulator is responsible for creating realistic-looking source data in PostgreSQL. Later parts of the platform will move this data through streaming, storage, transformation, and analytics layers.

## Setup

From the repo root:

```bash
cd simulator
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

What these commands mean:

- `cd simulator` moves into the Python simulator project.
- `python -m venv .venv` creates a local virtual environment.
- `source .venv/bin/activate` tells your terminal to use that environment.
- `pip install -e ".[dev]"` installs the simulator in editable mode, plus development tools like `pytest`.

## Database

Start PostgreSQL from the repo root:

```bash
docker compose up -d postgres
```

By default, the simulator connects to the local PostgreSQL container using these settings:

| Variable | Default |
|---|---|
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `food_delivery` |
| `POSTGRES_USER` | `food_delivery_user` |
| `POSTGRES_PASSWORD` | `food_delivery_password` |

You can check which settings the simulator will use:

```bash
delivery-simulator show-db-config
```

You can check that the simulator can connect to PostgreSQL:

```bash
delivery-simulator check-db
```

## Commands

List the zones already loaded in PostgreSQL:

```bash
delivery-simulator list-zones
```

Seed reference data:

```bash
delivery-simulator seed --profile tiny
```

This inserts or updates:
- customers
- restaurants
- menu items
- couriers

Preview generated orders without inserting them:

```bash
delivery-simulator preview-orders --profile tiny
```

Generate and insert orders:

```bash
delivery-simulator generate-orders --profile tiny
```

This inserts or updates:
- orders
- order items
- deliveries

## Profiles

Profiles control how much data the simulator generates.

| Profile | Customers | Restaurants | Couriers | Orders |
|---|---:|---:|---:|---:|
| `tiny` | 100 | 20 | 25 | 500 |
| `dev` | 1,000 | 100 | 150 | 5,000 |
| `demo` | 10,000 | 500 | 750 | 50,000 |

## Tests

Run the simulator tests from the repo root:

```bash
simulator/.venv/bin/pytest simulator/tests
```

Or, if your virtual environment is active and you are inside the `simulator` folder:

```bash
pytest
```