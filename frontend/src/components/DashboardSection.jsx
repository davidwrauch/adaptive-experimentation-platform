import React from "react";

export default function DashboardSection({ title, description, audience, children }) {
  return (
    <section className="dashboard-section" aria-label={title}>
      <div className="dashboard-section-heading">
        <p className="eyebrow">{title}</p>
        <p>{description}</p>
        {audience && <small>{audience}</small>}
      </div>
      <div className="dashboard-section-content">{children}</div>
    </section>
  );
}
