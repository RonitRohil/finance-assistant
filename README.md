# FinanceAssistant — AI-Powered Personal Finance & Stock Intelligence

> A RAG-based AI assistant for stock analysis, portfolio tracking, and personal finance — built for Indian markets (NSE/BSE) and ETFs.

---

## What this project is

FinanceAssistant is a personal AI tool that lets you ask natural language questions about stocks, your portfolio, market news, and your own spending. It uses **Retrieval-Augmented Generation (RAG)** to ground its answers in real financial data — not hallucinations.

Built for personal use first, then shareable with family.

---

## Folder Structure

```
FinanceAssistant/
├── README.md                        ← You are here
├── docs/
│   ├── architecture/                ← All ADRs (Architecture Decision Records)
│   │   ├── ADR-001-system-overview.md
│   │   ├── ADR-002-tech-stack.md
│   │   ├── ADR-003-vector-database.md
│   │   └── ADR-004-data-sources-apis.md
│   ├── planning/
│   │   └── phases-roadmap.md        ← Phase-by-phase feature plan
│   └── study-notes/                 ← Learning notes as we build
│       ├── 01-rag-fundamentals.md
│       ├── 02-vector-databases.md
│       └── 03-embeddings.md
└── (source code will go here during development)
```

---

## Phases at a Glance

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 1 | RAG foundation, stock Q&A, news ingestion, basic portfolio | 🔨 Planning |
| Phase 2 | Portfolio tracking, personal finance, spending insights | ⏳ Upcoming |
| Phase 3 | AI agents, alerts, cloud deployment, multi-user | ⏳ Future |

---

## Key Decisions Made

- **Backend**: FastAPI (Python) — best AI/ML ecosystem
- **Frontend**: Next.js (React) — full-stack dashboard
- **Vector DB**: ChromaDB (Phase 1) → Qdrant (Phase 2+)
- **LLM**: Claude API (Anthropic)
- **Embeddings**: sentence-transformers (free, local)
- **Data**: yfinance + nsepy + NewsAPI (free tier)

See `docs/architecture/` for full reasoning behind every decision.

---

## How to Use These Docs

- Start with `docs/architecture/ADR-001-system-overview.md` for the big picture
- Read `docs/planning/phases-roadmap.md` for what to build and when
- Study `docs/study-notes/` when learning a new concept before implementing it
- Every time a decision changes, update the relevant ADR

---

*Last updated: April 2026*
