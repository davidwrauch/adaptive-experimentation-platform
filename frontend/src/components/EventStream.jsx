import React from "react";
import { HelpLabel } from "./InfoTooltip";

export default function EventStream({ events }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: capped recent assignment and reward events. Why: gives an audit trail without fetching the full event table. Good: fresh timestamps and varied policies. Bad: stale or empty stream. Action: start live simulation or inspect ingestion.">
            Recent events
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        A replayable audit trail of policy assignments, selected interventions, and observed reward.
      </p>
      <div className="event-list">
        {events.map((event) => (
          <article className="event-row" key={event.id}>
            <div>
              <strong>{event.policy}</strong>
              <span>{event.user_id}</span>
            </div>
            <div>
              <span>{event.action}</span>
              <strong>reward {event.reward}</strong>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
