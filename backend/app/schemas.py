from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    user_id: str
    policy: str
    action: str
    reward: float = 0.0
    propensity: float = Field(default=1.0, gt=0.0, le=1.0)
    context: dict[str, Any] = Field(default_factory=dict)


class EventRead(EventCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionRequest(BaseModel):
    policy: str = "epsilon_greedy"
    user_id: str = "demo-user"
    context: dict[str, float] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=lambda: ["control", "variant_a", "variant_b"])


class DecisionResponse(BaseModel):
    policy: str
    action: str
    propensity: float


class AssignmentRequest(BaseModel):
    user_id: str = "sample-user"
    requested_policy: str = "linucb"
    context: dict[str, Any] = Field(default_factory=dict)


class AssignmentResponse(BaseModel):
    selected_policy: str
    selected_intervention: dict[str, Any]
    route: str
    confidence: float
    evidence_summary: str
    governance_reason: str


class PolicyControlUpdate(BaseModel):
    traffic_cap: float | None = Field(default=None, ge=0.0, le=1.0)
    canary_percentage: float | None = Field(default=None, ge=0.0, le=1.0)


class AdminReseedRequest(BaseModel):
    token: str | None = None


class StreamStepRequest(BaseModel):
    batch_size: int = Field(default=25, ge=1)


class StreamStepResponse(BaseModel):
    event_count_added: int
    total_events: int
    latest_timestamp: datetime | None
    policy_counts_added: dict[str, int]


class ReplayStartRequest(BaseModel):
    source: str = Field(default="synthetic", pattern="^(synthetic|open_bandit)$")
    batch_size: int = Field(default=25, ge=1)
    replay_speed_seconds: int = Field(default=7, ge=1, le=60)


class ReplayStatusResponse(BaseModel):
    running: bool
    source: str
    batch_size: int
    replay_speed_seconds: int
    total_replayed_events: int
    last_batch_added: int
    latest_timestamp: datetime | None = None
    message: str


class MessagingGenerationRequest(BaseModel):
    user_id: str = "sample-user"
    policy: str = "linucb"
    context: dict[str, Any] = Field(default_factory=dict)


class MessagingGenerationResponse(BaseModel):
    retrieved_evidence: dict[str, Any]
    candidate_message_variants: list[dict[str, Any]]
    cta_variants: list[str]
    cadence_recommendation: str
    message_length_recommendation: str
    governance_status: str
    requires_human_review: bool
    rationale: str


class OpeMetric(BaseModel):
    ips: float
    snips: float
    doubly_robust: float
    uncertainty: float
    effective_sample_size: float
    low_overlap_risk: bool


class GovernanceMetric(BaseModel):
    status: str
    reason: str
    traffic_share: float


class SegmentRewardMetric(BaseModel):
    segment: str
    event_count: int
    average_immediate_reward: float
    average_long_term_reward: float


class BehavioralMetric(BaseModel):
    cumulative_immediate_reward: float
    cumulative_long_term_reward: float
    average_immediate_reward: float
    average_long_term_reward: float
    average_fatigue_delta: float
    average_unsubscribe_risk: float
    average_unsubscribe_risk_delta: float
    reward_by_segment: list[SegmentRewardMetric]


class ObservabilityCheck(BaseModel):
    name: str
    severity: str
    passed: bool
    value: float
    threshold: float
    explanation: str
    recommended_action: str


class ObservabilityMetric(BaseModel):
    alerts: list[ObservabilityCheck]
    health_score: int
    checks: list[ObservabilityCheck]


class PolicyMetric(BaseModel):
    policy: str
    event_count: int
    cumulative_reward: float
    average_reward: float
    assignments: dict[str, int]
    ope: OpeMetric | None = None
    governance: GovernanceMetric | None = None
    behavioral: BehavioralMetric | None = None


class MetricsResponse(BaseModel):
    total_events: int
    policies: list[PolicyMetric]
    latest_timestamp: datetime | None = None
    observability: ObservabilityMetric | None = None
    streaming: dict[str, Any] | None = None
    rollout: dict[str, Any] | None = None
    exploration: dict[str, Any] | None = None
    bayesian: dict[str, Any] | None = None
