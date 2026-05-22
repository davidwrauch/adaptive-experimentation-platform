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
- **Local embeddings:** optional `sentence-transformers` MiniLM retrieval with deterministic local-vector fallback
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

For lightweight local mode without streaming infrastructure:

```powershell
docker compose up -d postgres
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

The default command keeps the original lightweight 400-event seed for fast local checks. To create
a larger portfolio demo with replayed production-style traffic:

```powershell
python scripts/seed_demo_data.py --mode portfolio
python scripts/seed_demo_data.py --mode portfolio --n 100000
```

Hosted production auto-seeding uses 25,000 events by default when `APP_ENV=production` and the
events table is empty. Override it with:

```text
DEMO_SEED_SIZE=25000
```

For hosted demos, the dashboard is designed to load fast from `GET /metrics/summary`, then request
capped details only when needed. Use `POST /demo/stream-step` to append small synthetic batches over
time instead of reseeding a huge table during a live walkthrough:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri https://<your-render-service>.onrender.com/demo/stream-step `
  -Body '{ "batch_size": 25 }' `
  -ContentType "application/json"
```

Temporary hosted-demo reseed endpoint:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri https://<your-render-service>.onrender.com/admin/reseed-demo `
  -Headers @{ "X-Admin-Reseed-Token" = "<ADMIN_RESEED_TOKEN>" } `
  -Body "{}" `
  -ContentType "application/json"
```

This endpoint is temporary and demo-only. It clears the hosted demo event store and reseeds with
`DEMO_SEED_SIZE` events. Protect it with a long random `ADMIN_RESEED_TOKEN`.

Run replay modes:

```powershell
python scripts/run_replay.py --source synthetic --mode direct --n 500 --seed 11
python scripts/run_replay.py --source synthetic --mode stream --n 500 --seed 11
python scripts/download_open_bandit.py
python scripts/run_replay.py --source open_bandit --open-bandit-path data/raw/open_bandit/<file>.csv --n 1000
```

The dashboard also includes browser-level replay controls. Use synthetic replay for deterministic
lifecycle messaging traffic, or Open Bandit replay for logged recommendation-style actions, rewards,
and propensities. For a real downloaded Open Bandit CSV, set:

```text
OPEN_BANDIT_CSV_PATH=data/raw/open_bandit/<file>.csv
```

If no CSV is configured, the hosted demo uses a tiny built-in Open Bandit-shaped sample so the UI
can demonstrate the replay path without requiring a large dataset download.

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

## Deployment

This repo includes deployment scaffolding for a public portfolio deployment:

- `render.yaml` for the FastAPI backend on Render
- `frontend/vercel.json` for the React/Vite frontend on Vercel
- `backend/.env.example`
- `frontend/.env.example`

### Render Backend Settings

- **Service type:** Web Service
- **Runtime:** Python
- **Root directory:** repository root
- **Build command:** `pip install -r backend/requirements.txt`
- **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

Required backend environment variables:

- `APP_ENV=production`
- `DATABASE_URL=<managed Postgres URL>`
- `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`
- `AUTO_CREATE_TABLES=true`

### Vercel Frontend Settings

- **Framework preset:** Vite
- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `dist`

Required frontend environment variable:

- `VITE_API_BASE=https://<your-render-service>.onrender.com`

### Lightweight Hosted Mode

For public deployment, no large data download or streaming broker is required. Use synthetic replay,
managed Postgres, and deterministic AI/RAG fallbacks. Redpanda, Open Bandit Dataset replay, local
embeddings, and optional external LLM generation remain optional.

Recommended hosted demo setup:

- Render Starter backend for fewer cold starts during portfolio reviews
- Vercel free frontend
- Neon free Postgres
- `DEMO_SEED_SIZE=25000`
- Live simulation enabled from the dashboard, which appends small batches and refreshes summary metrics

See [Deployment Guide](docs/deployment.md) and [Architecture](docs/architecture.md).

## Key Concepts

- **Contextual bandits:** adaptive assignment under uncertainty.
- **Long-term reward:** immediate reward adjusted by retention, fatigue, and unsubscribe risk.
- **OPE:** IPS, SNIPS, and doubly robust estimators for logged-policy evaluation.
- **Governance:** policy decisions are routed through launch labels, controls, and review states.
- **Observability:** experiment quality checks identify when data is no longer trustworthy.
- **Exploration budgets:** segment-level limits prevent over-exploration of high-risk users.
- **Bayesian sequential testing:** beta-binomial comparisons produce continue/expand/stop/review guidance.
- **Constrained AI/RAG:** local evidence retrieval and deterministic generation without required external LLM calls.
- **Local embeddings retrieval:** uses `sentence-transformers` with `paraphrase-MiniLM-L3-v2` when installed, otherwise falls back to deterministic local vectors. No hosted vector database or external LLM is required.
- **Warehouse metrics:** dbt-style models document event-store to dashboard lineage.

## Documentation

- [Project overview](PROJECT_OVERVIEW.md)
- [Architecture](docs/architecture.md)
- [Deployment guide](docs/deployment.md)
- [Demo script](docs/demo_script.md)
- [Portfolio bullets](docs/portfolio_bullets.md)
- [Warehouse metrics layer](dbt/README.md)

## Resume Bullets

- Built a FastAPI, Postgres, Redpanda, and React/Vite adaptive experimentation platform for lifecycle messaging decisioning.
- Implemented logged-bandit replay, contextual policies, OPE, governance, observability, rollout controls, exploration budgets, and Bayesian sequential testing.
- Modeled long-term lifecycle outcomes including fatigue, retention, unsubscribe risk, and delayed reward.
- Added deterministic RAG-style evidence retrieval, AI-assisted assignment explanations, constrained messaging generation, and dbt-style warehouse models.
