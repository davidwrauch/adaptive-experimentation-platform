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
          <div className="chart-row" key={policy.policy}>
            <div>
              <strong>{policy.policy}</strong>
              <small>{((policy.event_count / totalEvents) * 100).toFixed(1)}% traffic share</small>
            </div>
            <div>
              <div className="bar-track tall">
                <div
                  className="bar-fill"
                  style={{ width: `${(policy.cumulative_reward / maxReward) * 100}%` }}
                />
              </div>
              <small>{policy.cumulative_reward.toFixed(2)} cumulative reward</small>
            </div>
          </div>
        ))}
      </div>

      <div className="policy-table compact-table">
        <div className="table-row table-head">
          <span>Policy</span>
          <span>Reward</span>
          <span>Assignments</span>
        </div>
        {metrics.policies.map((policy) => (
          <div className="table-row" key={policy.policy}>
            <strong>{policy.policy}</strong>
            <div className="bar-cell">
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${(policy.cumulative_reward / maxReward) * 100}%` }}
                />
              </div>
              <span>{policy.cumulative_reward}</span>
            </div>
            <span>{formatAssignments(policy.assignments)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatAssignments(assignments) {
  return Object.entries(assignments)
    .map(([action, count]) => `${action}: ${count}`)
    .join(" / ");
}
