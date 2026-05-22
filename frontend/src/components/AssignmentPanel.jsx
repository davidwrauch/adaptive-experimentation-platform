import React, { useState } from "react";
import { recommendAssignment, sampleUserContext } from "../api";

export default function AssignmentPanel() {
  const [recommendation, setRecommendation] = useState(null);
  const [profileKind, setProfileKind] = useState("mature");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const sampleContext = profileKind === "risky" ? highRiskContext() : sampleUserContext();

  async function handleRecommend() {
    try {
      setLoading(true);
      setError("");
      setRecommendation(await recommendAssignment(sampleContext));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function changeProfile(kind) {
    setProfileKind(kind);
    setRecommendation(null);
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>AI-assisted assignment scaffold</h2>
        <div className="button-row">
          <button onClick={() => changeProfile("mature")}>Mature profile</button>
          <button onClick={() => changeProfile("risky")}>High-risk profile</button>
          <button onClick={handleRecommend}>{loading ? "Checking..." : "Recommend"}</button>
        </div>
      </div>
      <p className="panel-copy">
        This deterministic scaffold shows how an AI-assisted decision could be explained without
        calling an external model: retrieve evidence, apply guardrails, choose a route, and explain why.
      </p>

      {error && <div className="alert">{error}</div>}
      <div className="assignment-grid">
        <div>
          <strong>Sample profile</strong>
          <p>{profileDescription(profileKind)}</p>
        </div>
        {recommendation ? (
          <div className="assignment-result">
            <span className={`route-pill route-${recommendation.route}`}>
              {routeLabel(recommendation.route)}
            </span>
            <dl>
              <dt>Recommended policy</dt>
              <dd>{recommendation.selected_policy}</dd>
              <dt>Message choice</dt>
              <dd>{formatIntervention(recommendation.selected_intervention)}</dd>
              <dt>Confidence</dt>
              <dd>{recommendation.confidence.toFixed(4)}</dd>
              <dt>Why this route</dt>
              <dd>{recommendation.evidence_summary}</dd>
              <dt>Guardrail</dt>
              <dd>{recommendation.governance_reason}</dd>
            </dl>
          </div>
        ) : (
          <div className="empty-inline">Run a deterministic recommendation for the sample profile.</div>
        )}
      </div>
    </section>
  );
}

function formatIntervention(intervention) {
  if (intervention.action === "no_send") {
    return "Do not send a message for this profile.";
  }
  return `${intervention.action} via ${intervention.channel}, ${intervention.tone} tone, ${intervention.topic_family} topic`;
}

function highRiskContext() {
  return {
    engagement: 0.38,
    engagement_score: 0.38,
    fatigue_score: 0.82,
    profile_maturity: 0.8,
    unsubscribe_risk: 0.46,
    prior_touch_count: 16,
    days_since_last_touch: 1,
    prior_sessions: 4,
  };
}

function profileDescription(kind) {
  if (kind === "risky") {
    return "High fatigue, high unsubscribe risk, and many prior touches. A reviewer should expect abstain or human review.";
  }
  return "Mature profile, low unsubscribe risk, moderate engagement, and enough history to support assisted routing.";
}

function routeLabel(route) {
  return {
    AI_assisted: "AI-assisted",
    human_review: "Human review",
    cold_start: "Cold start baseline",
    abstain: "Abstain",
  }[route] ?? route;
}
