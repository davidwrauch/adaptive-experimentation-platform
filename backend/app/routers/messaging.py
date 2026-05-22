from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import MessagingGenerationRequest, MessagingGenerationResponse
from app.services.messaging_generation import generate_messaging

router = APIRouter(prefix="/messaging", tags=["messaging"])


@router.post("/generate", response_model=MessagingGenerationResponse)
def generate(payload: MessagingGenerationRequest, db: Session = Depends(get_db)) -> dict:
    events = db.query(Event).all()
    generation = generate_messaging(events, payload.context, policy=payload.policy)
    return asdict(generation)
