import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { formatPolicyLabel, uncertaintyInsight } from "../interpretations";

export default function OpePanel({ metrics }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Can we estimate how policies would perform using logged traffic? OPE uses IPS, SNIPS, and doubly robust estimates to compare policies before risking broader rollout.">
            Off-policy evaluation
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        OPE estimates how each policy would have performed using logged traffic. It supports
        analysis, but does not decide whether a policy is safe to expand.
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
          <span>Overlap</span>
        </div>
        {metrics.policies.map((policy) => (
          <div className="governance-row" key={policy.policy}>
            <strong className="policy-label">{formatPolicyLabel(policy.policy)}</strong>
            <span>{format(policy.ope?.ips)}</span>
            <span>{format(policy.ope?.snips)}</span>
            <span>{format(policy.ope?.doubly_robust)}</span>
            <span>{format(policy.ope?.uncertainty)}</span>
            <span>{policy.ope?.low_overlap_risk ? "Low overlap" : "Healthy"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function format(value) {
  return Number.isFinite(value) ? value.toFixed(4) : "n/a";
}
