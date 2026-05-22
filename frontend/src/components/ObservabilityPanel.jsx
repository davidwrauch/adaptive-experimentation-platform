import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { severityInterpretation } from "../interpretations";

export default function ObservabilityPanel({ observability }) {
  const alerts = observability?.alerts ?? [];
  const healthScore = observability?.health_score ?? 100;
  const critical = alerts.filter((alert) => alert.severity === "critical").length;
  const warning = alerts.filter((alert) => alert.severity === "warning").length;

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: deterministic checks for experiment integrity and operational risk. Why: policy results are not trustworthy if traffic, volume, overlap, or risk exposure are unhealthy. Good: high health score and no critical alerts. Bad: critical checks or repeated warnings. Action: investigate, slow rollout, or pause.">
            Experiment observability
          </HelpLabel>
        </h2>
        <span className={healthScore >= 80 ? "health-score good" : "health-score watch"}>
          Health {healthScore}
        </span>
      </div>
      <p className="panel-copy">
        Monitoring checks catch experiment quality problems before a policy decision becomes
        misleading: traffic imbalance, overlap gaps, reward drift, saturation, and risk exposure.
      </p>
      <WhyThisMatters>
        Integrity monitoring keeps adaptive systems honest. It connects data quality and user-risk
        signals to operational safety before a policy recommendation reaches production traffic.
      </WhyThisMatters>
      <div className="health-visual">
        <div className="health-ring" style={{ "--score": `${healthScore}%` }}>
          <strong>{healthScore}</strong>
          <span>health</span>
        </div>
        <div className="severity-summary">
          <SeverityBar label="critical" count={critical} total={Math.max(1, alerts.length)} />
          <SeverityBar label="warning" count={warning} total={Math.max(1, alerts.length)} />
          <SeverityBar label="stable" count={Math.max(0, (observability?.checks ?? []).length - alerts.length)} total={Math.max(1, observability?.checks?.length ?? 1)} />
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="empty-inline">No active monitoring alerts.</div>
      ) : (
        <div className="alert-list">
          {alerts.map((alert) => (
            <article className="monitor-alert" key={alert.name}>
              <span className={`severity severity-${alert.severity}`}>{alert.severity}</span>
              <div>
                <strong>{formatName(alert.name)}</strong>
                <p>{alert.explanation}</p>
                <small>{alert.recommended_action}</small>
                <small>{severityCopy(alert.severity)}</small>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function SeverityBar({ label, count, total }) {
  const width = Math.min(100, (count / total) * 100);
  return (
    <div className="severity-bar-card">
      <span className={`severity severity-${label === "stable" ? "stable" : label}`}>
        {label} {count}
      </span>
      <span className="mini-track">
        <span className={`mini-fill severity-fill-${label}`} style={{ width: `${width}%` }} />
      </span>
    </div>
  );
}

function severityCopy(severity) {
  const detail = severityInterpretation(severity);
  return `${detail.interpretation} Suggested action: ${detail.action}`;
}

function formatName(name) {
  return name.replaceAll("_", " ");
}
