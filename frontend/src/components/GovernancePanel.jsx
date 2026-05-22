import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { governanceExplanation, uncertaintyInsight } from "../interpretations";

export default function GovernancePanel({ metrics }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: off-policy evaluation estimates plus launch guidance. Why: evaluates policies using logged data before risking broader rollout. Good: high value, low uncertainty, healthy overlap. Bad: low overlap, high uncertainty, or risk-heavy wins. Action: deploy, canary, review, or pause.">
            OPE and governance
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Off-policy estimates ask how each policy would have performed using logged traffic.
        Governance labels translate those estimates into launch guidance.
      </p>
      <WhyThisMatters>
        Offline evaluation reduces experimentation risk by separating "looks promising" from
        "safe enough to expose to more users." {uncertaintyInsight(metrics)}
      </WhyThisMatters>

      <div className="governance-grid">
        <div className="governance-row governance-head">
          <span>Policy</span>
          <span>IPS</span>
          <span>SNIPS</span>
          <span>DR</span>
          <span>Uncertainty</span>
          <span>Status</span>
        </div>
        {metrics.policies.map((policy) => (
          <div className="governance-row" key={policy.policy}>
            <strong>{policy.policy}</strong>
            <span>{format(policy.ope?.ips)}</span>
            <span>{format(policy.ope?.snips)}</span>
            <span>{format(policy.ope?.doubly_robust)}</span>
            <span>{format(policy.ope?.uncertainty)}</span>
            <div>
              <span className={`status-pill status-${policy.governance?.status}`}>
                {policy.governance?.status ?? "unknown"}
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
