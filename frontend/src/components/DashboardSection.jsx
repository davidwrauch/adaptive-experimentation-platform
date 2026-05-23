import React from "react";
import ResearchPopover from "./ResearchPopover";

export default function DashboardSection({ title, description, audience, researchKey, children }) {
  return (
    <section className="dashboard-section" aria-label={title}>
      <div className="dashboard-section-heading">
        <div className="section-heading compact-heading">
          <p className="eyebrow">{title}</p>
          <ResearchPopover referenceKey={researchKey} />
        </div>
        <p>{description}</p>
        {audience && <small>{audience}</small>}
      </div>
      <div className="dashboard-section-content">{children}</div>
    </section>
  );
}
