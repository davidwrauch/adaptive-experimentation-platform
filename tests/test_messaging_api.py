from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient


def test_messaging_generate_endpoint_requires_human_review():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        "/messaging/generate",
        json={
            "user_id": "u1",
            "policy": "linucb",
            "context": {
                "engagement_score": 0.7,
                "fatigue_score": 0.2,
                "profile_maturity": 0.9,
                "unsubscribe_risk": 0.08,
                "prior_touch_count": 4,
                "days_since_last_touch": 8,
            },
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["requires_human_review"] is True
    assert body["retrieved_evidence"]
    assert body["candidate_message_variants"]
