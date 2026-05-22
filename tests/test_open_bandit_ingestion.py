from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Event
from app.services.open_bandit import iter_open_bandit_events, map_open_bandit_row
from app.services.replay_engine import replay_to_db


def test_open_bandit_row_mapping_preserves_logged_bandit_fields():
    payload = map_open_bandit_row(
        {
            "item_id": "sku-123",
            "click": "1",
            "propensity_score": "0.25",
            "behavior_policy": "bts",
            "timestamp": "2020-01-01 00:00:00",
            "user_feature_0": "0.7",
        },
        replay_order=3,
    )

    assert payload["action"] == "sku-123"
    assert payload["reward"] == 1.0
    assert payload["policy"] == "bts"
    assert payload["propensity"] == 0.25
    assert payload["context"]["source"] == "open_bandit"
    assert payload["context"]["logged_policy"] == "bts"
    assert payload["context"]["replay_order"] == 3
    assert payload["context"]["outcome"]["long_term_reward"] >= 0.0


def test_open_bandit_iterator_reads_csv(tmp_path: Path):
    csv_path = tmp_path / "obd.csv"
    csv_path.write_text(
        "item_id,click,propensity_score,behavior_policy\n"
        "a,1,0.2,random\n"
        "b,0,0.4,bts\n",
        encoding="utf-8",
    )

    events = list(iter_open_bandit_events(csv_path))

    assert len(events) == 2
    assert events[0]["policy"] == "random"
    assert events[1]["action"] == "b"


def test_replay_source_switch_supports_synthetic_and_open_bandit(tmp_path: Path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    csv_path = tmp_path / "obd.csv"
    csv_path.write_text(
        "item_id,click,propensity_score,behavior_policy\n"
        "a,1,0.2,random\n",
        encoding="utf-8",
    )

    with TestingSessionLocal() as db:
        synthetic_count = replay_to_db(db, n=2, seed=1, source="synthetic")
        open_bandit_count = replay_to_db(
            db,
            n=1,
            source="open_bandit",
            open_bandit_path=str(csv_path),
        )
        stored = db.query(Event).all()

    assert synthetic_count == 2
    assert open_bandit_count == 1
    assert len(stored) == 3
    assert any(event.context.get("source") == "open_bandit" for event in stored)
