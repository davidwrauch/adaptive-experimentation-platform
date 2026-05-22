from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Event
from app.services.rollout import RolloutControlStore, rollout_recommendation
from fastapi.testclient import TestClient


def test_rollout_store_caps_and_pause_resume():
    store = RolloutControlStore()

    control = store.update("linucb", traffic_cap=1.5, canary_percentage=0.2)
    assert control.traffic_cap == 1.0
    assert control.canary_percentage == 0.2
    assert store.pause("linucb").state == "paused"
    assert store.resume("linucb").state == "active"


def test_rollout_recommends_rollback_for_critical_alerts():
    events = [
        Event(user_id=f"u{i}", policy="a", action="x", reward=0.1, propensity=0.01, context={"unsubscribe_risk": 0.5})
        for i in range(10)
    ]

    recommendation = rollout_recommendation(events)

    assert recommendation["recommendation"] == "rollback"


def test_policy_control_api_endpoints():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post("/controls/policies/linucb/pause")
    listed = client.get("/controls/policies")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["state"] == "paused"
    assert listed.status_code == 200
    assert "policies" in listed.json()
