from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Event
from app.services.demo_seed import seed_production_demo_if_empty


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
