# FinanceAssistant — Phases Roadmap

**Last updated:** April 2026 (v2 — post brainstorming reprioritization)
**Project start:** May 2026 (estimated)
**Solo developer** — ~15–20 hrs/week available alongside job hunting

---

## What Changed in v2 (Brainstorm-Driven Updates)

| Item | Old Priority | New Priority | Reason |
|------|-------------|-------------|--------|
| Watchlist price alerts | Phase 2 | Phase 1 Sprint 4 | Highest daily-use feature, simple to build |
| Expert/Simple conversation mode | Phase 3 | Phase 1 Sprint 4 | Family beta testers need this from day one |
| Indian financial calendar as RAG source | Not planned | Phase 1 Sprint 3 | Static data, huge answer quality boost |
| "Why is this stock moving?" compound query | Not planned | Phase 1 Sprint 4 | Killer demo feature, uses all RAG components |
| Define supported stock universe (Nifty 500) | Not planned | Phase 1 Sprint 2 | Prevent sparse-data hallucinations on mid-caps |
| Docker Compose setup | Phase 1 | Phase 2 | Adds Windows complexity, not needed locally |

---

## Now / Next / Later View

```
NOW (Phase 1 — May–July 2026, 10 weeks, 5 sprints)
  Foundation + killer demo feature working locally

NEXT (Phase 2 — Aug–Oct 2026, 10 weeks)
  Intelligence: personal finance, AI agents, Qdrant migration

LATER (Phase 3 — Nov 2026+, ongoing)
  Cloud deployment, real-time data, mutual funds, voice
```

---

## Phase 1 — Foundation ("It works and wows")

**Goal**: A working local app where you can ask "Why is TCS falling today?" and get a grounded, cited answer. Family can use it. You use it daily.

**Definition of Done**: The "Why is this stock moving?" feature works end-to-end with real data and citations. Expert/Simple mode toggle works. At least one family member has given feedback.

**Stock universe**: Nifty 500 only in Phase 1. If a user asks about a stock outside Nifty 500, the system clearly says "I have limited data on this stock" rather than hallucinating.

### Sprint 1 — Scaffold & Hello World RAG (Weeks 1–2)
→ See `sprint-plans.md` for full detail

Key deliverables:
- FastAPI backend running, health check works
- Ollama (mistral) connected and responding
- ChromaDB set up with first collection
- "Hello World" RAG: one document, one question, one correct answer
- Next.js frontend shell running at localhost:3000

### Sprint 2 — Data Pipeline (Weeks 3–4)
Key deliverables:
- yfinance ingestion for Nifty 500 stocks
- sentence-transformers embeddings working
- ChromaDB populated with 500 stock summaries
- NewsAPI ingestion + APScheduler running
- Supported stock list documented (Nifty 500 only)
- Sparse data detection: warn when < 3 documents retrieved

### Sprint 3 — RAG Chain + Indian Calendar (Weeks 5–6)
Key deliverables:
- Full LangChain RetrievalQA chain working
- Indian financial calendar embedded as RAG source (RBI dates, F&O expiry, earnings season, budget)
- `/api/chat` endpoint responding with citations
- 20 test questions verified (pass/fail documented)

### Sprint 4 — Portfolio + Power Features (Weeks 7–8)
Key deliverables:
- Portfolio CRUD (add/edit/delete holdings)
- "Why is this stock moving today?" compound query working
- Expert vs Simple conversation mode toggle
- Watchlist with email alerts when price crosses target
- Portfolio context injected into every RAG response

### Sprint 5 — Chat UI + Polish + Beta (Weeks 9–10)
Key deliverables:
- Full Next.js chat UI with message history + source citations
- Stock dashboard page (price chart + key metrics)
- Portfolio overview page (P&L table + allocation pie)
- Family beta: 3 users, 5 feedback items collected
- Demo video recorded for portfolio

---

## Phase 2 — Intelligence ("It's smart")

**Goal**: Proactive insights, personal finance understanding, and a smarter agent that decides what tools to call.

**Trigger**: Phase 1 complete, app used daily, at least 1 family member using it.

### M2.1 — Personal Finance Module (Weeks 1–3)
- PDF upload for bank/credit card statements (HDFC, SBI, ICICI formats)
- Transaction categorization via LLM (food, rent, investment, EMI)
- Spending dashboard: monthly breakdown, category trends
- Savings goal tracker: "Am I on track to save ₹5L this year?"
- RAG over personal spending: "How much on food vs investing last quarter?"

### M2.2 — Mutual Funds Module (Weeks 2–4) ← moved up from Phase 3
- AMFI NAV data ingestion (free, updated daily)
- Track SIP investments and performance
- Fund vs benchmark comparison (vs Nifty 50, category average)
- "Which of my mutual funds is underperforming?" — RAG answer
- Mutual funds likely more relevant to family than direct stocks

### M2.3 — AI Agents (Weeks 3–5)
- Upgrade from RetrievalQA to LangChain Agent with tools:
  - `get_stock_price(ticker)` — live price from yfinance
  - `get_portfolio_performance()` — real-time P&L
  - `search_news(query, date_range)` — filtered ChromaDB search
  - `compare_stocks(ticker1, ticker2)` — side-by-side fundamentals
  - `get_fundamentals(ticker)` — P/E, revenue, debt ratios
  - `check_calendar(date_range)` — upcoming RBI/results events
- Agent decides which tools to call; multi-step reasoning enabled
- Demo: "Should I add TCS or Wipro given my current tech exposure?"

### M2.4 — Advanced Portfolio Analytics (Weeks 5–6)
- Portfolio vs benchmark (Nifty 50, Nifty IT, Nifty Bank)
- Sector allocation analysis + overexposure warnings
- Dividend tracking and projected annual income
- Tax implications: STCG vs LTCG calculator (buy/sell date aware)
- "What-If" simulator: "What if I had bought 100 TCS shares 6 months ago?"

### M2.5 — Infrastructure Upgrades (Weeks 6–8)
- Migrate ChromaDB → Qdrant (Docker on Windows)
- Upgrade embeddings: sentence-transformers → OpenAI text-embedding-3-small
- Migrate SQLite → PostgreSQL (Supabase free tier)
- Add Alembic for DB migrations
- Basic user authentication (for family access)
- Conversational memory (remember previous messages in session)

### M2.6 — UX Polish (Weeks 8–10)
- Suggested follow-up questions after each answer
- Export reports as PDF
- Dark mode
- Mobile-responsive improvements
- Docker Compose setup (now makes sense, post-complexity)

---

## Phase 3 — Scale & Share ("It's a product")

**Goal**: Cloud deployment, real-time data, anything that makes it meaningfully better than existing retail tools.

**Trigger**: Phase 2 complete, family actively using it, clear value proposition proven.

### M3.1 — Cloud Deployment
- FastAPI → Railway or Render (free tier)
- Next.js → Vercel (free)
- PostgreSQL → Supabase (512MB free)
- Qdrant → Qdrant Cloud (1GB free)
- CI/CD with GitHub Actions
- Custom domain (optional)

### M3.2 — Real-Time Data
- Angel One SmartAPI or Upstox (free with demat account)
- WebSocket streaming for live portfolio value
- Real-time price alerts (upgrade from email to push notifications)
- Intraday chart support

### M3.3 — Advanced AI Features
- Earnings call transcript ingestion (NSE publishes these)
- Technical analysis signals: RSI, MACD, Bollinger Bands (via `ta-lib`)
- Multi-document comparison: "Compare Q4 for TCS vs Infosys vs Wipro"
- Sector rotation signals: "Which sectors are institutional money moving into?"

### M3.4 — Voice Interface (Stretch)
- Speech-to-text: Whisper API (local via `whisper.cpp` — free)
- Text-to-speech for answers
- "Hey Finance, how's my portfolio?"

---

## Risks & Mitigations (Updated)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| yfinance breaks (Yahoo changes API) | Medium | High | nsepy as backup; document alternative tickers |
| NewsAPI 100 req/day not enough | Medium | Medium | Batch queries; GNews as backup source |
| Ollama (mistral) gives weak financial answers | Medium | Medium | Upgrade to llama3.1:8b; switch to Claude API if quality is blocking |
| ChromaDB sparse for mid-cap stocks | High | Medium | Nifty 500 scope limit + explicit "limited data" warning |
| Family members confused by chat UI | High | High | Expert/Simple toggle in Phase 1 Sprint 4, not Phase 3 |
| Windows-specific library install issues | Medium | Low | Document fixes in claude-code-setup-prompt.md troubleshooting |
| Scope creep (too many features in Phase 1) | High | High | Sprint plans enforce hard P0/P1/P2 tiers; cut P2 before P0 |

---

## Decision Log (chronological)

| Date | Decision | Reason |
|------|----------|--------|
| Apr 2026 | Use ChromaDB for Phase 1 | Zero setup, sufficient for learning |
| Apr 2026 | Use yfinance as primary data source | Free, reliable, covers NSE/BSE well |
| Apr 2026 | FastAPI over Django/Flask | Best Python AI/ML ecosystem, async |
| Apr 2026 | sentence-transformers over OpenAI embeddings | Free, local, no API cost |
| Apr 2026 | Ollama (mistral:7b) for dev LLM | No free Anthropic API credits; Ollama is truly free |
| Apr 2026 | Nifty 500 scope for Phase 1 | Prevent hallucinations from sparse mid-cap data |
| Apr 2026 | Move watchlist alerts to Phase 1 | Highest daily-use value, low build cost |
| Apr 2026 | Move Expert/Simple mode to Phase 1 | Family beta in Phase 1 requires it |
| Apr 2026 | Move mutual funds to Phase 2 | More relevant to family than direct stocks |
| Apr 2026 | Defer Docker Compose to Phase 2 | Windows complexity not worth it during initial build |
