import React, { useMemo, useState } from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import ResearchPopover from "./ResearchPopover";
import { convergenceStatus, formatPolicyLabel, launchRecommendation } from "../interpretations";

const interventionMessages = {
  control: "Weekly digest: You have unread updates from creators you follow.",
  variant_a: "Personalized recommendation summary: New recommendations matching your interests are waiting.",
  variant_b: "Urgency reminder: Your saved recommendations may expire soon.",
};

const candidates = [
  "Short reminder",
  "Personalized recommendation summary",
  "Weekly digest",
  "Win-back message",
  "Urgency reminder",
  "Educational onboarding tip",
  "Contextual recommendation",
];

export default function DecisionTracePanel({ events, metrics, uplift }) {
  const [selectedId, setSelectedId] = useState(events?.[0]?.id ?? null);
  const selectedEvent = useMemo(
    () => events.find((event) => event.id === selectedId) ?? events?.[0],
    [events, selectedId],
  );
  const policyMetric = (metrics.policies ?? []).find((policy) => policy.policy === selectedEvent?.policy);
  const context = selectedEvent?.context ?? {};
  const intervention = context.intervention ?? {};
  const outcome = context.outcome ?? {};
  const recommendation = launchRecommendation(metrics, uplift);
  const stability = convergenceStatus(metrics);

  if (!selectedEvent) {
    return (
      <section className="panel">
        <h2>Decision Trace</h2>
        <ResearchPopover referenceKey="trace" />
        <div className="empty-inline">No recent decisions yet. Start live simulation to create traceable events.</div>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Decision Trace follows one adaptive decision from user context through candidate interventions, policy selection, logging, reward feedback, metrics updates, and governance review.">
            Decision Trace
          </HelpLabel>
        </h2>
        <ResearchPopover referenceKey="trace" />
        <span className={`status-pill status-${policyMetric?.governance?.status ?? "canary"}`}>
          {policyMetric?.governance?.status ?? "logged"}
        </span>
      </div>
      <p className="panel-copy">
        This trace shows how one Northstar lifecycle message moves through the adaptive
        experimentation system end-to-end.
      </p>
      <WhyThisMatters>
        Production adaptive systems need explainable decision logs: what the user looked like,
        what was eligible, why one intervention was selected, what was suppressed, and how reward
        feedback changed the operating posture.
      </WhyThisMatters>

      <div className="trace-layout">
        <div className="trace-picker">
          {events.slice(0, 6).map((event) => (
            <button
              className={event.id === selectedEvent.id ? "secondary-button active-trace" : "secondary-button"}
              key={event.id}
              onClick={() => setSelectedId(event.id)}
              type="button"
            >
              {formatPolicyLabel(event.policy)} · {event.user_id}
            </button>
          ))}
        </div>

        <div className="trace-detail">
          <div className="trace-card">
            <span>User/context features</span>
            <dl>
              <dt>Engagement</dt>
              <dd>{formatNumber(context.engagement_score ?? context.engagement)}</dd>
              <dt>Fatigue</dt>
              <dd>{formatNumber(context.fatigue_score)}</dd>
              <dt>Profile maturity</dt>
              <dd>{formatNumber(context.profile_maturity)}</dd>
              <dt>Unsubscribe risk</dt>
              <dd>{formatNumber(context.unsubscribe_risk)}</dd>
              <dt>Prior touches</dt>
              <dd>{context.prior_touch_count ?? "n/a"}</dd>
              <dt>Days since touch</dt>
              <dd>{context.days_since_last_touch ?? "n/a"}</dd>
            </dl>
          </div>

          <div className="trace-card">
            <span>Eligible intervention candidates</span>
            <ul className="plain-list">
              {candidates.map((candidate) => (
                <li key={candidate}>{candidate}</li>
              ))}
            </ul>
          </div>

          <div className="trace-card selected-message-card">
            <span>Selected intervention/message</span>
            <strong>{interventionMessages[selectedEvent.action] ?? selectedEvent.action}</strong>
            <p>{whySelected(selectedEvent.policy)}</p>
            <small>
              {intervention.message_length ?? "n/a"} chars · {intervention.tone ?? "unknown"} tone ·{" "}
              {intervention.topic_family ?? "unknown"} topic · cadence {cadence(intervention)}
            </small>
          </div>

          <div className="trace-card">
            <span>Suppressed alternative</span>
            <strong>High-frequency short reminder</strong>
            <p>Suppressed when fatigue, recent touch count, or unsubscribe probability is elevated.</p>
          </div>

          <div className="trace-card trace-wide">
            <span>Decision and outcome</span>
            <div className="trace-metrics">
              <Metric label="Selected policy" value={formatPolicyLabel(selectedEvent.policy)} />
              <Metric label="Selection probability" value={formatNumber(selectedEvent.propensity)} />
              <Metric label="Expected immediate reward" value={formatNumber(outcome.immediate_reward)} />
              <Metric label="Expected long-term reward" value={formatNumber(outcome.long_term_reward)} />
              <Metric label="Observed reward" value={formatNumber(selectedEvent.reward)} />
              <Metric label="Fatigue impact" value={formatNumber(outcome.fatigue_delta)} />
              <Metric label="Unsubscribe impact" value={formatNumber(outcome.unsubscribe_risk_delta)} />
              <Metric label="Convergence status" value={stability.status} />
            </div>
          </div>

          <div className="trace-card trace-wide">
            <span>Governance checks applied</span>
            <p>
              OPE overlap, reward uncertainty, traffic share, fatigue exposure, unsubscribe risk,
              saturation, and rollout controls are applied before expansion.
            </p>
            <strong>Final recommendation/logged outcome: {recommendation.state}</strong>
            <small>{recommendation.reason}</small>
          </div>
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatNumber(value) {
  if (value === undefined || value === null) return "n/a";
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric.toFixed(3) : String(value);
}

function cadence(intervention) {
  if ((intervention.cta_aggressiveness ?? 0) >= 0.7) return "high-frequency";
  if ((intervention.message_length ?? 0) > 140) return "moderate";
  return "low-pressure";
}

function whySelected(policy) {
  if (policy === "linucb") {
    return "Selected because user context suggests contextual recommendations can improve retention with lower fatigue risk.";
  }
  if (policy === "epsilon_greedy") {
    return "Selected while exploring aggressive short-term response strategies; governance monitors fatigue closely.";
  }
  if (policy === "thompson_sampling") {
    return "Selected because uncertainty-aware exploration is testing a promising intervention arm.";
  }
  return "Selected as the static baseline for causal comparison and experiment calibration.";
}
