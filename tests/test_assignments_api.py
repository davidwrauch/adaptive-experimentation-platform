from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Event
from fastapi.testclient import TestClient


def test_assignment_recommendation_endpoint_returns_explanation_payload():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add(
            Event(
                user_id="u1",
                policy="linucb",
                action="variant_a",
                reward=0.3,
                propensity=0.5,
                context={
                    "engagement_score": 0.7,
                    "fatigue_score": 0.2,
                    "profile_maturity": 0.9,
                    "unsubscribe_risk": 0.08,
                    "prior_touch_count": 4,
                    "days_since_last_touch": 8,
                    "intervention": {"channel": "email", "tone": "supportive"},
                    "outcome": {"long_term_reward": 0.32},
                },
            )
        )
        db.commit()

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        "/assignments/recommend",
        json={
            "user_id": "sample",
            "requested_policy": "linucb",
            "context": {
                "engagement_score": 0.7,
                "fatigue_score": 0.2,
                "profile_maturity": 0.9,
                "unsubscribe_risk": 0.08,
                "prior_touch_count": 5,
                "days_since_last_touch": 9,
            },
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["selected_policy"] == "linucb"
    assert body["route"] in {"AI_assisted", "human_review", "cold_start", "abstain"}
    assert body["selected_intervention"]
    assert body["evidence_summary"]
    assert body["governance_reason"]
