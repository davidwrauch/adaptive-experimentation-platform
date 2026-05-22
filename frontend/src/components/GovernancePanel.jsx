import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { formatPolicyLabel, governanceExplanation, formatGovernanceStatus } from "../interpretations";

export default function GovernancePanel({ metrics }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: rollout safety guidance. Why: evaluates whether policies are safe to expand. Good: high value, low uncertainty, healthy overlap. Bad: low overlap, high uncertainty, or risk-heavy wins. Action: continue rollout, monitor closely, route to human review, or hold expansion.">
            Governance recommendations
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Governance translates reward, uncertainty, traffic share, overlap, fatigue, and unsubscribe
        exposure into rollout guidance.
      </p>
      <WhyThisMatters>
        This panel answers "Is it safe to expand?" A policy can be statistically promising while
        still requiring controlled rollout, human review, or paused expansion.
      </WhyThisMatters>

      <div className="governance-grid">
        <div className="governance-row governance-head">
          <span>Policy</span>
          <span>Traffic share</span>
          <span>Uncertainty</span>
          <span>Overlap</span>
          <span>Average reward</span>
          <span>Status</span>
        </div>
        {metrics.policies.map((policy) => (
          <div className="governance-row" key={policy.policy}>
            <strong className="policy-label">{formatPolicyLabel(policy.policy)}</strong>
            <span>{formatPercent(policy.governance?.traffic_share)}</span>
            <span>{format(policy.ope?.uncertainty)}</span>
            <span>{policy.ope?.low_overlap_risk ? "Low overlap" : "Healthy"}</span>
            <span>{format(policy.average_reward)}</span>
            <div>
              <span className={`status-pill status-${policy.governance?.status}`}>
                {formatGovernanceStatus(policy.governance?.status)}
              </span>
              <small>{policy.governance?.reason}</small>
              <small>{governanceExplanation(policy.governance?.status)}</small>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function format(value) {
  return Number.isFinite(value) ? value.toFixed(4) : "n/a";
}

function formatPercent(value) {
  return Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "n/a";
}
