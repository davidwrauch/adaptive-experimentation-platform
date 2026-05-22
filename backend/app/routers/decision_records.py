from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DecisionRecord
from app.schemas import DecisionRecordCreate, DecisionRecordRead

router = APIRouter(prefix="/decision-records", tags=["decision-records"])


@router.get("", response_model=list[DecisionRecordRead])
def list_decision_records(limit: int = 25, db: Session = Depends(get_db)) -> list[DecisionRecord]:
    safe_limit = max(1, min(limit, 100))
    return db.query(DecisionRecord).order_by(desc(DecisionRecord.timestamp), desc(DecisionRecord.id)).limit(safe_limit).all()


@router.post("", response_model=DecisionRecordRead)
def create_decision_record(payload: DecisionRecordCreate, db: Session = Depends(get_db)) -> DecisionRecord:
    record = DecisionRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
