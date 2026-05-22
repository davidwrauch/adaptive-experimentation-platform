from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Event
from app.services.demo_seed import build_demo_events, seed_production_demo_if_empty


def test_build_demo_events_supports_scaled_portfolio_size():
    events = build_demo_events(n=1_000)

    assert len(events) == 1_000
    assert {event.policy for event in events} == {
        "static",
        "epsilon_greedy",
        "linucb",
        "thompson_sampling",
    }


def test_production_demo_seed_is_disabled_locally(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session() as db:
        inserted = seed_production_demo_if_empty(db)
        count = db.query(Event).count()

    assert inserted == 0
    assert count == 0


def test_production_demo_seed_runs_once_when_empty(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEMO_SEED_SIZE", "400")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session() as db:
        first_insert = seed_production_demo_if_empty(db)
        second_insert = seed_production_demo_if_empty(db)
        count = db.query(Event).count()

    assert first_insert == 400
    assert second_insert == 0
    assert count == 400
