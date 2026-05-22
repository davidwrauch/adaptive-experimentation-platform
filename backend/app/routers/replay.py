from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ReplayStartRequest, ReplayStatusResponse
from app.services.replay_control import pause_replay, replay_status, start_replay

router = APIRouter(prefix="/replay", tags=["replay"])


@router.post("/start", response_model=ReplayStatusResponse)
def start(payload: ReplayStartRequest, db: Session = Depends(get_db)) -> dict:
    start_replay(
        db,
        source=payload.source,
        batch_size=payload.batch_size,
        replay_speed_seconds=payload.replay_speed_seconds,
    )
    return replay_status(db)


@router.post("/pause", response_model=ReplayStatusResponse)
def pause(db: Session = Depends(get_db)) -> dict:
    pause_replay()
    return replay_status(db)


@router.get("/status", response_model=ReplayStatusResponse)
def status(db: Session = Depends(get_db)) -> dict:
    return replay_status(db)
