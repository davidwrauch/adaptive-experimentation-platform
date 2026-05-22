from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import AssignmentRequest, AssignmentResponse
from app.services.assignment_orchestrator import recommend_assignment

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/recommend", response_model=AssignmentResponse)
def recommend(payload: AssignmentRequest, db: Session = Depends(get_db)) -> dict:
    events = db.query(Event).all()
    recommendation = recommend_assignment(
        events=events,
        user_context=payload.context,
        requested_policy=payload.requested_policy,
    )
    return asdict(recommendation)

