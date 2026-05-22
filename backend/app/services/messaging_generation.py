import os
from dataclasses import dataclass

from app.services.evidence_retrieval import retrieve_evidence, summarize_evidence
from app.services.simulation import segment_for_context


@dataclass(frozen=True)
class MessagingGeneration:
    retrieved_evidence: dict
    candidate_message_variants: list[dict]
    cta_variants: list[str]
    cadence_recommendation: str
    message_length_recommendation: str
    governance_status: str
    requires_human_review: bool
    rationale: str


def generate_messaging(
    events: list,
    user_context: dict,
    policy: str = "linucb",
) -> MessagingGeneration:
    evidence = retrieve_evidence(events, user_context, policy)
    risk_profile = evidence["current_user_risk_profile"]
    governance_status = _governance_status(risk_profile)
    templates = evidence["approved_message_templates"]
    selected_templates = _template_candidates(templates, risk_profile)

    if _external_llm_enabled():
        # Placeholder seam for future LLM call. The demo intentionally stays deterministic
        # unless the environment explicitly enables an implementation.
        variants = _deterministic_variants(selected_templates, risk_profile)
    else:
        variants = _deterministic_variants(selected_templates, risk_profile)

    return MessagingGeneration(
        retrieved_evidence={
            "similar_segment": evidence["similar_user_segment_summary"],
            "historical_policy": evidence["historical_policy_performance"],
            "successful_interventions": evidence["prior_successful_intervention_attributes"],
            "risk_profile": risk_profile,
            "approved_templates": selected_templates,
            "summary": summarize_evidence(evidence),
        },
        candidate_message_variants=variants,
        cta_variants=_cta_variants(risk_profile),
        cadence_recommendation=_cadence(risk_profile),
        message_length_recommendation=_length(risk_profile),
        governance_status=governance_status,
        requires_human_review=True,
        rationale=_rationale(evidence, governance_status),
    )


def _external_llm_enabled() -> bool:
    return os.getenv("ENABLE_OPTIONAL_LLM_GENERATION", "false").lower() == "true" and bool(
        os.getenv("OPENAI_API_KEY")
    )


def _template_candidates(templates: list[dict], risk_profile: dict) -> list[dict]:
    if risk_profile["risk_tier"] == "high":
        return [template for template in templates if template["cta_aggressiveness"] <= 0.25]
    return templates[:2]


def _deterministic_variants(templates: list[dict], risk_profile: dict) -> list[dict]:
    if risk_profile["risk_tier"] == "high":
        return [
            {
                "template_id": "abstain_no_send",
                "message": "No outbound message recommended for this profile.",
                "source_template_id": templates[0]["template_id"] if templates else "none",
                "requires_human_review": True,
            }
        ]

    variants = []
    for template in templates:
        variants.append(
            {
                "template_id": f"candidate_{template['template_id']}",
                "message": (
                    f"Use a {template['tone']} {template['channel']} message about "
                    f"{template['topic_family']} with a low-pressure next step."
                ),
                "source_template_id": template["template_id"],
                "requires_human_review": True,
            }
        )
    return variants


def _cta_variants(risk_profile: dict) -> list[str]:
    if risk_profile["risk_tier"] == "high":
        return ["Do not send", "Ask a human reviewer before outreach"]
    if risk_profile["risk_tier"] == "medium":
        return ["Learn more", "Save for later"]
    return ["Continue", "See recommended next step", "Learn more"]


def _cadence(risk_profile: dict) -> str:
    if risk_profile["risk_tier"] == "high":
        return "abstain from automated outreach for this cycle"
    if risk_profile["days_since_last_touch"] <= 2:
        return "wait at least 5 days before another touch"
    return "standard lifecycle cadence, no more than one touch this week"


def _length(risk_profile: dict) -> str:
    if risk_profile["risk_tier"] == "high":
        return "no message unless a human reviewer approves"
    if risk_profile["fatigue_score"] >= 0.5:
        return "short message under 90 words"
    return "standard short message under 120 words"


def _governance_status(risk_profile: dict) -> str:
    if risk_profile["risk_tier"] == "high":
        return "abstain_or_human_review"
    return "requires_human_review"


def _rationale(evidence: dict, governance_status: str) -> str:
    segment = segment_for_context(evidence["current_user_risk_profile"])
    return (
        f"Generated only from approved templates and logged evidence for {segment}. "
        f"Governance status is {governance_status}; autonomous deployment is disabled."
    )
