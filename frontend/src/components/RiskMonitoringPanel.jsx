import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { formatPolicyLabel, riskInsight } from "../interpretations";

export default function RiskMonitoringPanel({ metrics }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: fatigue deltas and unsubscribe-risk exposure by policy. Why: lifecycle messaging can create churn when it over-contacts users. Good: low fatigue and low unsubscribe risk. Bad: rising risk or aggressive policies on tired users. Action: soften cadence, pause variants, or route to review.">
            Fatigue and risk monitoring
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Tracks whether policies are over-contacting users or pushing high-risk profiles toward
        unsubscribe. This is the safety layer for adaptive messaging.
      </p>
      <WhyThisMatters>{riskInsight(metrics)}</WhyThisMatters>

      <div className="risk-grid">
        <div className="risk-row risk-head">
          <span>Policy</span>
          <span>Fatigue delta</span>
          <span>Unsubscribe risk</span>
          <span>Unsubscribe delta</span>
          <span>Segments</span>
        </div>
        {metrics.policies.map((policy) => (
          <div className="risk-row" key={policy.policy}>
            <strong className="policy-label">{formatPolicyLabel(policy.policy)}</strong>
            <span>{format(policy.behavioral?.average_fatigue_delta)}</span>
            <span>{format(policy.behavioral?.average_unsubscribe_risk)}</span>
            <span>{format(policy.behavioral?.average_unsubscribe_risk_delta)}</span>
            <span>{formatSegments(policy.behavioral?.reward_by_segment ?? [])}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function format(value) {
  return Number.isFinite(value) ? value.toFixed(4) : "n/a";
}

function formatSegments(segments) {
  return segments
    .map((segment) => `${segment.segment}: ${segment.average_long_term_reward.toFixed(3)}`)
    .join(" / ");
}
