#!/usr/bin/env bash
set -euo pipefail
CONNECT_URL="http://localhost:8083"
CONNECTOR_NAME="food-delivery-postgres-connector"
CONNECTOR_CONFIG_PATH="debezium/connectors/postgres-source.json"

echo "Waiting for Debezium Connect at ${CONNECT_URL}..."

until curl --silent --fail "${CONNECT_URL}" > /dev/null; do
    sleep 2
done

echo "Debezium Connect is ready."

if curl --silent --fail "${CONNECT_URL}/connectors/${CONNECTOR_NAME}" > /dev/null; then
    echo "Connector ${CONNECTOR_NAME} already exists."
else
    echo "Registering connector ${CONNECTOR_NAME}..."

    curl --silent --fail \
        -X POST "${CONNECT_URL}/connectors" \
        -H "Content-Type: application/json" \
        --data "@${CONNECTOR_CONFIG_PATH}" \
        > /dev/null

    echo "Connector ${CONNECTOR_NAME} registered."
fi

echo "Connector status:"
curl --silent "${CONNECT_URL}/connectors/${CONNECTOR_NAME}/status"
echo