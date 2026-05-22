import React from "react";

const POLICIES = ["static", "epsilon_greedy", "thompson_sampling", "linucb"];

export default function PolicyDashboard({ metrics, onSimulate }) {
  const maxReward = Math.max(1, ...metrics.policies.map((policy) => policy.cumulative_reward));

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Policy performance</h2>
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

      <div className="policy-table">
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
