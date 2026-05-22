import React from "react";

export default function GovernancePanel({ metrics }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>OPE and governance</h2>
      </div>
      <p className="panel-copy">
        Off-policy estimates ask how each policy would have performed using logged traffic.
        Governance labels translate those estimates into launch guidance.
      </p>

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
