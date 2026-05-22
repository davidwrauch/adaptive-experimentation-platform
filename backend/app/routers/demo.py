from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StreamStepRequest, StreamStepResponse
from app.services.demo_seed import build_demo_events
from app.services.metrics_summary import latest_event_timestamp, total_events_from_summary, update_metrics_summary

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/stream-step", response_model=StreamStepResponse)
def stream_step(payload: StreamStepRequest | None = None, db: Session = Depends(get_db)) -> StreamStepResponse:
    batch_size = payload.batch_size if payload else 25
    batch_size = max(1, min(batch_size, 250))
    events = build_demo_events(n=batch_size)
    policy_counts = Counter(event.policy for event in events)

    db.add_all(events)
    update_metrics_summary(db, events)
    db.commit()

    return StreamStepResponse(
        event_count_added=len(events),
        total_events=total_events_from_summary(db),
        latest_timestamp=latest_event_timestamp(db),
        policy_counts_added=dict(policy_counts),
    )
