import React, { useEffect, useState } from "react";
import { fetchUpliftMetrics } from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { formatPolicyLabel } from "../interpretations";

export default function UpliftPanel() {
  const [uplift, setUplift] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchUpliftMetrics().then(setUplift).catch(() => setError("Uplift metrics are warming up."));
  }, []);

  const policies = uplift?.policy_incrementality ?? [];
  const maxIncremental = Math.max(1, ...policies.map((policy) => Math.abs(policy.incremental_reward_captured)));

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: estimates treatment impact compared with counterfactual control outcomes. Why: raw clicks can overstate causal value. Good: positive incremental reward with enough control data. Bad: high raw reward but weak incremental value. Action: fund policies and segments with positive uplift.">
            Incrementality & Uplift
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Raw reward shows what happened. Uplift estimates what changed because a policy intervened,
        using static/control traffic as the counterfactual baseline.
      </p>
      <WhyThisMatters>
        Incrementality prevents teams from over-investing in users who would have clicked anyway.
        It shifts budget toward policies and segments that create additional retention or reward.
      </WhyThisMatters>
      {error && <div className="alert">{error}</div>}
      {uplift && (
        <>
          <div className="metrics-grid compact-metrics">
            <div className="metric-card">
              <span>Raw winner</span>
              <strong className="policy-label">{formatPolicyLabel(uplift.raw_reward_winner)}</strong>
            </div>
            <div className="metric-card">
              <span>Incremental winner</span>
              <strong className="policy-label">{formatPolicyLabel(uplift.incremental_value_winner)}</strong>
            </div>
            <div className="metric-card">
              <span>ATE</span>
              <strong>{uplift.average_treatment_effect.toFixed(4)}</strong>
            </div>
            <div className="metric-card">
              <span>Top-decile lift</span>
              <strong>{uplift.top_decile_lift.toFixed(4)}</strong>
            </div>
          </div>
          <div className="chart-stack">
            {policies.map((policy) => (
              <article className="policy-chart-card" key={policy.policy}>
                <div>
                  <strong className="policy-label">{formatPolicyLabel(policy.policy)}</strong>
                  <small>raw {policy.raw_average_reward.toFixed(4)}</small>
                </div>
                <div className="chart-metric">
                  <div className="bar-track tall">
                    <div
                      className="bar-fill"
                      style={{ width: `${Math.abs(policy.incremental_reward_captured / maxIncremental) * 100}%` }}
                    />
                  </div>
                  <small>{policy.incremental_reward_captured.toFixed(3)} incremental reward</small>
                </div>
                <small>control baseline {policy.counterfactual_control_reward.toFixed(4)}</small>
              </article>
            ))}
          </div>
          <div className="exploration-card-grid">
            {(uplift.segment_cate ?? []).map((segment) => (
              <article className="exploration-card" key={segment.segment}>
                <strong>{segment.segment}</strong>
                <span>CATE {segment.conditional_treatment_effect.toFixed(4)}</span>
                <small>{segment.fallback_used ? "fallback control used" : "segment control available"}</small>
              </article>
            ))}
          </div>
          <small>
            {formatPolicyLabel(uplift.raw_reward_winner)} leads raw reward;{" "}
            {formatPolicyLabel(uplift.incremental_value_winner)} leads estimated incremental value.
          </small>
        </>
      )}
    </section>
  );
}
