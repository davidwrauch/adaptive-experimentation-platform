import React from "react";

export default function InfoTooltip({ label = "More context", children }) {
  return (
    <span className="tooltip-wrap">
      <button className="info-icon" type="button" aria-label={label}>
        i
      </button>
      <span className="tooltip-card" role="tooltip">
        {children}
      </span>
    </span>
  );
}

export function HelpLabel({ children, help }) {
  return (
    <span className="help-label">
      {children}
      <InfoTooltip>{help}</InfoTooltip>
    </span>
  );
}

export function WhyThisMatters({ children }) {
  return (
    <div className="why-summary">
      <strong>Why this matters</strong>
      <p>{children}</p>
    </div>
  );
}
