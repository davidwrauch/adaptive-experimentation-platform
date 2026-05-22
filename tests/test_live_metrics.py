from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Event
from app.services.demo_seed import build_demo_events
from app.services.metrics_summary import update_metrics_summary


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
    return TestClient(app), TestingSessionLocal


def test_stream_step_inserts_events_and_returns_lightweight_counts():
    client, TestingSessionLocal = make_client_with_db()

    response = client.post("/demo/stream-step", json={"batch_size": 12})

    with TestingSessionLocal() as db:
        event_count = db.query(Event).count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["event_count_added"] == 12
    assert body["total_events"] == 12
    assert event_count == 12
    assert sum(body["policy_counts_added"].values()) == 12
    assert body["latest_timestamp"] is not None


def test_stream_step_respects_batch_cap():
    client, TestingSessionLocal = make_client_with_db()

    response = client.post("/demo/stream-step", json={"batch_size": 999})

    with TestingSessionLocal() as db:
        event_count = db.query(Event).count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["event_count_added"] == 250
    assert event_count == 250


def test_metrics_summary_handles_large_demo_data_without_full_payload():
    client, TestingSessionLocal = make_client_with_db()
    events = build_demo_events(n=5_000)
    with TestingSessionLocal() as db:
        db.add_all(events)
        update_metrics_summary(db, events)
        db.commit()

    response = client.get("/metrics/summary")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] == 5_000
    assert {policy["policy"] for policy in body["policies"]} == {
        "static",
        "epsilon_greedy",
        "linucb",
        "thompson_sampling",
    }
    assert "observability" in body
    assert "bayesian" in body


def test_recent_events_endpoint_respects_limit():
    client, TestingSessionLocal = make_client_with_db()
    events = build_demo_events(n=20)
    with TestingSessionLocal() as db:
        db.add_all(events)
        update_metrics_summary(db, events)
        db.commit()

    response = client.get("/events/recent?limit=7")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 7


def test_metrics_compatibility_uses_capped_metrics_shape():
    client, TestingSessionLocal = make_client_with_db()
    events = build_demo_events(n=40)
    with TestingSessionLocal() as db:
        db.add_all(events)
        update_metrics_summary(db, events)
        db.commit()

    response = client.get("/metrics")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] == 40
    assert body["policies"][0]["ope"] is not None
    assert "rollout" in body
