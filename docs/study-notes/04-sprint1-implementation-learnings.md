# Study Notes: Sprint 1 Implementation Learnings

**Date:** April 2026
**Sprint:** Sprint 1 — Scaffold & Hello World RAG
**Status:** Completed ✅
**What this is:** Real-world observations from actually building and running the system. Theory meets reality.

---

## What We Actually Built and Verified

By end of Sprint 1, the following was confirmed working on a live Windows 11 machine:

```
POST /api/news/ingest  → fetched 3 real articles from NewsAPI
                       → embedded with sentence-transformers
                       → stored in ChromaDB with metadata

POST /api/chat         → embedded the question
                       → retrieved 3 most relevant news chunks from ChromaDB
                       → sent context + question to Mistral (Ollama)
                       → returned answer + cited 3 real sources with dates

GET  /health           → {"status": "ok", "llm": "ollama", "version": "0.1.0"}
```

The full RAG loop — ingest → embed → store → retrieve → generate → cite — works end to end.

---

## Real Output from the First Successful RAG Query

**Question asked:** "What is a Price to Earnings ratio and why does it matter for Indian stocks?"

**Sources retrieved (real, from ChromaDB):**
- "Stock Market Highlights: Sensex, Nifty close in the red..." — BusinessLine, 2026-04-23
- "Closing bell: Sensex settles 918 points higher..." — BusinessLine, 2026-04-10
- "Stock Market Live: Sensex drops 370 pts, Nifty tops 22,800..." — BusinessLine, 2026-04-07

**Mistral's answer (key part):**
> "The sources used for this response are the provided context documents that mentioned changes in stock market indices, but they did not provide specific data about the P/E ratios, which would require additional data on the EPS and share prices of individual companies."

**Why this is actually perfect behavior:**
The system prompt says "Answer using ONLY the provided context. If you don't have enough information, say so clearly." Mistral correctly identified that the retrieved news articles were about index movements, not P/E ratios specifically, and said so instead of hallucinating numbers. This is exactly what a trustworthy financial AI should do.

**Lesson:** A good system prompt that instructs the LLM to admit uncertainty is as important as the retrieval quality. Both are needed.

---

## Warnings Encountered and What They Actually Mean

### 1. ChromaDB Telemetry Errors (harmless)

```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
Failed to send telemetry event ClientCreateCollectionEvent: ...
Failed to send telemetry event CollectionQueryEvent: ...
```

**What it is:** A confirmed bug in `chromadb==0.5.x`. The internal `capture()` method signature changed in a dependency but ChromaDB's call sites weren't updated. The calls fail silently — no data is actually sent, and nothing breaks.

**Impact on functionality:** Zero. The RAG pipeline works perfectly despite these errors.

**Fix:** Upgrade to `chromadb>=0.6.0` where the bug is patched. Deferred to Phase 2 since it's a bigger upgrade.

**What to do now:** Ignore these lines in your logs. They'll be there every time you start the server. They are not errors in your code.

### 2. Windows Symlinks Warning (harmless)

```
UserWarning: `huggingface_hub` cache-system uses symlinks by default to efficiently 
store duplicated files but your machine does not support them in 
C:\Users\Ronit\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2
```

**What it is:** HuggingFace's model cache normally uses symlinks to avoid duplicating large model files. Windows doesn't allow symlinks by default for non-admin users.

**Impact on functionality:** Zero. The model downloads and works perfectly. You just use slightly more disk space because the cache can't deduplicate via symlinks.

**Fix (optional):** Enable Windows Developer Mode in Settings → System → For developers. This allows symlinks without admin rights. Not urgent.

**Practical note:** The `all-MiniLM-L6-v2` model is ~90MB. Even without symlinks, you won't run into disk issues.

### 3. LangChain Deprecation Warning (minor)

```
LangChainDeprecationWarning: The class `HuggingFaceEmbeddings` was deprecated in 
LangChain 0.2.2 and will be removed in 1.0.
```

**What it is:** LangChain moved `HuggingFaceEmbeddings` from `langchain_community` to a dedicated `langchain-huggingface` package.

**Fix applied:**
```bash
pip install langchain-huggingface
```
Then in `app/core/embeddings.py`:
```python
# Old (deprecated):
from langchain_community.embeddings import HuggingFaceEmbeddings

# New (correct):
from langchain_huggingface import HuggingFaceEmbeddings
```

**Lesson:** LangChain moves fast and breaks things between minor versions. Always pin your requirements.txt versions exactly. Don't use `langchain>=0.3.0` — use `langchain==0.3.0`.

### 4. ChromaDB k Auto-Capping (expected behavior)

```
Number of requested results 5 is greater than number of elements in index 3, 
updating n_results = 3
```

**What it is:** We asked ChromaDB for `k=5` nearest results, but only 3 documents were in the collection. ChromaDB automatically reduces k to the collection size.

**Impact on functionality:** Zero — returns the best available results.

**When it disappears:** As soon as you ingest more articles than k. After running 5 news ingest calls, you'll have 100+ articles and this warning never appears again.

**Lesson:** This is useful behavior — ChromaDB gracefully handles the "not enough data" case rather than throwing an error. Your code doesn't need to handle this edge case.

### 5. Ollama "bind: Only one usage of each socket address" (good sign)

```
Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket address 
(protocol/network address/port) is normally permitted.
```

**What it is:** You tried to run `ollama serve` but Ollama was already running in the background. The Windows installer starts Ollama as a background service automatically.

**What to do:** Nothing. This error means Ollama is already running — which is exactly what you want. You don't need to run `ollama serve` manually.

**How to verify Ollama is running:**
```powershell
curl http://localhost:11434/api/tags
```
If it returns a JSON list of models (including `mistral:latest`), Ollama is running correctly.

---

## Key Architecture Insight: What the Full RAG Loop Looks Like in Logs

When you call `POST /api/chat`, here's the sequence you can trace in the logs:

```
1. Request comes in: POST /api/chat {"message": "..."}
2. [embeddings.py] get_embeddings() called — returns cached instance
3. [vectorstore.py] similarity_search() called — ChromaDB searches
   → "Number of requested results 5..." (if < 5 docs) or silent
4. [rag_service.py] Retrieved N documents passed to Mistral
5. [ollama] Mistral generates answer (takes 3-15 seconds depending on length)
6. Response sent: {"answer": "...", "sources": [...], "session_id": null}
7. Log: "POST /api/chat HTTP/1.1" 200 OK
```

The telemetry errors fire at step 3 — they're ChromaDB trying (and failing) to log events to their servers. Everything before and after step 3 works correctly.

---

## How the News Ingest Pipeline Actually Works

When you call `POST /api/news/ingest?query=TCS Infosys earnings&limit=50`:

```
1. news_service.py calls NewsAPI with your query
2. NewsAPI returns up to `limit` articles (title + description + URL + date + source)
3. Each article is formatted as a text document:
   "Title: [article title]\n[description text]"
4. Metadata is attached: {ticker, date, source, type: "news"}
5. ingest_service.py chunks the text (if long enough)
6. sentence-transformers embeds each chunk into a 384-dim vector
7. ChromaDB stores: vector + text + metadata
8. Returns: {"ingested": N, "collection": "stock_news"}
```

**Important:** NewsAPI free tier gives you 100 requests/day. Each `POST /api/news/ingest` call = 1 request. Plan accordingly — 5-10 ingest calls per day is safe.

**Recommended daily ingest queries to maximize coverage:**
```
Morning (pre-market):
  - "Nifty Sensex Indian stock market today"
  - "TCS Infosys Wipro IT sector India"
  - "HDFC Bank Reliance ICICI earnings results"

Evening (post-close):
  - "NSE BSE closing market update India"
  - "Indian economy RBI inflation stocks"
```

---

## What "Good" RAG Behavior Looks Like vs "Bad"

**Good behavior (what we saw):**
- Sources are real, dated, from named publications
- Answer acknowledges when context doesn't contain specific data
- Answer is grounded: "Based on the news articles from April 2026..."
- Sources match the question topic (market news → market news retrieved)

**Bad behavior (what to watch for as data grows):**
- Sources are irrelevant to the question (retrieval failing)
- Answer contradicts the sources (LLM ignoring context)
- Answer states specific numbers not in any source (hallucination)
- "I cannot answer" even when relevant sources exist (over-cautious prompt)

**How to diagnose if answers feel wrong:**
1. Check the `sources` array in the response — are those chunks relevant to the question?
2. If sources are irrelevant → retrieval problem (ChromaDB, embedding quality)
3. If sources are relevant but answer is wrong → generation problem (system prompt, Mistral)

This distinction matters — retrieval bugs and generation bugs require different fixes.

---

## Sprint 1 Definition of Done — Final Status

| Item | Status | Notes |
|------|--------|-------|
| `/health` returns `{"status": "ok", "llm": "ollama"}` | ✅ Done | Confirmed |
| Ollama (mistral) responds to test question | ✅ Done | test_llm() passes |
| ChromaDB collection created with embedded documents | ✅ Done | `stock_news` collection |
| RAG chain returns answer with source citations | ✅ Done | 3 real BusinessLine articles cited |
| News ingestion pipeline working | ✅ Done | NewsAPI → embed → ChromaDB |
| Next.js frontend loads at localhost:3000 | ✅ Done | Shell confirmed |
| All code committed to `dev` branch on GitHub | ⬜ Pending | Commit before Sprint 2 starts |

**One remaining action before Sprint 2:** `git add . && git commit -m "Sprint 1 complete: RAG pipeline working end-to-end"`

---

## What to Learn Next

Before starting Sprint 2 (yfinance data pipeline), it helps to understand:

- **pandas DataFrames** — yfinance returns data as pandas DataFrames. You'll need to know how to convert them to dicts/lists for JSON responses and ChromaDB storage.
- **APScheduler basics** — how to schedule recurring jobs (morning news ingest, evening price update) without a separate process.

Both are covered briefly in Sprint 2 setup. No prior knowledge needed — just be aware they're coming.

---

*Updated: April 2026 | Next: `05-yfinance-and-pandas.md` (pre-reading for Sprint 2) → `06-apscheduler.md`*
