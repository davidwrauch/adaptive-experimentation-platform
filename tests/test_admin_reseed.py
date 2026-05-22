from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Event, MetricsSummary


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


def test_admin_reseed_requires_matching_token(monkeypatch):
    monkeypatch.setenv("ADMIN_RESEED_TOKEN", "secret-token")
    client, _ = make_client_with_db()

    missing_token = client.post("/admin/reseed-demo")
    wrong_token = client.post("/admin/reseed-demo", json={"token": "wrong"})
    app.dependency_overrides.clear()

    assert missing_token.status_code == 403
    assert wrong_token.status_code == 403


def test_admin_reseed_replaces_events_and_returns_count(monkeypatch):
    monkeypatch.setenv("ADMIN_RESEED_TOKEN", "secret-token")
    monkeypatch.setenv("DEMO_SEED_SIZE", "25")
    client, TestingSessionLocal = make_client_with_db()

    with TestingSessionLocal() as db:
        db.add(
            Event(
                user_id="old-user",
                policy="old_policy",
                action="old_action",
                reward=0.0,
                propensity=1.0,
                context={"demo": True},
            )
        )
        db.commit()

    response = client.post(
        "/admin/reseed-demo",
        headers={"X-Admin-Reseed-Token": "secret-token"},
    )

    with TestingSessionLocal() as db:
        event_count = db.query(Event).count()
        old_event_count = db.query(Event).filter(Event.policy == "old_policy").count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["event_count"] == 25
    assert event_count == 25
    assert old_event_count == 0


def test_admin_reseed_accepts_body_token(monkeypatch):
    monkeypatch.setenv("ADMIN_RESEED_TOKEN", "body-token")
    monkeypatch.setenv("DEMO_SEED_SIZE", "10")
    client, TestingSessionLocal = make_client_with_db()

    response = client.post("/admin/reseed-demo", json={"token": "body-token"})

    with TestingSessionLocal() as db:
        event_count = db.query(Event).count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["event_count"] == 10
    assert event_count == 10


def test_admin_reseed_rebuilds_summary_after_existing_rows(monkeypatch):
    monkeypatch.setenv("ADMIN_RESEED_TOKEN", "secret-token")
    monkeypatch.setenv("DEMO_SEED_SIZE", "20")
    client, TestingSessionLocal = make_client_with_db()

    with TestingSessionLocal() as db:
        db.add(
            MetricsSummary(
                policy="static",
                event_count=999,
                cumulative_reward=999.0,
                cumulative_long_term_reward=999.0,
                fatigue_delta_sum=999.0,
                unsubscribe_risk_sum=999.0,
                unsubscribe_risk_delta_sum=999.0,
                assignments={"control": 999},
            )
        )
        db.commit()

    response = client.post("/admin/reseed-demo", json={"token": "secret-token"})

    with TestingSessionLocal() as db:
        summary_rows = db.query(MetricsSummary).all()
        total_summary_events = sum(row.event_count for row in summary_rows)

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["event_count"] == 20
    assert total_summary_events == 20
    assert all(row.event_count < 999 for row in summary_rows)
