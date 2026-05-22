from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AssignmentRequest, AssignmentResponse
from app.services.assignment_orchestrator import recommend_assignment
from app.services.metrics_summary import recent_events

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/recommend", response_model=AssignmentResponse)
def recommend(payload: AssignmentRequest, db: Session = Depends(get_db)) -> dict:
    events = recent_events(db, limit=500)
    recommendation = recommend_assignment(
        events=events,
        user_context=payload.context,
        requested_policy=payload.requested_policy,
    )
    return asdict(recommendation)
