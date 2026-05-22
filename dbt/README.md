# Warehouse and Metrics Layer

This folder sketches a dbt-style analytics layer for the Adaptive Experimentation Platform.
It is warehouse-ready SQL, but it is not required for the local FastAPI demo.

## Model Roles

- `stg_events`: extracts event-store fields into typed analytics columns, including policy, action, immediate reward, long-term reward, fatigue, unsubscribe risk, propensity, and timestamp.
- `stg_assignments`: focuses on assignment-level fields and flags low propensity overlap.
- `mart_policy_performance`: policy-level immediate and long-term reward metrics.
- `mart_experiment_health`: policy-level health checks for low overlap, high unsubscribe-risk exposure, saturation, and delayed reward gaps.
- `mart_user_state`: user-level fatigue, risk, touch count, and long-term reward rollups.
- `mart_governance_decisions`: warehouse-side governance labels and reasons.

## Metrics Flow

```text
Postgres event store
  -> stg_events
  -> stg_assignments
  -> mart_policy_performance
  -> mart_experiment_health
  -> mart_user_state
  -> mart_governance_decisions
  -> API / dashboard metrics
```

The application computes metrics directly for local development. In a production warehouse,
these dbt models would provide the governed metrics layer consumed by the API and dashboard.

## Lineage

Raw logged events are the system of record. Staging models normalize JSON event payloads into
stable analytical columns. Mart models aggregate those columns into operational metrics used for
policy evaluation, experiment health, user-state monitoring, and governance decisions.
