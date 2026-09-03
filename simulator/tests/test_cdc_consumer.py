import json

from delivery_simulator.cdc_consumer import (
    build_object_key,
    message_to_raw_event,
    write_batch_to_s3,
)
from delivery_simulator.object_storage import RAW_BUCKET_NAME


class FakeKafkaMessage:
    def __init__(
        self,
        topic: str = "food_delivery.app.orders",
        partition: int = 0,
        offset: int = 10,
        key: bytes | None = b'{"order_id": 1}',
        value: bytes | None = b'{"payload": {"after": {"order_id": 1}}}',
        timestamp: int = 1788267298927,
    ) -> None:
        self._topic = topic
        self._partition = partition
        self._offset = offset
        self._key = key
        self._value = value
        self._timestamp = timestamp

    def topic(self) -> str:
        return self._topic

    def partition(self) -> int:
        return self._partition

    def offset(self) -> int:
        return self._offset

    def key(self) -> bytes | None:
        return self._key

    def value(self) -> bytes | None:
        return self._value

    def timestamp(self) -> tuple[int, int]:
        return 1, self._timestamp


class FakeS3Client:
    def __init__(self) -> None:
        self.put_calls = []

    def put_object(self, Bucket: str, Key: str, Body: str) -> None:
        self.put_calls.append(
            {
                "Bucket": Bucket,
                "Key": Key,
                "Body": Body,
            }
        )


def test_build_object_key_uses_topic_partition_and_offsets() -> None:
    object_key = build_object_key(
        topic="food_delivery.app.orders",
        partition=0,
        first_offset=10,
        last_offset=25,
    )

    assert object_key.startswith("raw/cdc/orders/")
    assert "/partition=0/" in object_key
    assert object_key.endswith("/offsets=10-25.jsonl")


def test_message_to_raw_event_keeps_kafka_metadata() -> None:
    message = FakeKafkaMessage()

    raw_event = message_to_raw_event(message)

    assert raw_event["topic"] == "food_delivery.app.orders"
    assert raw_event["partition"] == 0
    assert raw_event["offset"] == 10
    assert raw_event["key"] == '{"order_id": 1}'
    assert raw_event["value"] == '{"payload": {"after": {"order_id": 1}}}'
    assert raw_event["kafka_timestamp"] == 1788267298927
    assert "landed_at" in raw_event


def test_message_to_raw_event_handles_empty_key_and_value() -> None:
    message = FakeKafkaMessage(key=None, value=None)

    raw_event = message_to_raw_event(message)

    assert raw_event["key"] is None
    assert raw_event["value"] is None


def test_write_batch_to_s3_writes_jsonl_object() -> None:
    s3_client = FakeS3Client()
    messages = [
        FakeKafkaMessage(offset=10),
        FakeKafkaMessage(offset=11),
    ]

    object_key = write_batch_to_s3(
        s3_client=s3_client,
        topic="food_delivery.app.orders",
        messages=messages,
    )

    assert len(s3_client.put_calls) == 1

    put_call = s3_client.put_calls[0]
    body_lines = put_call["Body"].splitlines()

    assert put_call["Bucket"] == RAW_BUCKET_NAME
    assert put_call["Key"] == object_key
    assert object_key.startswith("raw/cdc/orders/")
    assert object_key.endswith("/offsets=10-11.jsonl")
    assert len(body_lines) == 2

    first_event = json.loads(body_lines[0])
    second_event = json.loads(body_lines[1])

    assert first_event["offset"] == 10
    assert second_event["offset"] == 11
