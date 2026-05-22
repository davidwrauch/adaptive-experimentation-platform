import React, { useState } from "react";
import { HelpLabel } from "./InfoTooltip";

export default function EventStream({ events }) {
  const [expanded, setExpanded] = useState(false);
  const visibleEvents = expanded ? events.slice(0, 20) : events.slice(0, 8);

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
        A compact audit trail of policy assignments, selected interventions, and observed reward.
        It is intentionally capped so row-level logs do not dominate the operating dashboard.
      </p>
      <div className="event-list">
        {visibleEvents.map((event) => (
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
      {events.length > 8 && (
        <button className="secondary-button event-more" onClick={() => setExpanded((value) => !value)}>
          {expanded ? "Show fewer" : `Show more (${Math.min(events.length, 20) - 8})`}
        </button>
      )}
    </section>
  );
}
