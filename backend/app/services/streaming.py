from collections import deque
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.orm import Session

from app.models import Event

EXPERIMENT_EVENTS_TOPIC = "experiment_events"


class EventProducer(Protocol):
    def send(self, topic: str, event: dict) -> None:
        ...


class EventConsumer(Protocol):
    def poll(self, topic: str, max_records: int = 100) -> list[dict]:
        ...


@dataclass
class StreamingStatus:
    mode: str
    topic: str
    queued_events: int
    last_error: str | None = None


class InMemoryEventBus:
    def __init__(self) -> None:
        self.messages: dict[str, deque[dict]] = {}

    def send(self, topic: str, event: dict) -> None:
        self.messages.setdefault(topic, deque()).append(event)

    def poll(self, topic: str, max_records: int = 100) -> list[dict]:
        queue = self.messages.setdefault(topic, deque())
        records = []
        while queue and len(records) < max_records:
            records.append(queue.popleft())
        return records

    def queued(self, topic: str) -> int:
        return len(self.messages.setdefault(topic, deque()))


class KafkaEventProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092") -> None:
        from kafka import KafkaProducer
        import json

        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )

    def send(self, topic: str, event: dict) -> None:
        self._producer.send(topic, event)
        self._producer.flush()


class KafkaEventConsumer:
    def __init__(self, bootstrap_servers: str = "localhost:9092") -> None:
        from kafka import KafkaConsumer
        import json

        self._consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=1000,
        )

    def poll(self, topic: str, max_records: int = 100) -> list[dict]:
        self._consumer.subscribe([topic])
        records = []
        for message in self._consumer:
            records.append(message.value)
            if len(records) >= max_records:
                break
        return records


event_bus = InMemoryEventBus()


def publish_replay_events(events: list[dict], producer: EventProducer | None = None) -> int:
    producer = producer or event_bus
    for event in events:
        producer.send(EXPERIMENT_EVENTS_TOPIC, event)
    return len(events)


def consume_events_to_db(
    db: Session,
    consumer: EventConsumer | None = None,
    max_records: int = 100,
) -> int:
    consumer = consumer or event_bus
    records = consumer.poll(EXPERIMENT_EVENTS_TOPIC, max_records=max_records)
    db.add_all(Event(**record) for record in records)
    db.commit()
    return len(records)


def streaming_status() -> StreamingStatus:
    return StreamingStatus(
        mode="in_memory_test_bus",
        topic=EXPERIMENT_EVENTS_TOPIC,
        queued_events=event_bus.queued(EXPERIMENT_EVENTS_TOPIC),
    )
