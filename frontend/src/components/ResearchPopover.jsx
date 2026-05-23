import React, { useCallback, useEffect, useRef, useState } from "react";
import { researchReferences } from "../researchReferences";

const VIEWPORT_MARGIN = 16;
const DESKTOP_WIDTH = 380;

export default function ResearchPopover({ referenceKey }) {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ left: VIEWPORT_MARGIN, top: VIEWPORT_MARGIN, width: DESKTOP_WIDTH });
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);
  const reference = researchReferences[referenceKey];

  const updatePosition = useCallback(() => {
    const trigger = triggerRef.current;
    if (!trigger || typeof window === "undefined") return;

    const rect = trigger.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const width = Math.min(DESKTOP_WIDTH, viewportWidth - VIEWPORT_MARGIN * 2);
    const measuredHeight = popoverRef.current?.offsetHeight ?? 220;
    const availableBelow = viewportHeight - rect.bottom - VIEWPORT_MARGIN;
    const availableAbove = rect.top - VIEWPORT_MARGIN;
    const openAbove = availableBelow < measuredHeight && availableAbove > availableBelow;
    const preferredLeft = rect.left + rect.width / 2 - width / 2;
    const maxLeft = viewportWidth - width - VIEWPORT_MARGIN;
    const left = clamp(preferredLeft, VIEWPORT_MARGIN, maxLeft);
    const maxTop = viewportHeight - VIEWPORT_MARGIN - Math.min(measuredHeight, viewportHeight - VIEWPORT_MARGIN * 2);
    const preferredTop = openAbove ? rect.top - measuredHeight - 8 : rect.bottom + 8;
    const top = clamp(preferredTop, VIEWPORT_MARGIN, maxTop);

    setPosition({ left, top, width });
  }, []);

  useEffect(() => {
    if (!isOpen) return undefined;
    updatePosition();

    function handlePointerDown(event) {
      if (
        triggerRef.current?.contains(event.target) ||
        popoverRef.current?.contains(event.target)
      ) {
        return;
      }
      setIsOpen(false);
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, updatePosition]);

  if (!reference) return null;

  return (
    <span className="research-popover">
      <button
        aria-expanded={isOpen}
        className="research-badge"
        onClick={() => setIsOpen((value) => !value)}
        ref={triggerRef}
        type="button"
      >
        Research
      </button>
      {isOpen && (
        <span
          className="research-card"
          ref={popoverRef}
          role="dialog"
          aria-label={`Research provenance: ${reference.title}`}
          style={{ left: `${position.left}px`, top: `${position.top}px`, width: `${position.width}px` }}
        >
          <strong>{reference.title}</strong>
          <span>Source: {reference.source}</span>
          <p>Why it matters: {reference.why}</p>
          <a href={reference.url} target="_blank" rel="noreferrer">Open reference</a>
        </span>
      )}
    </span>
  );
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}
