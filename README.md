# Adaptive Experimentation & AI Decisioning Platform

A production-style portfolio project for adaptive lifecycle messaging. The platform chooses interventions while balancing immediate clicks, long-term retention, user fatigue, and unsubscribe risk.

It demonstrates the operating layer around adaptive decisioning: logged bandit replay, policy learning, off-policy evaluation, governance, observability, rollout controls, constrained AI-assisted explanations, and warehouse-ready metrics models.

## Systems Included

- **Backend:** FastAPI, SQLAlchemy, Postgres event store
- **Dashboard:** React/Vite experiment operations UI
- **Streaming:** Redpanda/Kafka scaffold with direct DB fallback and in-memory test bus
- **Policies:** static A/B, epsilon-greedy, Thompson Sampling, LinUCB-style scoring
- **Simulation:** user state, fatigue, retention, unsubscribe risk, immediate and long-term reward
- **Real data replay:** Open Bandit Dataset row mapping and replay mode
- **Evaluation:** IPS, SNIPS, doubly robust OPE, Bayesian sequential comparison
- **Governance:** deploy/canary/human_review/pause labels, rollout controls, rollback recommendations
- **Observability:** sample ratio mismatch, traffic imbalance, volume drops, reward drift, low overlap, saturation, unsubscribe-risk exposure
- **AI-assisted scaffolds:** deterministic assignment explanations, local embeddings retrieval, constrained messaging generation requiring human review
- **Warehouse layer:** dbt-style staging and mart models for governed metrics

## Demo Scenario

> A lifecycle messaging system is choosing interventions while balancing clicks, retention, fatigue, and unsubscribe risk.

The seeded portfolio demo is shaped to show:

- `epsilon_greedy` wins immediate reward
- `linucb` wins long-term reward
- `thompson_sampling` receives governance review due to low traffic
- observability flags saturation and unsubscribe-risk exposure
- high-risk users route to abstain or human review

## How To Run Locally

Install backend dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
```

Start local infrastructure:

```powershell
docker compose up -d postgres redpanda
```

Run the API:

```powershell
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload
```

Seed the portfolio demo:

```powershell
python scripts/seed_demo_data.py
```

Run replay modes:

```powershell
python scripts/run_replay.py --source synthetic --mode direct --n 500 --seed 11
python scripts/run_replay.py --source synthetic --mode stream --n 500 --seed 11
python scripts/download_open_bandit.py
python scripts/run_replay.py --source open_bandit --open-bandit-path data/raw/open_bandit/<file>.csv --n 1000
```

Start the dashboard:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- Dashboard: `http://localhost:5173`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Tests

```powershell
pytest
```

The test suite uses SQLite and in-memory streaming, so it does not require Postgres or Redpanda.

## Screenshots To Add

The `screenshots/` folder contains placeholders. After running locally, add:

- `01-dashboard-overview.png`: scenario banner, summary cards, observability status
- `02-assignment-and-messaging.png`: assignment explanation and constrained messaging generation
- `03-ope-governance.png`: OPE estimates and governance labels
- `04-rollout-bayesian.png`: rollout controls, exploration budget, Bayesian sequential results
- `05-long-term-risk.png`: short-term vs long-term reward and fatigue/risk monitoring

## Key Concepts

- **Contextual bandits:** adaptive assignment under uncertainty.
- **Long-term reward:** immediate reward adjusted by retention, fatigue, and unsubscribe risk.
- **OPE:** IPS, SNIPS, and doubly robust estimators for logged-policy evaluation.
- **Governance:** policy decisions are routed through launch labels, controls, and review states.
- **Observability:** experiment quality checks identify when data is no longer trustworthy.
- **Exploration budgets:** segment-level limits prevent over-exploration of high-risk users.
- **Bayesian sequential testing:** beta-binomial comparisons produce continue/expand/stop/review guidance.
- **Constrained AI/RAG:** local evidence retrieval and deterministic generation without required external LLM calls.
- **Warehouse metrics:** dbt-style models document event-store to dashboard lineage.

## Documentation

- [Project overview](PROJECT_OVERVIEW.md)
- [Architecture](docs/architecture.md)
- [Demo script](docs/demo_script.md)
- [Portfolio bullets](docs/portfolio_bullets.md)
- [Warehouse metrics layer](dbt/README.md)

## Resume Bullets

- Built a FastAPI, Postgres, Redpanda, and React/Vite adaptive experimentation platform for lifecycle messaging decisioning.
- Implemented logged-bandit replay, contextual policies, OPE, governance, observability, rollout controls, exploration budgets, and Bayesian sequential testing.
- Modeled long-term lifecycle outcomes including fatigue, retention, unsubscribe risk, and delayed reward.
- Added deterministic RAG-style evidence retrieval, AI-assisted assignment explanations, constrained messaging generation, and dbt-style warehouse models.
