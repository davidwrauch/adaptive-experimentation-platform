import React from "react";

export default function ObservabilityPanel({ observability }) {
  const alerts = observability?.alerts ?? [];
  const healthScore = observability?.health_score ?? 100;
  const critical = alerts.filter((alert) => alert.severity === "critical").length;
  const warning = alerts.filter((alert) => alert.severity === "warning").length;

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Experiment observability</h2>
        <span className={healthScore >= 80 ? "health-score good" : "health-score watch"}>
          Health {healthScore}
        </span>
      </div>
      <p className="panel-copy">
        Monitoring checks catch experiment quality problems before a policy decision becomes
        misleading: traffic imbalance, overlap gaps, reward drift, saturation, and risk exposure.
      </p>
      <div className="health-visual">
        <div className="health-ring" style={{ "--score": `${healthScore}%` }}>
          <strong>{healthScore}</strong>
          <span>health</span>
        </div>
        <div className="severity-summary">
          <span className="severity severity-critical">critical {critical}</span>
          <span className="severity severity-warning">warning {warning}</span>
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
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function formatName(name) {
  return name.replaceAll("_", " ");
}
