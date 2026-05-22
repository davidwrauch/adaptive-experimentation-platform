import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import AdminReseedRequest
from app.services.demo_seed import PORTFOLIO_DEMO_SEED_SIZE, build_demo_events

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reseed-demo")
def reseed_demo(
    payload: AdminReseedRequest | None = None,
    db: Session = Depends(get_db),
    x_admin_reseed_token: str | None = Header(default=None),
) -> dict:
    expected_token = os.getenv("ADMIN_RESEED_TOKEN")
    request_token = (payload.token if payload else None) or x_admin_reseed_token
    if not expected_token or request_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid admin reseed token")

    seed_size = int(os.getenv("DEMO_SEED_SIZE", str(PORTFOLIO_DEMO_SEED_SIZE)))
    db.query(Event).delete()
    events = build_demo_events(n=seed_size)
    db.add_all(events)
    db.commit()
    return {
        "status": "ok",
        "event_count": len(events),
        "message": "Temporary demo-only reseed completed.",
    }
