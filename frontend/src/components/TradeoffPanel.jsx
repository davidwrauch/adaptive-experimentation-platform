import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { policyPerformanceInsight } from "../interpretations";

export default function TradeoffPanel({ metrics }) {
  const maxReward = Math.max(
    1,
    ...metrics.policies.map((policy) =>
      Math.max(
        policy.behavioral?.cumulative_immediate_reward ?? 0,
        policy.behavioral?.cumulative_long_term_reward ?? 0,
      ),
    ),
  );

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: immediate clicks compared with delayed value after retention, fatigue, and unsubscribe risk. Why: prevents optimizing for clicks at the expense of customer health. Good: long-term reward rises with manageable fatigue. Bad: immediate reward wins while long-term reward falls. Action: shift traffic toward safer policies.">
            Short-term vs long-term reward
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Compares click-like immediate reward with longer-term value after retention, fatigue,
        and unsubscribe risk are included. The winning policy can change once future impact is counted.
      </p>
      <WhyThisMatters>{policyPerformanceInsight(metrics)}</WhyThisMatters>

      <div className="tradeoff-list">
        {metrics.policies.map((policy) => (
          <div className="tradeoff-card" key={policy.policy}>
            <strong>{policy.policy}</strong>
            <RewardBar
              label="Immediate"
              value={policy.behavioral?.cumulative_immediate_reward ?? 0}
              max={maxReward}
            />
            <RewardBar
              label="Long-term"
              value={policy.behavioral?.cumulative_long_term_reward ?? 0}
              max={maxReward}
            />
          </div>
        ))}
      </div>
    </section>
  );
}

function RewardBar({ label, value, max }) {
  return (
    <div className="reward-bar">
      <span>{label}</span>
      <div className="bar-track tall">
        <div
          className={label === "Immediate" ? "bar-fill" : "bar-fill alt-fill"}
          style={{ width: `${(value / max) * 100}%` }}
        />
      </div>
      <strong>{value.toFixed(2)}</strong>
    </div>
  );
}
