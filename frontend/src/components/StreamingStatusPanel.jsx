import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

export default function StreamingStatusPanel({ streaming }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: current event transport mode and queue depth. Why: ingestion reliability determines whether dashboard metrics are fresh. Good: known mode with low queue depth. Bad: growing queue or transport errors. Action: drain consumer or use direct DB fallback.">
            Streaming status
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Replay can write directly to Postgres or publish events through the local Redpanda/Kafka
        scaffold. Tests use the in-memory bus so development stays deterministic.
      </p>
      <WhyThisMatters>
        Live operations depend on trustworthy event flow. If data stops arriving, product decisions
        can look stale even when policies are healthy.
      </WhyThisMatters>
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
