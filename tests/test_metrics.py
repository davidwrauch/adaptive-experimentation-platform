from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Event
from fastapi.testclient import TestClient


def test_metrics_aggregates_events_by_policy():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add_all(
            [
                Event(user_id="u1", policy="static", action="control", reward=1.0, propensity=0.5, context={}),
                Event(user_id="u2", policy="static", action="variant_a", reward=0.0, propensity=0.5, context={}),
                Event(user_id="u3", policy="linucb", action="variant_b", reward=1.0, propensity=0.33, context={}),
            ]
        )
        db.commit()

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.get("/metrics")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] == 3
    static = next(policy for policy in body["policies"] if policy["policy"] == "static")
    assert static["event_count"] == 2
    assert static["cumulative_reward"] == 1.0
    assert static["assignments"]["control"] == 1
    assert static["ope"]["snips"] >= 0.0
    assert static["governance"]["status"] in {"deploy", "canary", "human_review", "pause"}
    assert static["behavioral"]["cumulative_immediate_reward"] == 1.0
    assert static["behavioral"]["cumulative_long_term_reward"] == 1.0
    assert static["behavioral"]["reward_by_segment"]
    assert "observability" in body
    assert "alerts" in body["observability"]
    assert body["observability"]["checks"]
    assert "streaming" in body
    assert "rollout" in body
    assert "exploration" in body
    assert "bayesian" in body
    assert body["generated_at"] is not None
    assert body["last_event_timestamp"] is not None
    assert body["cache_age_seconds"] >= 0
