# ML Platform Lifecycle: Causal Decisioning and Governance

## Causal Incrementality

Raw reward is not the same as causal impact. A policy can appear to win because it reaches users
who were already likely to click, retain, or convert. The uplift layer compares treatment outcomes
against static/control traffic and estimates:

- average treatment effect across treated events
- conditional treatment effect by segment
- incremental reward captured by policy
- uplift curve data for prioritizing high-lift traffic

When segment-level control traffic is sparse, the service falls back to the global control baseline.
That keeps the dashboard stable while clearly marking where fallback estimates were used.

## Champion/Challenger Lifecycle

Production personalization systems need versioned policies, not just algorithms. The policy lifecycle
registry tracks candidate, challenger, champion, and archived versions with rollback targets and notes.
This maps to a common production pattern:

- candidates are evaluated offline or in limited traffic
- challengers compete against the champion
- champions receive production traffic
- archived versions remain available for audit and rollback history

## Decision Records

Decision records capture deploy, pause, rollback, human review, and abstain decisions with supporting
evidence and metric snapshots. They make governance accountable by connecting:

- system recommendation
- operator rationale
- policy under review
- metrics snapshot at the time of decision

This is the audit trail that lets experimentation teams explain why a policy changed state.

## Production Mapping

Together, uplift metrics, lifecycle state, and decision records turn the demo from adaptive
experimentation into a causal decisioning platform. The same pattern applies to lifecycle messaging,
recommendations, pricing, ranking, and next-best-action systems where operators need both evidence
and control before automated decisions expand.
