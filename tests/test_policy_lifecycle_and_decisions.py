from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import DecisionRecord, PolicyVersion


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


def test_create_policy_version_api():
    client, TestingSessionLocal = make_client_with_db()

    response = client.post(
        "/policies/versions",
        json={"policy_name": "linucb", "version": "v1", "status": "candidate", "notes": "first"},
    )

    with TestingSessionLocal() as db:
        count = db.query(PolicyVersion).count()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["policy_name"] == "linucb"
    assert count == 1


def test_promote_candidate_sets_champion():
    client, _ = make_client_with_db()
    client.post("/policies/versions", json={"policy_name": "linucb", "version": "v1", "status": "candidate"})

    response = client.post("/policies/promote", json={"policy_name": "linucb", "version": "v1"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "champion"
    assert response.json()["deployed_at"] is not None


def test_rollback_champion_uses_target_version():
    client, _ = make_client_with_db()
    client.post("/policies/versions", json={"policy_name": "linucb", "version": "v1", "status": "candidate"})
    client.post(
        "/policies/versions",
        json={"policy_name": "linucb", "version": "v2", "status": "champion", "rollback_target": "v1"},
    )

    response = client.post("/policies/rollback", json={"policy_name": "linucb"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["version"] == "v1"
    assert response.json()["status"] == "champion"


def test_create_decision_record_includes_metrics_snapshot():
    client, TestingSessionLocal = make_client_with_db()
    payload = {
        "decision_type": "human_review",
        "policy": "linucb",
        "evidence_summary": "high uncertainty",
        "metrics_snapshot": {"total_events": 100, "health_score": 72},
        "operator_reason": "needs PM review",
        "system_recommendation": "review",
    }

    response = client.post("/decision-records", json=payload)
    list_response = client.get("/decision-records")

    with TestingSessionLocal() as db:
        record = db.query(DecisionRecord).first()

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert list_response.status_code == 200
    assert record.metrics_snapshot["health_score"] == 72
    assert list_response.json()[0]["metrics_snapshot"]["total_events"] == 100
