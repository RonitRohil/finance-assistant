# FinanceAssistant

Personal finance assistant. Monorepo with `backend/` (FastAPI + LangChain), `frontend/` (Next.js), and `docs/`.

## Branching
All development happens on `ronit-dev`. The user pushes to `main` themselves — do not run `git push`.

## Backend
- Python 3.11+, FastAPI, LangChain (Anthropic), Chroma, yfinance, APScheduler, SQLAlchemy
- Entry: `backend/app/main.py`
- Config via `backend/.env` (see `.env.example`)

## Frontend
- Next.js (App Router), TypeScript, Tailwind, ESLint, `src/` dir, `@/*` import alias

## Running
`docker-compose up` from the repo root brings up backend (:8000) and frontend (:3000).
