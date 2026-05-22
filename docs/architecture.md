# Architecture

## System Flow

```text
Replay / API events
  -> direct Postgres write OR Redpanda topic experiment_events
  -> FastAPI event store
  -> metrics services
  -> React dashboard
```

## Backend Services

- `policy_engine.py`: static A/B, epsilon-greedy, Thompson Sampling, and LinUCB-style policies.
- `simulation.py`: deterministic user-state and long-term reward simulation.
- `replay_engine.py`: synthetic and Open Bandit replay with direct or streaming mode.
- `streaming.py`: Redpanda/Kafka scaffold plus in-memory test bus.
- `ope.py`: IPS, SNIPS, and doubly robust OPE.
- `governance.py`: deploy/canary/human_review/pause labels.
- `monitoring.py`: experiment observability rules.
- `rollout.py`: traffic caps, canary percentages, pause/resume, rollback recommendation.
- `exploration.py`: segment-level exploration budgets and saturation metrics.
- `bayesian.py`: beta-binomial sequential comparison.
- `evidence_retrieval.py` and `embedding_retrieval.py`: deterministic and local-vector evidence retrieval.
- `assignment_orchestrator.py`: safe route selection for assignment explanations.
- `messaging_generation.py`: constrained review-only message generation.

## Data Modes

- Synthetic demo mode creates a clear lifecycle messaging portfolio story.
- Open Bandit Dataset mode maps real logged bandit rows into the same event schema and overlays lifecycle outcomes.

## Metrics Lineage

```text
events table
  -> service-level metrics for local demo
  -> dbt staging models
  -> dbt marts
  -> API/dashboard metrics
```

The app computes metrics directly for local development. The `dbt/` folder documents how the same data would flow through a warehouse metrics layer.
