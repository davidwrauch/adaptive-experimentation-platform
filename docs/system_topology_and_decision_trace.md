# System Topology and Decision Trace

## Event Lifecycle

Northstar decisions begin with a user context: engagement, fatigue, profile maturity, unsubscribe risk, prior touches, and recency. The system creates eligible lifecycle-message candidates, chooses a policy, selects an intervention, logs the decision, ingests reward feedback, updates metrics summaries, evaluates offline policy value, and applies governance before rollout expansion.

## Decision Logging

Each event stores the selected policy, action, propensity, observed reward, context features, intervention metadata, and simulated outcome fields. This makes one adaptive decision traceable from user state to logged outcome.

## Reward Feedback

Immediate reward approximates engagement or click response. Long-term reward includes delayed value, retention, fatigue, and unsubscribe-risk impact. The platform intentionally separates immediate response from long-term customer value.

## Continual Learning

Recent events feed policy metrics, Bayesian confidence, OPE, uplift, exploration saturation, and observability checks. Live simulation appends small batches so the hosted demo behaves like an operating system without scanning the full event table every refresh.

## Governance Review

Governance checks include uncertainty, traffic share, low propensity overlap, fatigue exposure, unsubscribe risk, saturation, and rollout controls. A policy can be statistically promising while still receiving Hold Expansion because operational guardrails are active.

## Production Adaptive Systems

This mirrors production adaptive systems: a decision service chooses among eligible interventions, an event store logs decisions and outcomes, metrics summarize behavior, evaluation services estimate value and incrementality, and governance systems control rollout blast radius.
