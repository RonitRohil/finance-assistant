# FinanceAssistant — Phase 1 Sprint Plans

**Last updated:** April 2026
**Team:** Ronit Jain (solo developer + learner)
**Capacity:** ~15–20 hrs/week (job hunting in parallel)
**Sprint length:** 2 weeks
**Estimation unit:** Hours (solo project, no story points needed)
**Buffer rule:** Plan to 70% capacity — learning new concepts always takes longer than expected

---

## Capacity Baseline

| Sprint | Available Hours | Planned (70%) | Buffer | Notes |
|--------|----------------|--------------|--------|-------|
| Sprint 1 | 30–40 hrs | 21–28 hrs | 10+ hrs | Heaviest learning curve (setup, new tools) |
| Sprint 2 | 30–40 hrs | 21–28 hrs | 10+ hrs | Data pipeline concepts new |
| Sprint 3 | 30–40 hrs | 21–28 hrs | 10+ hrs | LangChain chains + ChromaDB together |
| Sprint 4 | 30–40 hrs | 21–28 hrs | 10+ hrs | Most feature-dense sprint |
| Sprint 5 | 30–40 hrs | 21–28 hrs | 10+ hrs | UI + polish — faster once RAG works |

---

## Sprint 1 — Scaffold & Hello World RAG

**Dates:** Week 1–2 of May 2026
**Sprint goal:** Two services running locally. You can ask the AI one financial question and get an answer backed by real data — not hallucination.
**Success test:** `curl localhost:8000/health` returns OK. Ask "What is a P/E ratio?" via the chat endpoint and Ollama responds with a grounded answer.

### Backlog

| Priority | Item | Est. Hours | Notes |
|----------|------|-----------|-------|
| P0 | Install Ollama, pull mistral model | 1 hr | Download once, ~4GB |
| P0 | Create GitHub repo, clone locally | 0.5 hr | `finance-assistant` monorepo |
| P0 | Run Claude Code setup prompt (backend scaffold) | 2–3 hrs | From `claude-code-setup-prompt.md` — Claude Code generates the files |
| P0 | Verify FastAPI runs, `/health` endpoint returns OK | 0.5 hr | `uvicorn app.main:app --reload` |
| P0 | Verify Ollama responds via `get_llm()` factory | 1 hr | Run `test_llm()` function |
| P0 | Set up ChromaDB with first collection (`stock_data`) | 2 hrs | Embed 5 manual documents, test query |
| P0 | Hello World RAG chain: 1 doc → 1 question → 1 answer | 3 hrs | LangChain RetrievalQA, hardcoded document |
| P0 | Initialize Next.js frontend, verify at localhost:3000 | 1 hr | `npx create-next-app` |
| P1 | Git branching: create `dev` branch, first commit | 0.5 hr | Never push main directly |
| P1 | Create `.env` from `.env.example`, configure all keys | 0.5 hr | Ollama, ChromaDB paths |
| P1 | Write `README.md` setup instructions | 1 hr | So future-you can re-setup in 10 mins |
| P2 | Study: read `01-rag-fundamentals.md` study notes | 1 hr | Do this before building the RAG chain |
| P2 | Study: read `02-vector-databases.md` study notes | 1 hr | Do this before ChromaDB setup |

**Planned load:** ~14–15 hrs (well within 70% buffer — this sprint has high uncertainty)

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ollama install issues on Windows | High | Troubleshooting section in `claude-code-setup-prompt.md` |
| ChromaDB install fails on Windows | Medium | `pip install chromadb --only-binary :all:` |
| Claude Code generates wrong structure | Medium | Review each file against CLAUDE.md before accepting |
| LangChain version conflicts | Medium | Pin versions in `requirements.txt` exactly as specified |

### Definition of Done — Sprint 1
- [ ] `GET /health` returns `{"status": "ok", "llm": "ollama"}`
- [ ] Ollama (mistral) responds to at least one test question
- [ ] ChromaDB collection created with 5+ embedded documents
- [ ] RAG chain returns an answer with source document citation
- [ ] Next.js frontend loads at `localhost:3000` without errors
- [ ] All code committed to `dev` branch on GitHub

### Key Dates
| Date | Event |
|------|-------|
| May 5 | Sprint start |
| May 9 | Mid-sprint check: is Ollama + FastAPI working? If not, debug before going further |
| May 16 | Sprint end / demo to yourself: ask 3 questions, verify answers |

---

## Sprint 2 — Data Pipeline (Real Indian Market Data)

**Dates:** Week 3–4 of May 2026
**Sprint goal:** ChromaDB populated with real NSE/BSE data for Nifty 500 stocks. News flowing in automatically. Sparse-data warning works.
**Success test:** Ask "Tell me about TCS's recent performance" and get an answer citing actual yfinance data, not hardcoded text. Ask about a random mid-cap outside Nifty 500 and see the "limited data" warning.

### Backlog

| Priority | Item | Est. Hours | Notes |
|----------|------|-----------|-------|
| P0 | Build `stock_service.py`: yfinance wrapper for Nifty 500 | 4 hrs | `.NS` suffix auto-append, error handling |
| P0 | Download Nifty 500 ticker list (NSE publishes CSV) | 1 hr | Store as `backend/data/nifty500_tickers.csv` |
| P0 | Build `ingest_service.py`: stock data → ChromaDB | 4 hrs | Format summaries, add metadata (ticker, date, type) |
| P0 | Run first bulk ingest: 500 stock summaries embedded | 2 hrs | Will take ~20–30 mins to run; verify in ChromaDB |
| P0 | Sparse data detection: warn if < 3 docs retrieved | 2 hrs | Add to RAG service response |
| P0 | Sign up for NewsAPI, build `news_service.py` | 2 hrs | newsapi-python library |
| P0 | Build news ingestion: fetch → chunk → embed → store | 3 hrs | `stock_news` collection with date/ticker metadata |
| P0 | APScheduler: schedule news ingest morning + evening | 2 hrs | 9 AM and 6 PM IST |
| P1 | Test retrieval: 10 queries, check relevance | 2 hrs | Document pass/fail in a test log |
| P1 | Build `GET /api/stocks/{ticker}` endpoint | 2 hrs | Returns price, PE, market cap |
| P1 | Sign up for GNews as NewsAPI backup | 0.5 hr | 100 req/day free |
| P2 | Study: read `03-embeddings.md` study notes | 1 hr | Before running bulk embeddings |
| P2 | Experiment: try different chunk sizes (400 vs 600 chars) | 1 hr | Find best retrieval quality for financial text |

**Planned load:** ~26–27 hrs (slightly high — if tight, drop P2 items)

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| yfinance rate limiting on 500 stocks | Medium | Add 0.5s delay between fetches, run overnight |
| NewsAPI 100 req/day not enough for testing | Medium | Use batch queries (multiple tickers per request) |
| Embedding 500 stocks takes too long | Low | sentence-transformers is fast; ~500 stocks ≈ 5 minutes |
| ChromaDB query returns wrong stocks | Medium | Check metadata filtering; print top-5 results with scores |

### Definition of Done — Sprint 2
- [ ] Nifty 500 stock data ingested into ChromaDB (`stock_data` collection)
- [ ] NewsAPI news ingesting on schedule (verify in logs)
- [ ] Sparse data warning fires correctly for non-Nifty-500 stocks
- [ ] `/api/stocks/TCS.NS` returns real current price and PE ratio
- [ ] 10 test queries run and results documented (pass/fail)
- [ ] APScheduler jobs visible and running in FastAPI startup logs

### Key Dates
| Date | Event |
|------|-------|
| May 19 | Sprint start |
| May 23 | Mid-sprint: is yfinance data in ChromaDB? Run first query test |
| May 30 | Sprint end / demo: live news query working |

---

## Sprint 3 — RAG Chain + Indian Financial Calendar

**Dates:** Week 5–6 of June 2026
**Sprint goal:** The full RAG chain answers financial questions with citations. Indian market calendar embedded — system knows upcoming RBI dates, F&O expiry, earnings season.
**Success test:** Ask "Is there any major market event this week?" and get an answer citing the financial calendar. Ask "What's Reliance's recent performance?" and get a cited answer from real data.

### Backlog

| Priority | Item | Est. Hours | Notes |
|----------|------|-----------|-------|
| P0 | Build production RAG chain in `rag_service.py` | 4 hrs | System prompt, RetrievalQA, source citations |
| P0 | Craft financial system prompt (cite sources, admit uncertainty) | 2 hrs | Most important prompt engineering in Phase 1 |
| P0 | Build Indian financial calendar data source | 3 hrs | JSON file: RBI dates, F&O expiry (last Thursday each month), earnings season months, Budget date |
| P0 | Embed calendar into ChromaDB (`market_events` collection) | 1 hr | One-time ingest, update monthly |
| P0 | Add `POST /api/chat` endpoint | 2 hrs | Request/response schema, calls rag_service |
| P0 | Test 20 questions end-to-end, document results | 3 hrs | Build a `tests/rag_test_cases.md` with expected vs actual |
| P1 | Multi-collection retrieval: pull from stock_data AND stock_news AND market_events | 2 hrs | Merge results, re-rank by relevance |
| P1 | Add conversation session ID to chat endpoint | 1 hr | Store last 5 messages in memory for context |
| P1 | Portfolio context injection: "Given my holdings: [X]..." | 2 hrs | Pull from SQLite, inject into system prompt |
| P2 | Write study note: `04-langchain-chains.md` | 1.5 hrs | Document what you learned about RetrievalQA and chains |
| P2 | Experiment: RAG with vs without calendar data (compare answer quality) | 1 hr | Should show clear improvement for event-related questions |

**Planned load:** ~21–22 hrs

### Indian Financial Calendar Data to Embed
Build this as `backend/data/indian_financial_calendar.json`:
```json
[
  {"event": "RBI MPC Meeting", "date": "2026-06-04", "impact": "All sectors", "description": "Reserve Bank of India Monetary Policy Committee rate decision. Markets typically volatile 1-2 days before and after. Banking stocks most affected."},
  {"event": "F&O Expiry", "date": "2026-05-28", "recurrence": "Last Thursday of every month", "impact": "Nifty, BankNifty", "description": "Monthly futures and options expiry. Volatility typically spikes in the last hour of trading. Intraday moves may be exaggerated."},
  {"event": "Q4 FY26 Results Season", "date_range": "Apr–May 2026", "impact": "All sectors", "description": "Companies report January–March quarter results. IT companies typically report first (TCS, Infosys, Wipro in April)."},
  {"event": "Union Budget", "date": "2027-02-01", "recurrence": "First working day of February", "impact": "All sectors", "description": "Annual budget announcement. Historically most impactful single day for Indian markets. Defence, infra, FMCG sectors move dramatically."}
]
```

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mistral gives weak answers on Indian companies | High | Upgrade to llama3.1:8b; add more context in system prompt |
| Multi-collection retrieval returns noisy results | Medium | Implement metadata-filtered retrieval per query type |
| RAG citations are hallucinated | Medium | Always return `source_documents` and display them in UI |
| System prompt too complex, Ollama ignores parts | Medium | Simplify prompt; test each constraint independently |

### Definition of Done — Sprint 3
- [ ] `/api/chat` endpoint working end-to-end
- [ ] 20 test questions documented with pass/fail and quality score (1–5)
- [ ] Indian financial calendar embedded in ChromaDB
- [ ] Calendar context appears in answers about market events
- [ ] Portfolio holdings injected into RAG context
- [ ] Source citations returned with every answer

### Key Dates
| Date | Event |
|------|-------|
| Jun 2 | Sprint start |
| Jun 6 | Mid-sprint: RAG chain working? Run first 10 test questions |
| Jun 13 | Sprint end / demo: 20 question test pass rate ≥ 70% |

---

## Sprint 4 — Portfolio + Power Features

**Dates:** Week 7–8 of June 2026
**Sprint goal:** The "Why is this stock moving today?" feature works. Portfolio tracking with P&L works. Expert/Simple mode toggle works. Watchlist alerts send emails.
**Success test:** Add RELIANCE.NS to portfolio (100 shares @ ₹2800). Ask "Why is Reliance moving today?" — system returns news + price context + portfolio impact. Toggle to Simple mode — same question returns jargon-free answer your father would understand.

### Backlog

| Priority | Item | Est. Hours | Notes |
|----------|------|-----------|-------|
| P0 | Portfolio SQLite schema + CRUD endpoints | 3 hrs | holdings, transactions tables; `/api/portfolio` |
| P0 | Portfolio P&L calculator | 2 hrs | Current value, gain/loss, %, vs Nifty |
| P0 | "Why is this stock moving today?" compound query | 4 hrs | Fuses: today's price delta + top 3 news chunks + calendar events + technical context; single prompt |
| P0 | Expert / Simple conversation mode toggle | 2 hrs | System prompt switch; stored in session or user preference |
| P0 | Watchlist table in SQLite | 1 hr | ticker, target_price, alert_type (above/below), email |
| P0 | Price alert checker: APScheduler job, email via SMTP | 3 hrs | Gmail SMTP works free; runs every 30 mins during market hours |
| P1 | `/api/portfolio` injected into RAG — "given my holdings..." | 2 hrs | Already partially built in Sprint 3; complete it |
| P1 | Nifty 50 benchmark comparison for portfolio | 2 hrs | yfinance `^NSEI` historical data |
| P1 | Sector allocation summary (tech %, banking %, etc.) | 2 hrs | Map Nifty 500 tickers to sectors via lookup table |
| P2 | Write study note: `05-agentic-rag.md` | 1.5 hrs | Document the "Why is this stock moving" multi-source fusion pattern |
| P2 | What-If simulator: historical hypothetical trade P&L | 2 hrs | yfinance historical + date math — purely computational, no AI |

**Planned load:** ~24–25 hrs (dense sprint — cut P2 first if running long)

### "Why Is This Stock Moving Today?" — Build Plan

This is the killer demo feature. Here's exactly how to build it:

```
User asks: "Why is TCS falling today?"

Step 1 — Detect intent: "why is [ticker] moving" pattern
Step 2 — Fetch live context (real-time, not from ChromaDB):
  - Current price + % change from yfinance
  - 5-day price history (for context: is this a continuation or reversal?)
Step 3 — Retrieve from ChromaDB:
  - Top 3 news chunks for TCS from last 48 hours
  - Any market_events in the next 7 days
  - Latest earnings summary for TCS
Step 4 — Check portfolio context:
  - Does user hold TCS? What % of portfolio?
Step 5 — Compose compound prompt:
  "TCS is down 2.3% today (₹3,420 → ₹3,341).
   Recent news: [3 chunks]
   Upcoming events: [calendar]
   User holds: 50 shares (8% of portfolio)
   Explain why the stock is moving and what it means for the user."
Step 6 — Return answer + all sources cited
```

This one feature demonstrates: live data fetching, RAG retrieval, calendar context, portfolio awareness, and LLM reasoning all in one query. Perfect for interview demos.

### Email Alert Setup (Free)

```python
# Uses Gmail SMTP — completely free
import smtplib
from email.mime.text import MIMEText

def send_alert(to_email, ticker, current_price, target_price):
    msg = MIMEText(f"{ticker} has crossed your target of ₹{target_price}. Current: ₹{current_price}")
    msg['Subject'] = f"FinanceAssistant Alert: {ticker}"
    msg['From'] = "your.gmail@gmail.com"
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("your.gmail@gmail.com", "app_password_here")
        server.send_message(msg)
```

Use Gmail App Password (not your regular password) — enable in Google account settings.

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| "Why is stock moving" prompt too long for Ollama context | High | Keep retrieved context < 2000 chars; summarize news chunks |
| Email alerts spam during testing | Low | Use a test email; add "test mode" flag |
| P&L calculation wrong (currency, splits) | Medium | Test with known historical data; check yfinance `auto_adjust=True` |
| Sprint is too packed | High | P2 items are all optional — cut ruthlessly |

### Definition of Done — Sprint 4
- [ ] Portfolio CRUD works (add/edit/delete holdings, view P&L)
- [ ] "Why is this stock moving?" returns cited answer with live price + news
- [ ] Expert/Simple mode toggle changes answer style measurably (test with same question)
- [ ] Watchlist email alert fires when price crosses target (test manually)
- [ ] Portfolio vs Nifty 50 comparison works

### Key Dates
| Date | Event |
|------|-------|
| Jun 16 | Sprint start |
| Jun 20 | Mid-sprint: portfolio CRUD and "why is moving" working |
| Jun 27 | Sprint end / demo: show the full "why is stock moving" flow to someone |

---

## Sprint 5 — Chat UI + Polish + Family Beta

**Dates:** Week 9–10 of July 2026
**Sprint goal:** A real, shareable app. Your family can log in (locally for now), use it, and give feedback. You have a demo video for your portfolio.
**Success test:** Your father uses the app on his own (without you explaining it). He asks a question and gets a useful answer. You record a 3-minute demo video.

### Backlog

| Priority | Item | Est. Hours | Notes |
|----------|------|-----------|-------|
| P0 | Chat interface in Next.js (message bubbles, input, history) | 4 hrs | Use shadcn/ui components; keep it simple |
| P0 | Source citations displayed below AI answer | 2 hrs | "Based on: [article title, date, source]" |
| P0 | Expert/Simple toggle visible in UI | 1 hr | Simple button, stores preference |
| P0 | Stock dashboard page: price chart + key metrics | 3 hrs | Recharts for price history; key metrics cards |
| P0 | Portfolio overview page: P&L table + allocation pie | 3 hrs | Recharts pie chart; colour-coded P&L |
| P0 | Error states: "I don't have enough data on this stock" shown clearly | 1 hr | Don't silently fail |
| P0 | Loading states: skeleton UI while AI is thinking | 1 hr | Prevents user from thinking app is frozen |
| P1 | News feed page: latest market news with sentiment tag | 2 hrs | Pull from ChromaDB; display as feed |
| P1 | Mobile-responsive layout (works on phone) | 2 hrs | Tailwind responsive classes |
| P1 | Basic error handling: API down, rate limit, LLM timeout | 2 hrs | User-friendly error messages |
| P1 | Record 3-minute demo video | 1 hr | Show the "why is stock moving" feature, portfolio view, mode toggle |
| P2 | Run 5 real questions from family, note feedback | 2 hrs | Write up in `docs/planning/beta-feedback.md` |
| P2 | Update `docs/study-notes/` with anything learned this sprint | 1 hr | Keep the knowledge base current |
| P2 | Clean up code: remove debug prints, add type hints | 2 hrs | Make it portfolio-ready |

**Planned load:** ~24–26 hrs

### Family Beta Protocol

Share access to the local app (on your laptop, same WiFi) with father and at least one cousin. Give them this brief:

> "This is an AI assistant for Indian stocks. Try asking it about stocks you follow. Ask it about your portfolio. Ask it what it thinks about a stock you're considering. Tell me what was confusing, what was missing, and what was useful."

Collect 5 specific pieces of feedback. Document in `docs/planning/beta-feedback.md`. Each feedback item should become either a Phase 2 task or a decision to not build it.

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| UI takes too long, cuts into polish time | Medium | Keep UI simple — shadcn components do the heavy lifting |
| Family feedback is too vague ("it's nice") | Medium | Ask specific questions: "What would make you use this daily?" |
| Demo video reveals a bug live | Low | Record multiple takes; use the clean one |
| Phase 1 scope was too ambitious | Medium | Anything not P0 can be carried to Phase 2 |

### Definition of Done — Sprint 5 (Phase 1 Complete)
- [ ] Chat UI works end-to-end with source citations visible
- [ ] Stock dashboard page works with real chart data
- [ ] Portfolio page shows real P&L and allocation
- [ ] Expert/Simple mode toggle visible and functional
- [ ] At least 1 family member has used the app and given feedback
- [ ] 5 feedback items documented
- [ ] 3-minute demo video recorded
- [ ] All code on `dev` branch, clean and committed
- [ ] Phase 1 is something you'd show at a job interview

### Key Dates
| Date | Event |
|------|-------|
| Jun 30 | Sprint start |
| Jul 4 | Mid-sprint: chat UI working, stock dashboard done |
| Jul 11 | Sprint end / Phase 1 demo day |
| Jul 12 | Family beta session |
| Jul 14 | Phase 2 planning kickoff |

---

## Carryover Policy

If something doesn't get done in a sprint, be honest about it:

- **P0 items not done** → Must carry to next sprint as P0 (do not skip)
- **P1 items not done** → Carry as P1, but can be deferred to Phase 2 if two consecutive sprints pass
- **P2 items not done** → Move to Phase 2 backlog, no guilt

Unfinished work is not failure. Pretending it's done is the actual failure.

---

## Phase 1 Backlog (items not in any sprint yet)

These are good ideas from brainstorming that didn't fit Phase 1 scope. Pick from here if a sprint finishes early:

- `nsepy` integration as yfinance backup (already in ADR-004)
- SEBI circular ingestion (scrape NSE announcements page)
- Nifty sector ETF tracking (BANKBEES, ITBEES, PSUBANKEX)
- IPO calendar (NSE publishes upcoming IPO list)
- FII/DII activity data (NSE publishes daily — institutional money flow)
- SIP calculator: "How much to invest monthly to reach ₹50L in 10 years?"
