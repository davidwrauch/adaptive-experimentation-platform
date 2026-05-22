from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Event
from app.services.replay_control import pause_replay, replay_state


def make_client_with_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    pause_replay()
    replay_state.total_replayed_events = 0
    return TestClient(app), TestingSessionLocal


def test_replay_start_inserts_synthetic_events_and_updates_status():
    client, TestingSessionLocal = make_client_with_db()

    response = client.post(
        "/replay/start",
        json={"source": "synthetic", "batch_size": 15, "replay_speed_seconds": 3},
    )

    with TestingSessionLocal() as db:
        event_count = db.query(Event).count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["running"] is True
    assert body["source"] == "synthetic"
    assert body["last_batch_added"] == 15
    assert body["total_replayed_events"] == 15
    assert event_count == 15


def test_replay_open_bandit_uses_logged_dataset_shape():
    client, TestingSessionLocal = make_client_with_db()

    response = client.post(
        "/replay/start",
        json={"source": "open_bandit", "batch_size": 8, "replay_speed_seconds": 5},
    )

    with TestingSessionLocal() as db:
        stored = db.query(Event).all()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["last_batch_added"] == 8
    assert any(event.context.get("source") == "open_bandit" for event in stored)
    assert {event.policy for event in stored} <= {"random", "bts"}


def test_replay_pause_transitions_state_without_deleting_events():
    client, TestingSessionLocal = make_client_with_db()
    client.post("/replay/start", json={"source": "synthetic", "batch_size": 5, "replay_speed_seconds": 3})

    response = client.post("/replay/pause")

    with TestingSessionLocal() as db:
        event_count = db.query(Event).count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["running"] is False
    assert response.json()["last_batch_added"] == 0
    assert event_count == 5


def test_replay_status_reports_saved_state():
    client, _ = make_client_with_db()
    client.post("/replay/start", json={"source": "synthetic", "batch_size": 3, "replay_speed_seconds": 9})

    response = client.get("/replay/status")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["running"] is True
    assert response.json()["batch_size"] == 3
    assert response.json()["replay_speed_seconds"] == 9
