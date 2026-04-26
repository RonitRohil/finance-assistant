# ADR-001: System Overview — FinanceAssistant

**Status:** Accepted  
**Date:** April 2026  
**Deciders:** Ronit Jain  

---

## Context

We want to build a personal AI-powered finance assistant that:

1. Answers questions about Indian stocks (NSE/BSE) and ETFs using real data
2. Tracks a personal portfolio and explains P&L
3. Ingests market news and summarizes sentiment
4. Eventually helps with personal budgeting and spending analysis
5. Can be shared with family members as a beta audience

The primary frustration this solves: today Ronit uses generic AI chatbots (ChatGPT, Claude.ai) to analyse stocks, but those tools have no real-time data, no memory of his portfolio, and no ability to reason over his personal financial history. This project fixes all three.

The target is a **local-first tool** that later moves to the cloud.

---

## Decision

We will build FinanceAssistant as a **RAG-based AI system** with the following high-level architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                       │
│               Next.js dashboard (chat + charts)             │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / REST
┌──────────────────────────▼──────────────────────────────────┐
│                      FASTAPI BACKEND                        │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│   │  RAG Engine │  │  Data Ingest │  │  Finance Tools  │    │
│   │ (LangChain) │  │  (Schedulers)│  │  (yfinance,API) │    │
│   └──────┬──────┘  └──────┬───────┘  └────────┬────────┘    │
└──────────┼────────────────┼────────────────────┼────────────┘
           │                │                    │
┌──────────▼────────────────▼────────────────────▼────────────┐
│                       DATA LAYER                            │
│  ┌─────────────────┐    ┌──────────────────────────────────┐│
│  │  Vector Store   │    │  Relational DB (SQLite → Postgres││
│  │  (ChromaDB)     │    │  portfolio, transactions, users  ││
│  │  embeddings of  │    │  watchlists, alerts              ││
│  │  news, filings, │    └──────────────────────────────────┘│
│  │  earnings docs  │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
           │
┌──────────▼─────────────────────────────────────────────────┐
│                   EXTERNAL DATA SOURCES                    │
│  yfinance │ nsepy │ NewsAPI │ Alpha Vantage │ Broker APIs  │
└────────────────────────────────────────────────────────────┘
```

---

## Core Concept: What is RAG and why are we using it?

**RAG = Retrieval-Augmented Generation**

Instead of asking an LLM a question cold (which leads to hallucination and stale data), RAG works in two steps:

1. **Retrieve**: Search a vector database for documents most relevant to the user's question (e.g., recent earnings reports, news articles about RELIANCE.NS)
2. **Generate**: Feed those retrieved documents as context to the LLM, which then answers the question grounded in real data

This means our AI says "Based on Reliance's Q4 2024 earnings report, which shows revenue of ₹2.3L Cr..." rather than making something up.

---

## Four Pillars of the System

### Pillar 1 — Stock Intelligence (Phase 1)
The user asks: *"Is TCS overvalued right now?"*  
The system: fetches recent price data + retrieves earnings reports from the vector store + asks Claude to synthesize an answer.

### Pillar 2 — News & Sentiment (Phase 1)
The system continuously ingests financial news, embeds it into the vector store, and can answer: *"What's the market sentiment around Nifty 50 this week?"*

### Pillar 3 — Portfolio Tracking (Phase 1–2)
User enters their holdings. System tracks P&L, answers: *"How is my portfolio performing vs Nifty?"*

### Pillar 4 — Personal Finance (Phase 2)
User uploads or connects bank statements. System answers: *"How much did I spend on food this quarter?"* or *"Am I on track to save ₹5L this year?"*

---

## Options Considered

### Option A: Build everything custom (no RAG framework)
**Pros:** Maximum control, deep learning  
**Cons:** Reinventing the wheel — embedding, chunking, retrieval all need to be built from scratch. Takes 3x longer to get to a working product.

### Option B: Use LangChain + ChromaDB + FastAPI (chosen)
**Pros:** Production-grade RAG in days, not weeks. Great documentation. Huge community. Can still customize everything.  
**Cons:** Extra dependency to learn. But the learning is valuable — LangChain is an industry-standard skill.

### Option C: Use a managed service like Vectara or Cohere Embed
**Pros:** Zero infrastructure  
**Cons:** Free tiers are very limited. Locks us into a vendor. No learning value.

---

## Consequences

**What becomes easier:**
- Adding new data sources just means writing a new ingestion script
- Swapping the LLM (Claude → GPT-4 → local model) requires changing one line
- The vector store can grow with new documents without any schema changes

**What becomes harder:**
- We need to manage embedding consistency — if we change the embedding model, we need to re-embed all documents
- Local ChromaDB needs to be backed up manually in Phase 1

**What we'll revisit in Phase 2:**
- Move from SQLite to PostgreSQL
- Move from ChromaDB to Qdrant (for better filtering and production readiness)
- Add user authentication for family access

---

## Action Items

- [x] Define system overview and data flow
- [x] Set up FastAPI project scaffold (Phase 1 dev) — **Sprint 1 ✅ confirmed working on Windows 11**
- [x] Set up ChromaDB locally — **Sprint 1 ✅ `stock_news` collection live, 3 BusinessLine articles embedded**
- [x] Build first ingestion pipeline (NewsAPI → embeddings → ChromaDB) — **Sprint 1 ✅ `/api/news/ingest` working end-to-end**
- [x] Build first RAG chain (query → retrieve → Mistral/Ollama answer) — **Sprint 1 ✅ `/api/chat` returning cited answers with real sources**
- [ ] Build yfinance ingestion pipeline (Nifty 500 bulk ingest) — Sprint 2
- [ ] Add APScheduler for automated daily ingestion — Sprint 2
- [ ] Build minimal Next.js chat UI — Sprint 5
