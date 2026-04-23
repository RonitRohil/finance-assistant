# FinanceAssistant — Claude Code Project Context

## What this project is
A RAG-based AI finance assistant for Indian stock markets (NSE/BSE) and ETFs. Users can chat with an AI about stocks, portfolio performance, and market news. Built for personal use + family sharing.

## Repo structure
```
finance-assistant/
├── backend/          ← FastAPI (Python 3.11+)
├── frontend/         ← Next.js 14 + TypeScript + Tailwind
├── docs/             ← Architecture docs, study notes, ADRs
├── CLAUDE.md         ← This file
└── docker-compose.yml
```

## Tech stack
- **Backend**: FastAPI + LangChain + ChromaDB + SQLite
- **LLM**: Ollama (mistral:7b) for dev — Claude API for production
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2), runs locally
- **Data**: yfinance (NSE/BSE stocks + ETFs), nsepy, NewsAPI
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Recharts

## LLM switching (critical)
The LLM is controlled by `.env` — never hardcode model names anywhere:
```python
# Always use the factory function, never instantiate LLM directly
from app.core.llm import get_llm
llm = get_llm()
```

## Backend folder structure
```
backend/
├── app/
│   ├── main.py              ← FastAPI app entry point
│   ├── core/
│   │   ├── llm.py           ← LLM factory (Ollama dev / Claude prod switcher)
│   │   ├── embeddings.py    ← Embedding model setup (sentence-transformers)
│   │   ├── vectorstore.py   ← ChromaDB client and helpers
│   │   └── config.py        ← All settings loaded from .env via pydantic-settings
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py      ← POST /api/chat
│   │       ├── stocks.py    ← GET /api/stocks/{ticker}
│   │       ├── portfolio.py ← CRUD /api/portfolio
│   │       └── news.py      ← GET /api/news
│   ├── services/
│   │   ├── rag_service.py   ← RAG chain logic (retrieval + generation)
│   │   ├── stock_service.py ← yfinance wrapper
│   │   ├── news_service.py  ← NewsAPI wrapper
│   │   └── ingest_service.py← Embed and store documents into ChromaDB
│   └── models/
│       ├── database.py      ← SQLAlchemy engine + session
│       └── schemas.py       ← Pydantic request/response models
├── requirements.txt
├── .env.example
└── .env                     ← gitignored, never commit
```

## Key coding rules
1. Always `async def` for FastAPI route handlers
2. Use `get_llm()` factory — never instantiate LLM directly
3. Add metadata `{ticker, date, source, type}` to every ChromaDB document
4. Handle errors gracefully — stock APIs go down, rate limits happen
5. Indian stock tickers use `.NS` suffix: `TCS.NS`, `RELIANCE.NS`, `HDFCBANK.NS`
6. Never commit `.env` — only `.env.example`
7. Windows dev environment — use `venv\Scripts\activate` not `source`

## Environment variables (.env)
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434

ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-haiku-4-5

NEWSAPI_KEY=
ALPHA_VANTAGE_KEY=

CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=sqlite:///./finance.db
```

## Branching
All development on `dev` branch. Push to `main` only for stable milestones.
Never run `git push` — let the user do that.

## Running locally (Windows)
```bash
# Terminal 1 — keep Ollama running
ollama serve

# Terminal 2 — Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# Terminal 3 — Frontend
cd frontend
npm run dev
# App: http://localhost:3000
```

## Current phase
Phase 1 — Foundation. Building: RAG pipeline, stock Q&A, news ingestion, basic portfolio tracking, chat UI.

## Docs
See `docs/architecture/` for all ADRs and `docs/study-notes/` for learning material on RAG, embeddings, and vector databases.
