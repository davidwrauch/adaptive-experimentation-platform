from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Event
from app.services.replay_engine import replay_to_db
from app.services.streaming import InMemoryEventBus, consume_events_to_db, publish_replay_events


def test_in_memory_producer_consumer_writes_to_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    bus = InMemoryEventBus()
    payload = {
        "user_id": "u1",
        "policy": "static",
        "action": "control",
        "reward": 1.0,
        "propensity": 1.0,
        "context": {},
    }

    publish_replay_events([payload], producer=bus)
    with Session() as db:
        count = consume_events_to_db(db, consumer=bus)
        stored = db.query(Event).count()

    assert count == 1
    assert stored == 1


def test_replay_stream_mode_uses_test_bus():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session() as db:
        count = replay_to_db(db, n=3, seed=5, mode="stream")
        stored = db.query(Event).count()

    assert count == 3
    assert stored == 3
