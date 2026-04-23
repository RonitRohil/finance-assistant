# FinanceAssistant — Phases Roadmap

**Last updated:** April 2026  
**Project start:** May 2026 (estimated)

---

## Overview

```
Phase 1: Foundation (8–10 weeks)
  ↓ RAG pipeline working, basic chat UI, stock Q&A, news ingestion

Phase 2: Intelligence (8–10 weeks)
  ↓ Portfolio tracking, personal finance, smarter agents, better UI

Phase 3: Scale & Share (ongoing)
  ↓ Cloud deployment, multi-user, alerts, advanced analysis
```

---

## Phase 1 — Foundation ("It works!")

**Goal**: A working local app where you can chat with an AI about Indian stocks and get answers grounded in real data.

**Definition of Done for Phase 1**: You can ask "How has TCS performed this quarter?" and get an answer based on actual recent data — not hallucination.

### Milestones

#### M1.1 — Project Scaffold (Week 1–2)
- [ ] Initialize FastAPI project with proper folder structure
- [ ] Initialize Next.js frontend with TypeScript + Tailwind
- [ ] Set up Docker Compose to run both services together
- [ ] Configure Claude API key and test basic LLM call
- [ ] Write Hello World RAG: one document, one question, one answer

**Deliverable**: Two services running locally. Can ask Claude a question.

#### M1.2 — Data Pipeline (Week 2–3)
- [ ] Install and test yfinance with 10 Indian stocks
- [ ] Write `DataIngester` class: fetches stock data, formats as documents
- [ ] Install sentence-transformers, generate first embeddings
- [ ] Install ChromaDB, set up `stock_news` and `stock_data` collections
- [ ] Write `VectorStore` class: insert documents, query similar documents
- [ ] Test: embed 50 stock summaries, query "profitable tech stock"

**Deliverable**: ChromaDB populated with real Indian stock data.

#### M1.3 — RAG Chain (Week 3–4)
- [ ] Build LangChain RetrievalQA chain connected to ChromaDB
- [ ] Write system prompt for financial Q&A (grounded, cite sources)
- [ ] Build `/api/ask` FastAPI endpoint
- [ ] Test with 20 sample questions, check answer quality
- [ ] Add source citations to responses (which documents were retrieved)

**Deliverable**: Working RAG endpoint. Answers financial questions using real data.

#### M1.4 — News Ingestion (Week 4–5)
- [ ] Sign up for NewsAPI, write news fetcher
- [ ] Write news processor: clean → chunk → embed → store
- [ ] Schedule news ingestion with APScheduler (morning + evening)
- [ ] Build news collection in ChromaDB with metadata (date, ticker, source)
- [ ] Add news to RAG retrieval pipeline
- [ ] Test: "What's the latest news about Infosys?" returns actual recent articles

**Deliverable**: AI answers include current news context.

#### M1.5 — Basic Portfolio (Week 5–6)
- [ ] Design SQLite schema: stocks table, holdings table, transactions table
- [ ] Build `/api/portfolio` CRUD endpoints (add/update/delete holdings)
- [ ] Write portfolio calculator: current value, P&L, allocation %
- [ ] Add portfolio context to RAG ("given my holdings: X shares of Y...")
- [ ] Test: "How is my portfolio doing today?" returns actual P&L

**Deliverable**: Portfolio tracking with manual entry works.

#### M1.6 — Chat UI (Week 6–8)
- [ ] Build chat interface in Next.js (message bubbles, input box)
- [ ] Build stock dashboard page (price chart, key metrics)
- [ ] Build portfolio overview page (allocation pie chart, P&L table)
- [ ] Build news feed page (recent market news)
- [ ] Connect all pages to FastAPI endpoints
- [ ] Mobile-responsive layout

**Deliverable**: A real usable app. Share with father/cousins to try.

#### M1.7 — Polish & Testing (Week 8–10)
- [ ] Add error handling everywhere (API down, rate limit hit, etc.)
- [ ] Add loading states in UI
- [ ] Write basic tests for RAG pipeline
- [ ] Document setup instructions in README
- [ ] Record a demo video for portfolio
- [ ] Get 5 pieces of feedback from family beta users

**Phase 1 Complete**: Working local app, production-quality code, great portfolio piece.

---

## Phase 2 — Intelligence ("It's smart!")

**Goal**: The app gets meaningfully smarter — it knows your portfolio deeply, understands your spending, and proactively surfaces insights rather than just answering questions.

**Trigger**: Phase 1 is complete and being used daily.

### Milestones

#### M2.1 — Personal Finance Module (Week 1–3)
- [ ] Build PDF upload for bank/credit card statements
- [ ] Write statement parser (pdfplumber) for HDFC, SBI, ICICI formats
- [ ] Categorize transactions (food, rent, investment, EMI, etc.) using Claude
- [ ] Build spending dashboard: monthly breakdown, category trends
- [ ] Add spending data to RAG: "How much did I spend on food vs investing?"
- [ ] Build savings goal tracker

#### M2.2 — AI Agents (Week 3–5)
- [ ] Upgrade from simple RetrievalQA to LangChain Agent
- [ ] Build tools the agent can call:
  - `get_stock_price(ticker)` — real-time price
  - `get_portfolio_performance()` — P&L calculation
  - `search_news(query, date_range)` — filtered news search
  - `compare_stocks(ticker1, ticker2)` — side-by-side comparison
  - `get_fundamentals(ticker)` — P/E, revenue, debt
- [ ] Let agent decide which tools to call based on the question
- [ ] Test multi-step reasoning: "Should I buy more TCS or add Wipro to balance my tech exposure?"

#### M2.3 — Advanced Portfolio Analytics (Week 5–6)
- [ ] Portfolio vs benchmark comparison (vs Nifty 50, Nifty IT)
- [ ] Sector allocation analysis
- [ ] Correlation analysis between holdings
- [ ] Dividend tracking and projected income
- [ ] Tax loss harvesting suggestions (basic)

#### M2.4 — Migrate to Qdrant (Week 6–7)
- [ ] Set up Qdrant in Docker
- [ ] Migrate all ChromaDB data to Qdrant
- [ ] Enable payload filtering (retrieve news only for specific date ranges, tickers)
- [ ] Upgrade embeddings to OpenAI text-embedding-ada-002 (better quality)
- [ ] Re-embed all documents

#### M2.5 — Migrate DB to PostgreSQL (Week 7)
- [ ] Set up PostgreSQL in Docker
- [ ] Migrate SQLite schema to PostgreSQL
- [ ] Add Alembic for database migrations
- [ ] Add basic user authentication (for family access)

#### M2.6 — UX Improvements (Week 8–10)
- [ ] Conversational memory (remember previous messages in session)
- [ ] Suggested follow-up questions
- [ ] Export reports as PDF
- [ ] Dark mode
- [ ] Watchlist with price alerts (email notification)

---

## Phase 3 — Scale & Share ("It's a product!")

**Goal**: Deploy to cloud so family can use it from anywhere. Add features that make it meaningfully better than existing tools.

**Trigger**: Phase 2 is complete and family is actively using it.

### Milestones

#### M3.1 — Cloud Deployment
- [ ] Choose cloud provider: Railway, Render, or AWS (free tiers)
- [ ] Deploy FastAPI on Railway or Render
- [ ] Deploy Next.js on Vercel (free)
- [ ] Move PostgreSQL to Supabase (free 512MB)
- [ ] Move Qdrant to Qdrant Cloud (free 1GB)
- [ ] Set up CI/CD with GitHub Actions

#### M3.2 — Real-Time Data
- [ ] Integrate Angel One SmartAPI or Upstox for real-time prices
- [ ] WebSocket streaming for live portfolio value updates
- [ ] Real-time market alerts (price crosses target, news about watchlist)

#### M3.3 — Advanced AI Features
- [ ] Multi-document comparison: "Compare Q4 results for TCS vs Infosys vs Wipro"
- [ ] Earnings call transcript ingestion and Q&A
- [ ] Technical analysis signals (RSI, MACD via ta-lib)
- [ ] "Explain this in simple terms" mode for family members

#### M3.4 — Mutual Funds Module
- [ ] AMFI NAV data ingestion (free)
- [ ] Track SIP investments
- [ ] Fund vs benchmark comparison
- [ ] Switch/redeem recommendations

#### M3.5 — Voice Interface (Stretch Goal)
- [ ] Speech-to-text input (Whisper API)
- [ ] Text-to-speech for answers
- [ ] "Hey Finance, how's my portfolio today?"

---

## Decision Log (update when decisions change)

| Date | Decision | Reason |
|------|----------|--------|
| Apr 2026 | Use ChromaDB for Phase 1 | Zero setup, sufficient for learning |
| Apr 2026 | Use yfinance as primary data source | Free, reliable, covers NSE/BSE well |
| Apr 2026 | FastAPI over Django/Flask | Best Python AI/ML ecosystem, async |
| Apr 2026 | sentence-transformers over OpenAI embeddings | Free, local, no API cost |
| Apr 2026 | Claude API (Anthropic) as LLM | Best reasoning, we already use Claude |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| yfinance breaks (Yahoo changes API) | Medium | High | Keep nsepy as backup; document alternative |
| NewsAPI 100 req/day not enough | Medium | Medium | Batch queries; add GNews as backup source |
| ChromaDB performance degrades | Low | Medium | Migration to Qdrant already planned (Phase 2) |
| Claude API costs run high | Low | Low | Use Haiku for cheap queries, Sonnet only for complex analysis |
| Indian broker API requires KYC delay | Medium | Low | Phase 2 feature; yfinance covers us until then |
