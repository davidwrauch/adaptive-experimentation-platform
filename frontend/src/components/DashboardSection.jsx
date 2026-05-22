import React from "react";

export default function DashboardSection({ title, description, children }) {
  return (
    <section className="dashboard-section" aria-label={title}>
      <div className="dashboard-section-heading">
        <p className="eyebrow">{title}</p>
        <p>{description}</p>
      </div>
      <div className="dashboard-section-content">{children}</div>
    </section>
  );
}
