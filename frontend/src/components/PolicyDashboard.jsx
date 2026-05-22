import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

const POLICIES = ["static", "epsilon_greedy", "thompson_sampling", "linucb"];

export default function PolicyDashboard({ metrics, onSimulate }) {
  const maxReward = Math.max(1, ...metrics.policies.map((policy) => policy.cumulative_reward));
  const totalEvents = Math.max(1, metrics.total_events);

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: policy-level traffic, assignment mix, and cumulative reward. Why: shows which strategy is producing value. Good: reward grows with balanced traffic and acceptable risk. Bad: one policy dominates traffic without enough evidence. Action: compare with governance and long-term metrics before expanding.">
            Policy performance
          </HelpLabel>
        </h2>
        <div className="button-row">
          {POLICIES.map((policy) => (
            <button key={policy} onClick={() => onSimulate(policy)}>
              Simulate {policy}
            </button>
          ))}
        </div>
      </div>
      <p className="panel-copy">
        Shows how much traffic each policy assigned to each intervention and how much immediate
        reward it collected. This is the short-term view most experimentation dashboards stop at.
      </p>
      <WhyThisMatters>
        Product teams need to see both the business lift and how that lift was generated. A policy
        can win clicks while still creating churn risk or operational instability.
      </WhyThisMatters>

      <div className="chart-stack">
        {metrics.policies.map((policy) => (
          <div className="policy-chart-card" key={policy.policy}>
            <div>
              <strong>{policy.policy}</strong>
              <small>{((policy.event_count / totalEvents) * 100).toFixed(1)}% traffic share</small>
            </div>
            <div className="chart-metric">
              <div className="bar-track tall">
                <div
                  className="bar-fill"
                  style={{ width: `${(policy.cumulative_reward / maxReward) * 100}%` }}
                />
              </div>
              <small>{policy.cumulative_reward.toFixed(2)} cumulative reward</small>
            </div>
            <div className="assignment-chips">{formatAssignments(policy.assignments)}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatAssignments(assignments) {
  const text = Object.entries(assignments)
    .map(([action, count]) => `${action}: ${count}`)
    .join(" / ");
  return text || "No assignments yet";
}
