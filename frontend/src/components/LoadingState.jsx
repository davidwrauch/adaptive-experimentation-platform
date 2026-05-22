import React from "react";

const capabilities = [
  "Contextual bandits",
  "Bayesian experimentation",
  "OPE",
  "Causal uplift",
  "Governance",
  "Live replay",
];

const skeletonKpis = ["Traffic", "Live status", "Short-term winner", "Health"];
const skeletonPanels = ["Policy performance", "Risk monitoring", "Decision support"];

export default function LoadingState({ retryCount = 0 }) {
  return (
    <section className="loading-console">
      <div className="loading-intro">
        <div className="loading-pulse" />
        <div>
          <p className="eyebrow">Hosted demo warming up</p>
          <h2>Backend is waking up, retrying...</h2>
          <p className="loading-lede">
            Adaptive Experimentation Platform for lifecycle messaging decisions that balance clicks,
            retention, fatigue, unsubscribe risk, and rollout safety.
          </p>
          <p>
            Hosted demo usually loads in 5-15 seconds. Once awake, interactions should be faster.
          </p>
          <div className="capability-strip" aria-label="Platform capabilities">
            {capabilities.map((capability) => (
              <span key={capability}>{capability}</span>
            ))}
          </div>
          <small>Retry attempt {retryCount + 1} of 4</small>
        </div>
      </div>

      <div className="skeleton-dashboard" aria-label="Dashboard preview loading">
        <div className="skeleton-kpi-grid">
          {skeletonKpis.map((label) => (
            <div className="skeleton-card" key={label}>
              <span>{label}</span>
              <div className="skeleton-line skeleton-line-short" />
              <div className="skeleton-line" />
            </div>
          ))}
        </div>
        <div className="skeleton-panel-grid">
          {skeletonPanels.map((label) => (
            <div className="skeleton-panel" key={label}>
              <span>{label}</span>
              <div className="skeleton-chart">
                <i />
                <i />
                <i />
                <i />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
