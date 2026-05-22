import React from "react";

export default function ObservabilityPanel({ observability }) {
  const alerts = observability?.alerts ?? [];
  const healthScore = observability?.health_score ?? 100;

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
