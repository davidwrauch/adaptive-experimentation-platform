from dataclasses import dataclass

from app.services.embedding_retrieval import (
    get_embedding_model,
    retrieve_embedding_evidence,
)
from app.services.evidence_retrieval import retrieve_evidence, summarize_evidence
from app.services.exploration import exploration_budget_for_context
from app.services.governance import GovernanceDecision
from app.services.policy_engine import policy_engine
from app.services.rollout import rollout_store
from app.services.simulation import build_intervention


@dataclass(frozen=True)
class AssignmentRecommendation:
    selected_policy: str
    selected_intervention: dict
    route: str
    confidence: float
    evidence_summary: str
    governance_reason: str


def recommend_assignment(
    events: list,
    user_context: dict,
    requested_policy: str = "linucb",
    embedding_model=None,
    use_embeddings: bool = True,
) -> AssignmentRecommendation:
    selected_policy = _select_policy(events, requested_policy)
    if rollout_store.get(selected_policy).state == "paused":
        selected_policy = "static"
    action, propensity = policy_engine.choose(selected_policy, user_context)
    evidence = retrieve_evidence(events, user_context, selected_policy)
    embedding_evidence = _embedding_evidence(
        events,
        user_context,
        selected_policy,
        embedding_model=embedding_model,
        use_embeddings=use_embeddings,
    )
    if embedding_evidence:
        evidence["embedding_evidence"] = embedding_evidence
    uncertainty_score = _uncertainty_score(evidence, propensity)
    exploration_budget = exploration_budget_for_context(user_context, uncertainty_score)
    evidence["exploration_budget"] = exploration_budget
    governance = _governance_constraint(evidence, uncertainty_score)
    route = _route(user_context, uncertainty_score, governance)
    intervention = _select_intervention(route, selected_policy, action, evidence)
    confidence = _confidence(route, uncertainty_score, user_context)

    return AssignmentRecommendation(
        selected_policy=selected_policy,
        selected_intervention=intervention,
        route=route,
        confidence=confidence,
        evidence_summary=_combined_evidence_summary(evidence),
        governance_reason=governance.reason,
    )


def _select_policy(events: list, requested_policy: str) -> str:
    if not events:
        return "static"
    policy_counts: dict[str, int] = {}
    for event in events:
        policy_counts[event.policy] = policy_counts.get(event.policy, 0) + 1
    return requested_policy if requested_policy in policy_counts else max(policy_counts, key=policy_counts.get)


def _uncertainty_score(evidence: dict, propensity: float) -> float:
    event_count = evidence["historical_policy_performance"]["event_count"]
    segment_count = evidence["similar_user_segment_summary"]["event_count"]
    evidence_gap = max(0.0, 1.0 - min(event_count, 50) / 50)
    segment_gap = max(0.0, 1.0 - min(segment_count, 25) / 25)
    overlap_gap = max(0.0, 0.2 - propensity)
    return round(min(1.0, evidence_gap * 0.45 + segment_gap * 0.35 + overlap_gap), 4)


def _governance_constraint(evidence: dict, uncertainty_score: float) -> GovernanceDecision:
    risk = evidence["current_user_risk_profile"]
    if risk["risk_tier"] == "high":
        return GovernanceDecision("pause", "high unsubscribe or fatigue risk", 0.0)
    if uncertainty_score >= 0.65:
        return GovernanceDecision("human_review", "high assignment uncertainty", 0.0)
    return GovernanceDecision("canary", "deterministic AI-assisted scaffold within guardrails", 0.0)


def _route(context: dict, uncertainty_score: float, governance: GovernanceDecision) -> str:
    profile_maturity = float(context.get("profile_maturity", 0.0))
    unsubscribe_risk = float(context.get("unsubscribe_risk", 0.0))
    prior_touch_count = int(context.get("prior_touch_count", 0))

    if unsubscribe_risk >= 0.35 or governance.status == "pause":
        return "abstain"
    if profile_maturity < 0.5 or prior_touch_count < 2:
        return "cold_start"
    if uncertainty_score >= 0.65 or governance.status == "human_review":
        return "human_review"
    if profile_maturity >= 0.75 and unsubscribe_risk < 0.18:
        return "AI_assisted"
    return "human_review"


def _select_intervention(route: str, policy: str, action: str, evidence: dict) -> dict:
    if route == "abstain":
        return {
            "action": "no_send",
            "channel": "none",
            "tone": "none",
            "cta_aggressiveness": 0.0,
            "topic_family": "none",
            "message_length": 0,
        }
    if route == "cold_start":
        intervention = build_intervention("control", "static")
        return {"action": "control", **intervention}

    top_attributes = evidence["prior_successful_intervention_attributes"]["top_attributes"]
    intervention = build_intervention(action, policy)
    return {
        "action": action,
        **intervention,
        **{key: value for key, value in top_attributes.items() if key in intervention},
    }


def _confidence(route: str, uncertainty_score: float, context: dict) -> float:
    if route == "abstain":
        return 0.0
    maturity = float(context.get("profile_maturity", 0.0))
    risk_penalty = float(context.get("unsubscribe_risk", 0.0)) * 0.5
    confidence = 0.35 + maturity * 0.35 - uncertainty_score * 0.35 - risk_penalty
    if route == "AI_assisted":
        confidence += 0.15
    if route == "human_review":
        confidence -= 0.1
    return round(max(0.0, min(1.0, confidence)), 4)


def _embedding_evidence(
    events: list,
    user_context: dict,
    selected_policy: str,
    embedding_model,
    use_embeddings: bool,
) -> list[dict]:
    if not use_embeddings:
        return []
    model = embedding_model if embedding_model is not None else get_embedding_model()
    if model is None:
        return []
    return retrieve_embedding_evidence(
        events,
        user_context,
        selected_policy,
        top_k=3,
        embedding_model=model,
    )


def _combined_evidence_summary(evidence: dict) -> str:
    summary = summarize_evidence(evidence)
    embedding_evidence = evidence.get("embedding_evidence") or []
    if not embedding_evidence:
        budget = evidence.get("exploration_budget")
        if budget:
            return f"{summary} Exploration budget {budget['budget']} for {budget['segment']}."
        return summary
    top = embedding_evidence[0]
    budget = evidence.get("exploration_budget")
    budget_text = f" Exploration budget {budget['budget']} for {budget['segment']}." if budget else ""
    score = top.get("score", 0.0)
    return (
        f"{summary}{budget_text} Retrieved evidence: similar example with cosine score {score}: "
        f"{top['text']}. This example is considered similar because its segment, policy, "
        "risk, or intervention attributes overlap with the current assignment context."
    )
