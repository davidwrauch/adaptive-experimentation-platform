import React from "react";
import { researchReferences } from "../researchReferences";

export default function ResearchPopover({ referenceKey }) {
  const reference = researchReferences[referenceKey];
  if (!reference) return null;

  return (
    <span className="research-popover">
      <button className="research-badge" type="button">Research</button>
      <span className="research-card" role="dialog" aria-label={`Research provenance: ${reference.title}`}>
        <strong>{reference.title}</strong>
        <span>Source: {reference.source}</span>
        <p>Why it matters: {reference.why}</p>
        <a href={reference.url} target="_blank" rel="noreferrer">Open reference</a>
      </span>
    </span>
  );
}
