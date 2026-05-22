from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import assignments, controls, events, messaging, metrics, policies


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Adaptive Experimentation & AI Decisioning Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
