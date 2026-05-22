export default function EventStream({ events }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Recent events</h2>
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
