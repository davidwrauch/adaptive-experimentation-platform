import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { convergenceStatus } from "../interpretations";

export default function ConvergenceMonitoringPanel({ metrics }) {
  const status = convergenceStatus(metrics);
  const alerts = metrics.observability?.alerts ?? [];
  const policies = metrics.policies ?? [];
  const totalEvents = Math.max(1, metrics.total_events ?? 0);
  const maxTrafficShare = Math.max(0, ...policies.map((policy) => policy.event_count / totalEvents));
  const maxUncertainty = Math.max(0, ...policies.map((policy) => policy.ope?.uncertainty ?? 0));
  const saturatedSegments = (metrics.exploration?.segments ?? []).filter((segment) => segment.saturated).length;

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Convergence monitoring watches whether adaptive decisions are stabilizing or still moving: policy volatility, recommendation stability, reward drift, exploration concentration, arm saturation, and recent change rate.">
            Convergence and instability monitoring
          </HelpLabel>
        </h2>
        <span className={`convergence-badge convergence-${slug(status.status)}`}>{status.status}</span>
      </div>
      <p className="panel-copy">{status.reason}</p>
      <WhyThisMatters>
        Production bandit systems need to know whether learning is healthy. A policy can look good
        on reward but still be too volatile, saturated, or concentrated for launch expansion.
      </WhyThisMatters>
      <div className="convergence-grid">
        <Signal
          label="Policy volatility"
          value={maxUncertainty >= 0.35 ? "Volatile" : "Stable"}
          explanation="Tracks how much policy uncertainty is still moving."
        />
        <Signal
          label="Recommendation stability"
          value={alerts.length ? "Needs Review" : "Stable"}
          explanation="Checks whether active alerts make the recommendation less reliable."
        />
        <Signal
          label="Reward drift"
          value={hasDrift(alerts) ? "Volatile" : "Stable"}
          explanation="Watches for changing reward behavior in recent traffic."
        />
        <Signal
          label="Exploration concentration"
          value={maxTrafficShare >= 0.65 ? "Saturated" : "Learning"}
          explanation="Detects whether exploration is over-concentrated."
        />
        <Signal
          label="Arm/intervention saturation"
          value={saturatedSegments ? "Saturated" : "Stable"}
          explanation="Flags segments or interventions receiving too much exposure."
        />
        <Signal
          label="Recent change rate"
          value={metrics.total_events < 1000 ? "Learning" : "Stable"}
          explanation="Shows whether the system is still collecting enough evidence."
        />
      </div>
    </section>
  );
}

function Signal({ label, value, explanation }) {
  return (
    <div className="convergence-signal">
      <span className="signal-label">{label}</span>
      <strong className={`signal-status signal-${slug(value)}`}>{value}</strong>
      <small>{explanation}</small>
    </div>
  );
}

function hasDrift(alerts) {
  return alerts.some((alert) => String(alert.name).toLowerCase().includes("drift"));
}

function slug(value) {
  return String(value).toLowerCase().replaceAll(" ", "-");
}
