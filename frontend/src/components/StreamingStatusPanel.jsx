export default function StreamingStatusPanel({ streaming }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Streaming status</h2>
      </div>
      <p className="panel-copy">
        Replay can write directly to Postgres or publish events through the local Redpanda/Kafka
        scaffold. Tests use the in-memory bus so development stays deterministic.
      </p>
      <div className="compact-grid">
        <span>Mode</span>
        <strong>{streaming?.mode ?? "unknown"}</strong>
        <span>Topic</span>
        <strong>{streaming?.topic ?? "experiment_events"}</strong>
        <span>Queued events</span>
        <strong>{streaming?.queued_events ?? 0}</strong>
      </div>
    </section>
  );
}
