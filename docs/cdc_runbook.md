# CDC Runbook

This runbook explains how to run and verify the local change data capture flow.

CDC means change data capture. In this project, that means Postgres table changes are captured by Debezium and written into Redpanda topics.

## Flow

```text
delivery-simulator -> PostgreSQL -> Debezium Connect -> Redpanda topics
```

PostgreSQL is the operational system of record. The simulator writes rows into PostgreSQL. Debezium reads PostgreSQL changes and publishes them to Redpanda using the Kafka protocol.

## Start Services

From the repo root:

```bash
docker compose up -d postgres redpanda debezium
```

This starts:

- PostgreSQL on port `5432`
- Redpanda Kafka-compatible broker on port `19092`
- Debezium Connect REST API on port `8083`

## Verify Services

Check container status:

```bash
docker compose ps
```

Check Debezium Connect:

```bash
curl http://localhost:8083/
```

Expected: a JSON response with a Kafka Connect version and Kafka cluster id.

List Redpanda topics:

```bash
docker compose exec redpanda rpk topic list
```

## Create Buckets

Create the raw data bucket in SeaweedFS:

```bash
simulator/.venv/bin/python scripts/create_s3_buckets.py
```

This creates the `food-delivery-raw` bucket if it does not already exist.

## Register Connector

Debezium Connect runs as a service, but it needs a connector configuration before it knows which database and tables to watch.

The connector config is stored in `debezium/connectors/postgres-source.json`.

Register or verify the Postgres connector:

```bash
./scripts/register_debezium_connector.sh
```

The script waits for Debezium Connect, creates the connector if it is missing, and prints the connector status.

Check connector status:

```bash
curl http://localhost:8083/connectors/food-delivery-postgres-connector/status
```

Expected: the connector and task should both be `RUNNING`.

## Generate Source Data

The simulator writes data into PostgreSQL. Debezium then captures those table changes.

```bash
delivery-simulator seed --profile tiny
delivery-simulator generate-orders --profile tiny
```

## Consume CDC Events

Read one order CDC event:

```bash
docker compose exec redpanda rpk topic consume food_delivery.app.orders --num 1
```

Debezium events contain a large JSON structure. The most important part is inside `payload`.

Useful fields:

- `before`: the row before the change
- `after`: the row after the change
- `op`: the operation type

Common operation values:

| Value | Meaning |
|---|---|
| `r` | snapshot read |
| `c` | create / insert |
| `u` | update |
| `d` | delete |

## Live Update Test

Run this from the repo root:

```bash
docker compose exec postgres psql -U food_delivery_user -d food_delivery -c "
UPDATE app.orders
SET status = 'PICKED_UP',
    updated_at = NOW()
WHERE order_id = 1;
"
```

Then consume from the orders CDC topic:

```bash
docker compose exec redpanda rpk topic consume food_delivery.app.orders
```

Look for:

```json
"op": "u"
```

That proves this path is working:

```text
Postgres UPDATE -> Debezium CDC -> Redpanda topic
```

## Important Topics

Manual smoke-test topics:

```text
orders
order_items
deliveries
```

Debezium CDC topics:

```text
food_delivery.app.orders
food_delivery.app.order_items
food_delivery.app.deliveries
```

Kafka Connect internal topics:

```text
debezium_configs
debezium_offsets
debezium_statuses
```

The real pipeline should use the Debezium CDC topics.
