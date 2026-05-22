# Deployment Guide

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
docker compose up -d postgres redpanda
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Render Backend

Use a Render Web Service plus a managed Render Postgres database.

Exact settings:

- **Service type:** Web Service
- **Runtime:** Python
- **Root directory:** repository root
- **Build command:** `pip install -r backend/requirements.txt`
- **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

Required environment variables:

- `APP_ENV=production`
- `DATABASE_URL=<Render managed Postgres external/internal connection string>`
- `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`
- `AUTO_CREATE_TABLES=true`

Optional environment variables:

- `KAFKA_BOOTSTRAP_SERVERS=<broker host:port>`
- `ENABLE_OPTIONAL_LLM_GENERATION=false`
- `OPENAI_API_KEY=<only if optional LLM mode is explicitly enabled>`

## Vercel Frontend

Exact settings:

- **Framework preset:** Vite
- **Root directory:** `frontend`
- **Install command:** `npm install`
- **Build command:** `npm run build`
- **Output directory:** `dist`

Required environment variable:

- `VITE_API_BASE=https://<your-render-service>.onrender.com`

## Lightweight Production Mode

For a public portfolio deployment, use the lightweight path:

- synthetic replay only
- managed Postgres
- no required Redpanda broker
- no required Open Bandit Dataset download
- no required external LLM key

The direct DB replay path and deterministic generation paths remain fully functional.
