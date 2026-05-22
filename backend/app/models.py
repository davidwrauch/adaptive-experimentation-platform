from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    policy: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    reward: Mapped[float] = mapped_column(Float, default=0.0)
    propensity: Mapped[float] = mapped_column(Float, default=1.0)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class PolicyControlState(Base):
    __tablename__ = "policy_controls"

    policy: Mapped[str] = mapped_column(String(64), primary_key=True)
    traffic_cap: Mapped[float] = mapped_column(Float, default=1.0)
    canary_percentage: Mapped[float] = mapped_column(Float, default=0.25)
    state: Mapped[str] = mapped_column(String(32), default="active")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class MetricsSummary(Base):
    __tablename__ = "metrics_summary"

    policy: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    cumulative_reward: Mapped[float] = mapped_column(Float, default=0.0)
    cumulative_long_term_reward: Mapped[float] = mapped_column(Float, default=0.0)
    fatigue_delta_sum: Mapped[float] = mapped_column(Float, default=0.0)
    unsubscribe_risk_sum: Mapped[float] = mapped_column(Float, default=0.0)
    unsubscribe_risk_delta_sum: Mapped[float] = mapped_column(Float, default=0.0)
    assignments: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
