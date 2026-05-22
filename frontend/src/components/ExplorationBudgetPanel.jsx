export default function ExplorationBudgetPanel({ exploration }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Exploration budget</h2>
      </div>
      <p className="panel-copy">
        Exploration should increase when uncertainty is high, but shrink for fatigued or
        unsubscribe-risky users. Saturation flags show where exploration may be overused.
      </p>
      <div className="risk-grid">
        <div className="risk-row risk-head">
          <span>Segment</span>
          <span>Events</span>
          <span>Observed</span>
          <span>Budget</span>
          <span>Status</span>
        </div>
        {(exploration?.segments ?? []).map((segment) => (
          <div className="risk-row" key={segment.segment}>
            <strong>{segment.segment}</strong>
            <span>{segment.event_count}</span>
            <span>{(segment.observed_exploration_share * 100).toFixed(1)}%</span>
            <span>{(segment.budget * 100).toFixed(1)}%</span>
            <span>{segment.saturated ? "saturated" : "within budget"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
