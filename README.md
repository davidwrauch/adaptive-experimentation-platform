# Adaptive Experimentation & AI Decisioning Platform

Northstar is a fictional subscription lifecycle messaging company using adaptive experimentation to choose interventions across onboarding, re-engagement, retention, churn prevention, and renewal. This project models the operating system behind that workflow: contextual bandits choose messages, offline policy evaluation estimates counterfactual performance, uplift modeling separates raw response from incremental value, and governance controls keep rollout decisions sensitive to fatigue, unsubscribe risk, uncertainty, and long-term retention. The result is a demoable FastAPI, Postgres, Redpanda/Kafka scaffold, and React/Vite operating console for responsible adaptive decisioning.

## Architecture / System Overview

- **Replayed event traffic:** synthetic lifecycle messaging traffic plus Open Bandit Dataset-shaped replay for logged actions, rewards, propensities, and context.
- **Adaptive policies:** Static A/B Control, Epsilon Greedy, Thompson Sampling, and LinUCB-style contextual scoring.
- **Event store and metrics:** Postgres-backed event storage with fast incremental `metrics_summary` updates and capped heavy analytics.
- **Off-policy evaluation:** IPS, SNIPS, and doubly robust estimators for asking how alternate policies might have performed on logged traffic.
- **Causal uplift:** treatment/control comparisons, segment CATE, top-decile lift, and incremental reward estimates.
- **Governance layer:** launch posture, guardrails, observability checks, human review routes, abstention, and decision records.
- **Rollout controls:** persisted pause/resume state, traffic caps, canary rollout percentages, exploration budgets, and rollback guidance.
- **Live operations:** streaming scaffold with Redpanda, in-memory test bus, direct DB fallback, live simulation ticks, recent events, and decision tracing.
- **AI-assisted constrained messaging:** deterministic retrieval and local embeddings over approved templates, segment evidence, policy outcomes, and campaign examples. Generated variants require human review and no external LLM is required.

## Dashboard Sections And Why They Exist

The dashboard is organized as an operating console, not a chart gallery. Each section answers a launch or governance question that would come up in a real experimentation review.

### Overview

**Question answered:** What is happening, which strategy appears promising, and is it safe to expand?

The Overview is intentionally PM-first. It introduces the Northstar lifecycle messaging scenario, defines the primary metric, explains the four strategies as a short legend, then separates experiment result from operational recommendation.

**Inspired by:** experimentation scorecards, launch-review summaries, and progressive rollout consoles.

**References:**

- [Uber XP experimentation platform](https://www.uber.com/blog/xp/)
- [Statsig documentation](https://docs.statsig.com/)
- [Optimizely experiment scorecards](https://support.optimizely.com/hc/en-us/articles/34053132157965-Understanding-your-Experiment-Scorecard)

### PM Decision Card

**Question answered:** Did the experiment work well enough to safely expand?

The decision card compresses the executive readout into result, confidence, risk, recommendation, next action, and why. It makes explicit that a policy can be statistically promising while governance still recommends holding expansion.

**Inspired by:** progressive rollout systems, experiment review scorecards, and launch governance.

**References:**

- [LaunchDarkly progressive rollouts](https://launchdarkly.com/docs/home/releases/create-progressive-rollouts)
- [Statsig multiple rollout stages](https://docs.statsig.com/feature-flags/multiple-rollout-stages/)
- [Engineering for a Science-Centric Experimentation Platform at Netflix](https://arxiv.org/abs/1910.03878)

### Experiment Confidence

**Question answered:** How reliable is the result, and what action should the team take?

This section separates the statistical read from the operational action. It shows lift versus baseline, Bayesian probability-best, uncertainty level, statistical posture, and a recommended action.

**Inspired by:** experimentation scorecards, Bayesian decision support, and sequential launch review.

**References:**

- [Optimizely Stats Engine and feature experimentation](https://www.optimizely.com/products/feature-experimentation/)
- [Eppo experiment protocols](https://docs.geteppo.com/experiment-analysis/configuration/protocols/)
- [Netflix science-centric experimentation platform](https://arxiv.org/abs/1910.03878)

### Short-Term vs Long-Term Reward

**Question answered:** Are we optimizing clicks at the expense of retention, fatigue, or unsubscribe risk?

Northstar intentionally creates a realistic tension: Epsilon Greedy can win immediate response while LinUCB wins retention-adjusted long-term value. This prevents the dashboard from treating click-through as the only success signal.

**Inspired by:** product experimentation guardrails, retention metrics, and lifecycle messaging operations.

**References:**

- [DoorDash on balancing velocity and confidence in experimentation](https://careersatdoordash.com/blog/balancing-velocity-and-confidence-in-experimentation/)
- [Optimizely decision-making and guardrail metrics](https://support.optimizely.com/hc/en-us/articles/34053132157965-Understanding-your-Experiment-Scorecard)
- [Uber XP experimentation platform](https://www.uber.com/blog/xp/)

### Bayesian Sequential Results

**Question answered:** Which policy is most likely best right now, and should the experiment continue?

The Bayesian panel uses beta-binomial comparisons for binary rewards, probability-best, uncertainty bands, and stopping guidance. It supports continuous monitoring without pretending early directional evidence is final launch proof.

**Inspired by:** Bayesian A/B testing, sequential experimentation, and probability-of-best decision framing.

**References:**

- [Bayesian estimation of the binomial parameter in sequential experiments](https://journals.sagepub.com/doi/abs/10.1177/09622802231199160)
- [Beta-binomial distribution](https://en.wikipedia.org/wiki/Beta-binomial_distribution)
- [Netflix experimentation platform paper](https://arxiv.org/abs/1910.03878)

### OPE: IPS, SNIPS, And Doubly Robust

**Question answered:** Can we estimate how another policy would have performed using logged traffic?

OPE lets teams evaluate candidate policies before exposing more users. IPS and SNIPS use logged propensities; doubly robust estimation combines propensity weighting with an outcome model to reduce variance when the model is useful.

**Inspired by:** contextual bandit offline evaluation and counterfactual policy learning.

**References:**

- [Doubly Robust Policy Evaluation and Learning](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/double_robust.pdf)
- [Optimal and Adaptive Off-policy Evaluation in Contextual Bandits](https://proceedings.mlr.press/v70/wang17a/wang17a.pdf)
- [Doubly robust off-policy evaluation with shrinkage](https://arxiv.org/abs/1907.09623)

### Incrementality & Uplift

**Question answered:** Did the policy cause incremental value, or did it simply target users who would have responded anyway?

The uplift panel compares treatment and control outcomes, estimates average treatment effect, segment-level CATE, top-decile lift, and incremental reward captured. This is where raw reward is separated from causal value.

**Inspired by:** uplift modeling, heterogeneous treatment effects, and incrementality measurement.

**References:**

- [Survey and benchmarking study of multitreatment uplift modeling](https://link.springer.com/article/10.1007/s10618-019-00670-y)
- [Bridging the gap between uplift modeling and heterogeneous treatment effects](https://journals.sagepub.com/doi/10.1177/10949968221111083)
- [Rubin causal model](https://en.wikipedia.org/wiki/Rubin_causal_model)

### Exploration Budget

**Question answered:** Are we learning enough without over-exposing risky users or segments?

Exploration is useful only if it is governed. The platform tracks segment-level budgets, observed exploration, uncertainty-driven increases, and risk-driven reductions.

**Inspired by:** contextual bandit exploration/exploitation controls and budget pacing systems.

**References:**

- [Vowpal Wabbit contextual bandits](https://vowpalwabbit.org/docs/vowpal_wabbit/python/latest/tutorials/python_Contextual_bandits_and_Vowpal_Wabbit.html)
- [A Contextual-Bandit Approach to Personalized News Article Recommendation](https://arxiv.org/abs/1003.0146)
- [DoorDash budget pacing research](https://arxiv.org/abs/2509.07929)

### Governance

**Question answered:** Is this safe to deploy, expand, hold, route to review, or pause?

Governance turns metrics into operational policy. It considers reward, uncertainty, traffic share, low-overlap risk, fatigue, unsubscribe exposure, and observability alerts before recommending Continue Rollout, Monitor Closely, Hold Expansion, Human Review, or Rollback Recommended.

**Inspired by:** responsible AI governance, human oversight, model cards/system cards, and launch guardrails.

**References:**

- [Microsoft Responsible AI principles and approach](https://www.microsoft.com/en-us/ai/principles-and-approach)
- [OpenAI safety and system cards](https://openai.com/safety/)
- [Microsoft Responsible AI Standard Reference Guide](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/bade/documents/products-and-services/en-us/ai/RAIS-Reference-Guide-v2.pdf)

### Rollout Controls

**Question answered:** How do operators slow, pause, or safely expand a policy?

Rollout controls persist policy state to the backend. Operators can pause/resume, set traffic caps, set canary rollout percentages, and review rollback guidance without redeploying code.

**Inspired by:** feature flags, progressive delivery, kill switches, and staged rollouts.

**References:**

- [LaunchDarkly progressive rollouts](https://launchdarkly.com/docs/home/releases/create-progressive-rollouts)
- [Optimizely Feature Experimentation docs](https://docs.developers.optimizely.com/feature-experimentation/docs)
- [Statsig feature flags and rollout stages](https://docs.statsig.com/feature-flags/multiple-rollout-stages/)

### Decision Trace

**Question answered:** Why did the system choose this intervention for this user context?

Decision Trace follows one adaptive decision end-to-end: user features, eligible interventions, selected policy, selected message, propensity, expected reward, observed reward, fatigue impact, unsubscribe impact, governance checks, and logged outcome.

**Inspired by:** traceability, model cards, accountable AI review, and production decision logging.

**References:**

- [OpenAI practices for governing agentic AI systems](https://openai.com/index/practices-for-governing-agentic-ai-systems)
- [Microsoft Responsible AI governance](https://support.microsoft.com/en-us/topic/what-is-responsible-ai-33fc14be-15ea-4c2c-903b-aa493f5b8d92)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

### Convergence Monitoring

**Question answered:** Is the adaptive system stabilizing, learning, saturating, or becoming volatile?

The convergence panel tracks policy volatility, recommendation stability, reward drift, exploration concentration, arm saturation, and recent change rate. These checks make the dashboard feel like a live adaptive system rather than a static report.

**Inspired by:** ML observability, drift monitoring, and production bandit monitoring.

**References:**

- [Arize ML observability overview](https://arize.com/ml-observability/)
- [Arize model monitoring](https://arize.com/model-monitoring/)
- [Evidently open-source ML observability](https://github.com/evidentlyai/evidently)

### AI-Assisted Messaging

**Question answered:** What evidence supports this intervention recommendation?

The AI and Decision Support tab retrieves approved templates, similar segment evidence, historical campaign outcomes, policy summaries, and risk context. It explains selected and suppressed interventions in product language.

**Inspired by:** retrieval-grounded decision support, evidence cards, and human-in-the-loop AI operations.

**References:**

- [OpenAI practices for governing agentic AI systems](https://openai.com/index/practices-for-governing-agentic-ai-systems)
- [Microsoft Responsible AI Standard](https://www.microsoft.com/en-us/ai/principles-and-approach)
- [Vowpal Wabbit contextual bandits for personalized decisions](https://vowpalwabbit.org/docs/vowpal_wabbit/python/latest/tutorials/python_Contextual_bandits_and_Vowpal_Wabbit.html)

### Constrained Generation

**Question answered:** Can messaging variants be suggested without autonomous deployment?

The constrained generation layer creates candidate copy, CTA, cadence, and length recommendations only from approved templates and retrieved evidence. Every candidate is marked `requires_human_review`; high-risk users route to review or abstain.

**Inspired by:** responsible AI controls, approval workflows, and system-card style safety documentation.

**References:**

- [OpenAI safety practices](https://openai.com/safety/)
- [Microsoft Responsible AI Standard Reference Guide](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/bade/documents/products-and-services/en-us/ai/RAIS-Reference-Guide-v2.pdf)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Research & Industry Lineage

### Contextual Bandits

- [A Contextual-Bandit Approach to Personalized News Article Recommendation](https://arxiv.org/abs/1003.0146)
- [Vowpal Wabbit contextual bandits documentation](https://vowpalwabbit.org/docs/vowpal_wabbit/python/latest/tutorials/python_Contextual_bandits_and_Vowpal_Wabbit.html)
- [Multi-task learning for contextual bandits](https://arxiv.org/abs/1705.08618)

### Off-Policy Evaluation

- [Doubly Robust Policy Evaluation and Learning](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/double_robust.pdf)
- [Optimal and Adaptive Off-policy Evaluation in Contextual Bandits](https://proceedings.mlr.press/v70/wang17a/wang17a.pdf)
- [Doubly robust off-policy evaluation with shrinkage](https://arxiv.org/abs/1907.09623)

### Bayesian Experimentation

- [Bayesian estimation of the binomial parameter in sequential experiments](https://journals.sagepub.com/doi/abs/10.1177/09622802231199160)
- [Beta-binomial distribution](https://en.wikipedia.org/wiki/Beta-binomial_distribution)
- [Optimizely Stats Engine overview](https://www.optimizely.com/products/feature-experimentation/)

### Incrementality And Uplift

- [Survey and benchmarking study of multitreatment uplift modeling](https://link.springer.com/article/10.1007/s10618-019-00670-y)
- [Bridging uplift modeling and heterogeneous treatment effects](https://journals.sagepub.com/doi/10.1177/10949968221111083)
- [Rubin causal model](https://en.wikipedia.org/wiki/Rubin_causal_model)

### Responsible AI

- [Microsoft Responsible AI principles](https://www.microsoft.com/en-us/ai/principles-and-approach)
- [OpenAI safety and system cards](https://openai.com/safety/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

### ML Observability

- [Arize ML observability](https://arize.com/ml-observability/)
- [Arize model monitoring](https://arize.com/model-monitoring/)
- [Evidently AI observability framework](https://github.com/evidentlyai/evidently)

### Progressive Rollout Systems

- [LaunchDarkly progressive rollouts](https://launchdarkly.com/docs/home/releases/create-progressive-rollouts)
- [Statsig multiple rollout stages](https://docs.statsig.com/feature-flags/multiple-rollout-stages/)
- [Optimizely Feature Experimentation](https://docs.developers.optimizely.com/feature-experimentation/docs)

### Industry Experimentation Platforms

- [Uber XP experimentation platform](https://www.uber.com/blog/xp/)
- [Netflix science-centric experimentation platform](https://arxiv.org/abs/1910.03878)
- [DoorDash metrics layer for experimentation](https://careersatdoordash.com/blog/using-metrics-layer-to-standardize-and-scale-experimentation-at-doordash-2/)
- [Eppo experiment protocols](https://docs.geteppo.com/experiment-analysis/configuration/protocols/)

## What Makes This Project Different

Most portfolio projects stop at a simple A/B test or a model-serving demo. This platform models the operational tradeoffs that appear after a policy starts affecting users:

- It separates experimentation results from governance decisions.
- It includes long-term value, fatigue, unsubscribe risk, and delayed reward.
- It treats uncertainty as a first-class launch input, not a footnote.
- It supports OPE before broader exposure, and uplift modeling before claiming causal value.
- It gives operators rollout controls, decision records, and human review pathways.
- It shows why adaptive systems need observability, convergence checks, and exploration budgets.
- It keeps constrained AI messaging under approved evidence and human review instead of autonomous deployment.

## Current Capabilities

- PM-first Overview with scenario framing, strategy legend, primary metric, confidence, and launch posture.
- FastAPI backend with SQLAlchemy models and Postgres event store.
- React/Vite dashboard with cached incremental loading and live simulation controls.
- Static A/B Control, Epsilon Greedy, Thompson Sampling, and LinUCB-style contextual policy engine.
- Synthetic lifecycle messaging simulation with user state, fatigue, retention, unsubscribe risk, immediate reward, delayed reward, and long-term reward.
- Open Bandit Dataset row mapping and replay mode with synthetic behavioral overlay.
- Redpanda/Kafka scaffold with producer, consumer, direct DB fallback, and in-memory test bus.
- Fast `GET /metrics/summary`, capped `GET /metrics/details`, recent events, and live `POST /demo/stream-step`.
- IPS, SNIPS, and doubly robust OPE.
- Bayesian probability-best, uncertainty bands, and stopping recommendations.
- Causal uplift, CATE, top-decile lift, incremental reward, and budget allocation guidance.
- Observability checks for SRM, traffic imbalance, event volume drops, delayed reward gaps, propensity overlap, reward drift, policy saturation, high-risk exposure, and convergence.
- Persisted rollout controls, exploration budgets, policy lifecycle registry, and decision records.
- Decision Trace and System Flow panels showing how adaptive decisions move through the system.
- Local embeddings retrieval using `sentence-transformers` when available, with deterministic fallback.
- Constrained messaging generation from approved templates and retrieved evidence, always requiring human review.
- dbt-style staging and mart models documenting metrics lineage from event store to dashboard.
- Deployment scaffolding for Render, Vercel, and managed Postgres.

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

Seed the demo:

```powershell
python scripts/seed_demo_data.py
python scripts/seed_demo_data.py --mode portfolio
python scripts/seed_demo_data.py --mode portfolio --n 100000
```

Hosted production auto-seeding uses 25,000 events by default when `APP_ENV=production` and the event table is empty. Override it with:

```text
DEMO_SEED_SIZE=25000
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

Run tests:

```powershell
pytest
```

The test suite uses SQLite and in-memory streaming, so it does not require Postgres or Redpanda.

## Deployment

This repo includes:

- `render.yaml` for the FastAPI backend on Render
- `frontend/vercel.json` for the React/Vite frontend on Vercel
- `backend/.env.example`
- `frontend/.env.example`

### Render Backend

- **Service type:** Web Service
- **Runtime:** Python
- **Root directory:** repository root
- **Build command:** `pip install -r backend/requirements.txt`
- **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

Required environment variables:

- `APP_ENV=production`
- `DATABASE_URL=<managed Postgres URL>`
- `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`
- `AUTO_CREATE_TABLES=true`
- `DEMO_SEED_SIZE=25000`
- `ADMIN_RESEED_TOKEN=<long random token>` if using the temporary demo reseed endpoint

### Vercel Frontend

- **Framework preset:** Vite
- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `dist`

Required environment variable:

- `VITE_API_BASE=https://<your-render-service>.onrender.com`

Recommended hosted demo setup:

- Render Starter backend for fewer cold starts
- Vercel free frontend
- Neon free Postgres
- Synthetic replay and deterministic AI/RAG fallbacks
- No required Redpanda broker, large Open Bandit download, hosted vector database, or external LLM

## Documentation

- [Project overview](PROJECT_OVERVIEW.md)
- [Architecture](docs/architecture.md)
- [Deployment guide](docs/deployment.md)
- [Demo script](docs/demo_script.md)
- [Lifecycle messaging scenario](docs/lifecycle_messaging_scenario.md)
- [System topology and decision trace](docs/system_topology_and_decision_trace.md)
- [ML platform lifecycle](docs/ml_platform_lifecycle.md)
- [Warehouse metrics layer](dbt/README.md)
- [Portfolio bullets](docs/portfolio_bullets.md)

## Screenshots To Add

The `screenshots/` folder contains placeholders. After running locally, add:

- `01-dashboard-overview.png`: PM-first Overview, strategy legend, PM Decision Card, and launch posture.
- `02-experimentation.png`: confidence, Bayesian probability-best, OPE, uplift, and exploration budget.
- `03-risk-governance.png`: observability, governance recommendations, rollout controls, and decision log.
- `04-live-operations.png`: live simulation, replay controls, streaming status, system flow, and decision trace.
- `05-ai-decision-support.png`: selected/suppressed intervention, retrieved evidence, and constrained messaging generation.

## Future Work

- Production authentication and operator roles.
- Warehouse integration for scheduled dbt execution against production analytics data.
- Richer causal estimators for heterogeneous effects and sensitivity analysis.
- Real LLM routing behind strict approval, audit, and policy controls.
- Automated policy evaluation pipelines with scheduled backtests and launch review artifacts.
