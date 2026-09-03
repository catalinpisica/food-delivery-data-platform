import json
from datetime import datetime, timezone

from confluent_kafka import Consumer

from delivery_simulator.kafka_config import (
    CDC_CONSUMER_GROUP_ID,
    CDC_TOPICS,
    KAFKA_BOOTSTRAP_SERVERS,
)
from delivery_simulator.object_storage import RAW_BUCKET_NAME, create_s3_client


MAX_MESSAGES_PER_RUN = 100


def create_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": CDC_CONSUMER_GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def build_object_key(topic: str, partition: int, first_offset: int, last_offset: int) -> str:
    table_name = topic.split(".")[-1]
    now = datetime.now(timezone.utc)

    return (
        f"raw/cdc/{table_name}/"
        f"year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"partition={partition}/"
        f"offsets={first_offset}-{last_offset}.jsonl"
    )


def message_to_raw_event(message) -> dict:
    return {
        "topic": message.topic(),
        "partition": message.partition(),
        "offset": message.offset(),
        "key": message.key().decode("utf-8") if message.key() is not None else None,
        "value": message.value().decode("utf-8") if message.value() is not None else None,
        "kafka_timestamp": message.timestamp()[1],
        "landed_at": datetime.now(timezone.utc).isoformat(),
    }


def write_batch_to_s3(s3_client, topic: str, messages: list) -> str:
    partition = messages[0].partition()
    first_offset = messages[0].offset()
    last_offset = messages[-1].offset()

    object_key = build_object_key(
        topic=topic,
        partition=partition,
        first_offset=first_offset,
        last_offset=last_offset,
    )

    lines = []

    for message in messages:
        raw_event = message_to_raw_event(message)
        lines.append(json.dumps(raw_event))

    body = "\n".join(lines) + "\n"

    s3_client.put_object(
        Bucket=RAW_BUCKET_NAME,
        Key=object_key,
        Body=body,
    )

    return object_key


def consume_cdc_to_s3() -> None:
    consumer = create_consumer()
    s3_client = create_s3_client()

    messages_by_topic = {}

    try:
        consumer.subscribe(CDC_TOPICS)

        while True:
            message = consumer.poll(1.0)

            if message is None:
                break

            if message.error():
                raise RuntimeError(message.error())

            topic = message.topic()

            if topic not in messages_by_topic:
                messages_by_topic[topic] = []

            messages_by_topic[topic].append(message)

            total_messages = 0

            for topic_messages in messages_by_topic.values():
                total_messages = total_messages + len(topic_messages)

            if total_messages >= MAX_MESSAGES_PER_RUN:
                break

        for topic, messages in messages_by_topic.items():
            object_key = write_batch_to_s3(
                s3_client=s3_client,
                topic=topic,
                messages=messages,
            )

            print(f"Wrote {len(messages)} messages to s3://{RAW_BUCKET_NAME}/{object_key}")

        consumer.commit(asynchronous=False)

    finally:
        consumer.close()