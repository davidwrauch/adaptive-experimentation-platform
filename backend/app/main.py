from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers import admin, assignments, controls, decision_records, demo, events, messaging, metrics, policies, replay
from app.services.demo_seed import seed_production_demo_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_production_demo_if_empty(db)
    yield


app = FastAPI(
    title="Adaptive Experimentation & AI Decisioning Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(policies.router)
app.include_router(metrics.router)
app.include_router(assignments.router)
app.include_router(controls.router)
app.include_router(messaging.router)
app.include_router(admin.router)
app.include_router(demo.router)
app.include_router(replay.router)
app.include_router(decision_records.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": os.getenv("APP_ENV", "local"),
    }
