# Claude Code Setup Prompt — M1.1 Project Scaffold

This is the exact prompt to paste into Claude Code to scaffold the entire Phase 1 backend.
Run this from the root of the `finance-assistant` repo.

---

## Step 1 — Before opening Claude Code

Install these first (do once):

```bash
# 1. Install Ollama from https://ollama.com (Windows installer)
# After install, open a new terminal and pull the model:
ollama pull mistral

# 2. Make sure Python 3.11+ is installed
python --version

# 3. Make sure Node 18+ is installed
node --version

# 4. Clone your GitHub repo and open in terminal
git clone https://github.com/YOUR_USERNAME/finance-assistant.git
cd finance-assistant

# 5. Open Claude Code
claude
```

---

## Step 2 — Paste this prompt into Claude Code

Copy everything between the dashed lines and paste it as your first message to Claude Code:

---

```
I'm building a RAG-based finance assistant for Indian stock markets. 
The CLAUDE.md file in this repo has full project context. 

Please scaffold the entire backend for Phase 1. Here's exactly what I need:

**1. Create backend/ folder structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── llm.py
│   │   ├── embeddings.py
│   │   └── vectorstore.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── chat.py
│   │       ├── stocks.py
│   │       ├── portfolio.py
│   │       └── news.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py
│   │   ├── stock_service.py
│   │   ├── news_service.py
│   │   └── ingest_service.py
│   └── models/
│       ├── __init__.py
│       ├── database.py
│       └── schemas.py
├── requirements.txt
├── .env.example
└── .gitignore
```

**2. requirements.txt** — include these exact packages:
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
langchain==0.3.0
langchain-community==0.3.0
langchain-ollama==0.2.0
langchain-anthropic==0.2.0
chromadb==0.5.20
sentence-transformers==3.3.0
yfinance==0.2.48
newsapi-python==0.2.7
sqlalchemy==2.0.36
pydantic-settings==2.6.0
python-dotenv==1.0.1
apscheduler==3.10.4
httpx==0.27.2
pytest==8.3.3
```

**3. app/core/config.py** — Pydantic Settings class loading from .env:
- LLM_PROVIDER (default: "ollama")
- OLLAMA_MODEL (default: "mistral")
- OLLAMA_BASE_URL (default: "http://localhost:11434")
- ANTHROPIC_API_KEY (default: "")
- CLAUDE_MODEL (default: "claude-haiku-4-5")
- NEWSAPI_KEY (default: "")
- ALPHA_VANTAGE_KEY (default: "")
- CHROMA_PERSIST_DIR (default: "./chroma_db")
- DATABASE_URL (default: "sqlite:///./finance.db")

**4. app/core/llm.py** — LLM factory function:
- If LLM_PROVIDER == "ollama": return OllamaLLM from langchain_ollama
- If LLM_PROVIDER == "anthropic": return ChatAnthropic from langchain_anthropic
- Cache the instance (don't recreate on every call)
- Include a `test_llm()` function that sends "Say hello in one sentence" and prints the response

**5. app/core/embeddings.py** — Embedding setup:
- Use HuggingFaceEmbeddings with model "all-MiniLM-L6-v2"
- Cache the model instance (it takes ~3 seconds to load)
- Function: get_embeddings() -> HuggingFaceEmbeddings

**6. app/core/vectorstore.py** — ChromaDB setup:
- Function: get_vectorstore(collection_name: str) -> Chroma
- Use persistent ChromaDB at CHROMA_PERSIST_DIR
- Collections we'll use: "stock_news", "stock_data", "earnings_reports", "etf_data"
- Function: add_documents(collection_name, texts, metadatas) 
- Function: similarity_search(collection_name, query, k=5, filter=None)

**7. app/main.py** — FastAPI app:
- Include all routers from api/routes/
- CORS middleware (allow localhost:3000)
- Health check endpoint: GET /health returns {"status": "ok", "llm": LLM_PROVIDER, "version": "0.1.0"}
- On startup: log which LLM provider is active

**8. app/api/routes/chat.py** — Chat endpoint:
- POST /api/chat
- Request body: {"message": str, "session_id": str (optional)}
- Calls rag_service to get answer
- Response: {"answer": str, "sources": list[dict], "session_id": str}

**9. app/api/routes/stocks.py** — Stock data endpoints:
- GET /api/stocks/{ticker} — fetch basic info for a ticker using yfinance
- GET /api/stocks/{ticker}/history?period=1y — OHLCV history
- Response includes: currentPrice, previousClose, change_pct, volume, pe_ratio, market_cap

**10. app/services/rag_service.py** — RAG chain:
- Use LangChain RetrievalQA chain
- System prompt: "You are a financial analyst assistant for Indian markets. Answer using ONLY the provided context. If you don't have enough information, say so. Always cite which data you used."
- Return both the answer and source documents

**11. app/services/stock_service.py** — yfinance wrapper:
- Function: get_stock_info(ticker: str) -> dict
- Function: get_stock_history(ticker: str, period: str = "1y") -> list[dict]
- Handle errors: if ticker not found, return helpful error message
- Auto-append .NS for Indian stocks if no exchange suffix present

**12. app/models/database.py** — SQLAlchemy setup:
- SQLite database
- Holdings table: id, ticker, quantity, avg_buy_price, created_at, updated_at
- Transactions table: id, ticker, action (buy/sell), quantity, price, date, notes

**13. .env.example:**
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

**14. .gitignore** — include: .env, __pycache__, *.pyc, venv/, .venv/, chroma_db/, *.db, .pytest_cache/

After creating all files, please:
1. Create a Python virtual environment: python -m venv venv
2. Activate it and install requirements
3. Copy .env.example to .env
4. Run the health check to confirm everything works: uvicorn app.main:app --reload
5. Test the LLM connection by calling test_llm() — confirm Ollama responds

Make all code production-quality with proper error handling and type hints throughout.
```

---

## Step 3 — After Claude Code finishes

Run these to verify everything works:

```bash
# In one terminal — keep Ollama running
ollama serve

# In another terminal
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

Then open your browser: **http://localhost:8000/docs**

You should see the FastAPI auto-generated API documentation. Test the `/health` endpoint — it should return:
```json
{
  "status": "ok",
  "llm": "ollama",
  "version": "0.1.0"
}
```

---

## Step 4 — Frontend scaffold prompt (run after backend works)

Once backend is confirmed working, paste this into Claude Code:

```
Now scaffold the frontend/ folder with Next.js 14.

Run: cd frontend && npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

After setup, create these additional files:

1. src/lib/api.ts — API client with base URL pointing to http://localhost:8000
   - function askQuestion(message: string): Promise<{answer: string, sources: any[]}>
   - function getStockInfo(ticker: string): Promise<any>

2. src/app/page.tsx — Simple chat interface:
   - Text input for questions
   - Message history display (user messages + AI responses)
   - Show source citations below each AI response
   - Loading state while waiting for response

3. src/components/ChatMessage.tsx — Single message component
4. src/components/SourceCitation.tsx — Shows which documents were retrieved

Keep it simple and functional for now — no complex UI, just something that works.
```

---

## Troubleshooting

**"ollama: command not found"**  
Restart your terminal after installing Ollama. The PATH update needs a fresh terminal.

**"Connection refused" on port 11434**  
Ollama server isn't running. Open a new terminal and run `ollama serve`.

**chromadb install fails on Windows**  
Run: `pip install chromadb --only-binary :all:`

**sentence-transformers takes forever on first run**  
Normal — it's downloading the model (~80MB). Only happens once.

**yfinance returns empty data**  
Check ticker format: Indian stocks need `.NS` suffix. Test with `TCS.NS` not just `TCS`.

---

---

# Claude Code Setup Prompt — Sprint 2: Data Pipeline

**Sprint goal:** Nifty 500 stock data bulk-ingested into ChromaDB. NewsAPI news ingesting on a schedule. Sparse data detection so the system warns when it doesn't have enough to answer well.

**Run this AFTER Sprint 1 is committed and working.**

---

## Before you start

Make sure Sprint 1 is committed:
```bash
git add .
git commit -m "Sprint 1 complete: RAG pipeline working end-to-end"
git push origin dev
```

Also, if you haven't fixed the LangChain deprecation warning yet:
```bash
cd backend
venv\Scripts\activate
pip install langchain-huggingface
```

---

## Prompt to paste into Claude Code

Open Claude Code from the `finance-assistant/` root, then paste:

---

```
I'm continuing development on my RAG-based finance assistant for Indian stock markets.
The CLAUDE.md file has full project context.
Sprint 1 is complete — the RAG pipeline works end-to-end with NewsAPI and ChromaDB.

Sprint 2 goal: build the yfinance Nifty 500 data pipeline, set up APScheduler for
automated ingestion, and add sparse data detection to the RAG service.

Here is exactly what I need built:

---

**1. Create backend/data/ folder with Nifty 500 ticker list**

Create `backend/data/nifty500_tickers.py` that programmatically generates a Nifty 500 ticker list.
Use this curated list of the most important Nifty 500 stocks (cover all major sectors):

```python
# backend/data/nifty500_tickers.py
# Curated subset of Nifty 500 — all tickers use .NS suffix for NSE

NIFTY_500_TICKERS = [
    # Nifty 50 (large cap, most liquid)
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "SBIN.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "LT.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "WIPRO.NS", "SUNPHARMA.NS", "HCLTECH.NS", "TECHM.NS",
    "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "ADANIENT.NS",
    "NESTLEIND.NS", "GRASIM.NS", "BAJAJFINSV.NS", "DRREDDY.NS", "CIPLA.NS",
    "DIVISLAB.NS", "EICHERMOT.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS",
    "BPCL.NS", "IOC.NS", "M&M.NS", "TATACONSUM.NS", "BRITANNIA.NS",
    "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "SHREECEM.NS", "UPL.NS", "INDUSINDBK.NS",
    "TATAMOTORS.NS", "SBILIFE.NS", "HDFCLIFE.NS", "APOLLOHOSP.NS", "ADANIPORTS.NS",
    # Mid caps (Nifty Midcap 150 key names)
    "PIIND.NS", "MPHASIS.NS", "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS",
    "ZOMATO.NS", "PAYTM.NS", "NYKAA.NS", "POLICYBAZAAR.NS", "DMART.NS",
    "ASTRAL.NS", "ABCAPITAL.NS", "CHOLAFIN.NS", "MFSL.NS", "MAXHEALTH.NS",
    "FORTIS.NS", "LALPATHLAB.NS", "METROPOLIS.NS", "KANSAINER.NS", "BERGEPAINT.NS",
    "INDIGO.NS", "SPICEJET.NS", "IRCTC.NS", "IRFC.NS", "RVNL.NS",
    "TRENT.NS", "VEDL.NS", "NMDC.NS", "NATIONALUM.NS", "SAIL.NS",
    "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS", "PIDILITIND.NS",
    "HAVELLS.NS", "POLYCAB.NS", "VOLTAS.NS", "BLUESTARCO.NS", "WHIRLPOOL.NS",
    "BIOCON.NS", "ALKEM.NS", "IPCALAB.NS", "LAURUSLABS.NS", "GRANULES.NS",
    "CONCOR.NS", "APOLLOTYRE.NS", "MRF.NS", "CEAT.NS", "BALKRISIND.NS",
    # ETFs
    "NIFTYBEES.NS", "BANKBEES.NS", "JUNIORBEES.NS", "GOLDBEES.NS", "ITBEES.NS",
]

# Set for O(1) lookup — use this to validate user queries
SUPPORTED_TICKERS = set(NIFTY_500_TICKERS)

def is_supported(ticker: str) -> bool:
    """Check if ticker is in our supported universe."""
    t = ticker.upper()
    if not t.endswith(".NS"):
        t = t + ".NS"
    return t in SUPPORTED_TICKERS
```

---

**2. Update app/services/stock_service.py — yfinance wrapper for Nifty 500**

Replace the existing stock_service.py with this complete implementation:

```python
import yfinance as yf
import time
import logging
from typing import Optional
from backend.data.nifty500_tickers import is_supported, SUPPORTED_TICKERS

logger = logging.getLogger(__name__)

def normalize_ticker(ticker: str) -> str:
    """Ensure ticker has .NS suffix for Indian stocks."""
    t = ticker.upper().strip()
    if not t.endswith(".NS") and not t.endswith(".BO") and not t.startswith("^"):
        t = t + ".NS"
    return t

def get_stock_info(ticker: str) -> dict:
    """
    Fetch current stock info from yfinance.
    Returns: dict with price, PE, market cap, sector, etc.
    Raises ValueError if ticker not found or not in supported universe.
    """
    t = normalize_ticker(ticker)
    
    if not is_supported(t):
        return {
            "ticker": t,
            "error": f"{t} is outside our supported stock universe (Nifty 500). "
                     f"We have limited data on this stock and cannot provide reliable analysis.",
            "supported": False
        }
    
    try:
        stock = yf.Ticker(t)
        info = stock.info
        
        if not info or info.get("regularMarketPrice") is None:
            return {"ticker": t, "error": f"No data found for {t}. Market may be closed.", "supported": True}
        
        return {
            "ticker": t,
            "name": info.get("longName", t),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "current_price": info.get("regularMarketPrice"),
            "previous_close": info.get("previousClose"),
            "change_pct": round(
                ((info.get("regularMarketPrice", 0) - info.get("previousClose", 1)) 
                 / info.get("previousClose", 1) * 100), 2
            ),
            "volume": info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "supported": True
        }
    except Exception as e:
        logger.error(f"yfinance error for {t}: {e}")
        return {"ticker": t, "error": str(e), "supported": True}

def get_stock_history(ticker: str, period: str = "1y") -> list[dict]:
    """
    Fetch OHLCV history from yfinance.
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    """
    t = normalize_ticker(ticker)
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period)
        if hist.empty:
            return []
        return [
            {
                "date": str(idx.date()),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            }
            for idx, row in hist.iterrows()
        ]
    except Exception as e:
        logger.error(f"History fetch error for {t}: {e}")
        return []

def get_stock_summary_text(ticker: str) -> Optional[str]:
    """
    Generate a text summary of a stock suitable for embedding into ChromaDB.
    Returns None if data unavailable.
    """
    info = get_stock_info(ticker)
    if "error" in info:
        return None
    
    return (
        f"Stock: {info['name']} ({info['ticker']})\n"
        f"Sector: {info['sector']} | Industry: {info['industry']}\n"
        f"Current Price: ₹{info['current_price']} | "
        f"Change: {info['change_pct']}% | "
        f"Volume: {info['volume']:,}\n"
        f"P/E Ratio: {info['pe_ratio']} | P/B Ratio: {info['pb_ratio']}\n"
        f"Market Cap: ₹{info['market_cap']:,} | "
        f"52W High: ₹{info['52w_high']} | 52W Low: ₹{info['52w_low']}\n"
        f"Dividend Yield: {info['dividend_yield']}"
    )
```

---

**3. Create app/services/bulk_ingest_service.py — Nifty 500 bulk ingestion**

```python
import time
import logging
from datetime import date
from backend.data.nifty500_tickers import NIFTY_500_TICKERS
from app.services.stock_service import get_stock_summary_text, normalize_ticker
from app.core.vectorstore import add_documents

logger = logging.getLogger(__name__)

def ingest_all_nifty500_stocks(delay_seconds: float = 0.5) -> dict:
    """
    Fetch yfinance data for all Nifty 500 tickers and embed into ChromaDB.
    
    delay_seconds: pause between API calls to avoid rate limiting.
    This will take approximately 5-10 minutes for 500 stocks.
    Run once on startup, then scheduled daily.
    
    Returns: {"success": N, "failed": M, "failed_tickers": [...]}
    """
    success = 0
    failed = 0
    failed_tickers = []
    today = str(date.today())
    
    logger.info(f"Starting Nifty 500 bulk ingest — {len(NIFTY_500_TICKERS)} tickers")
    
    for i, ticker in enumerate(NIFTY_500_TICKERS):
        try:
            summary = get_stock_summary_text(ticker)
            if summary is None:
                logger.warning(f"[{i+1}/{len(NIFTY_500_TICKERS)}] No data for {ticker}, skipping")
                failed += 1
                failed_tickers.append(ticker)
                continue
            
            add_documents(
                collection_name="stock_data",
                texts=[summary],
                metadatas=[{
                    "ticker": ticker,
                    "type": "stock_summary",
                    "date": today,
                    "source": "yfinance"
                }]
            )
            success += 1
            
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i+1}/{len(NIFTY_500_TICKERS)} stocks ingested")
            
            time.sleep(delay_seconds)
            
        except Exception as e:
            logger.error(f"Error ingesting {ticker}: {e}")
            failed += 1
            failed_tickers.append(ticker)
    
    result = {"success": success, "failed": failed, "failed_tickers": failed_tickers}
    logger.info(f"Bulk ingest complete: {result}")
    return result
```

---

**4. Update app/services/news_service.py — news ingestion with APScheduler scheduling data**

Make sure news_service.py has these batch ingestion queries ready:

```python
# Add this to news_service.py — recommended daily ingest queries
MORNING_QUERIES = [
    "Nifty Sensex Indian stock market today",
    "TCS Infosys Wipro IT sector India earnings",
    "HDFC Bank Reliance ICICI earnings results India",
]

EVENING_QUERIES = [
    "NSE BSE closing market update India today",
    "Indian economy RBI inflation interest rates stocks",
]

def ingest_news_batch(queries: list[str], limit_per_query: int = 20) -> dict:
    """
    Ingest multiple queries in one batch call.
    Returns total articles ingested across all queries.
    """
    total = 0
    for query in queries:
        result = ingest_news(query=query, limit=limit_per_query)
        total += result.get("ingested", 0)
    return {"total_ingested": total, "queries_run": len(queries)}
```

---

**5. Create app/core/scheduler.py — APScheduler setup**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

def setup_scheduler():
    """
    Register all scheduled jobs.
    Call this from app startup.
    
    Schedule (IST):
    - 9:00 AM: Morning news ingest (pre-market)
    - 6:00 PM: Evening news ingest (post-close)
    - 6:30 PM: Nifty 500 price update (after market close)
    """
    from app.services.news_service import ingest_news_batch, MORNING_QUERIES, EVENING_QUERIES
    from app.services.bulk_ingest_service import ingest_all_nifty500_stocks

    scheduler.add_job(
        func=lambda: ingest_news_batch(MORNING_QUERIES),
        trigger=CronTrigger(hour=9, minute=0),
        id="morning_news_ingest",
        name="Morning news ingest (9 AM IST)",
        replace_existing=True
    )

    scheduler.add_job(
        func=lambda: ingest_news_batch(EVENING_QUERIES),
        trigger=CronTrigger(hour=18, minute=0),
        id="evening_news_ingest",
        name="Evening news ingest (6 PM IST)",
        replace_existing=True
    )

    scheduler.add_job(
        func=ingest_all_nifty500_stocks,
        trigger=CronTrigger(hour=18, minute=30),
        id="daily_stock_update",
        name="Daily Nifty 500 price update (6:30 PM IST)",
        replace_existing=True
    )

    logger.info("Scheduler configured: morning news (9AM), evening news (6PM), stock update (6:30PM) IST")
    return scheduler
```

---

**6. Update app/main.py — add scheduler startup and shutdown**

Add these lifecycle events to the FastAPI app (keep existing health check and routers):

```python
# Add to imports at the top of main.py
from app.core.scheduler import setup_scheduler

# Add startup and shutdown events to the FastAPI app
@app.on_event("startup")
async def startup_event():
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("APScheduler started — scheduled jobs active")

@app.on_event("shutdown")
async def shutdown_event():
    from app.core.scheduler import scheduler
    scheduler.shutdown()
    logger.info("APScheduler shutdown complete")
```

Also add a new endpoint to inspect scheduler status:

```python
@app.get("/api/scheduler/jobs")
async def list_scheduled_jobs():
    from app.core.scheduler import scheduler
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "not scheduled"
        })
    return {"jobs": jobs, "total": len(jobs)}
```

---

**7. Update app/services/rag_service.py — add sparse data detection**

Add this sparse data check to the RAG chain response. After retrieving documents, before generating the answer:

```python
MIN_DOCS_FOR_CONFIDENT_ANSWER = 3

def check_retrieval_quality(docs: list, query: str) -> dict:
    """
    Assess whether retrieved docs are sufficient to answer confidently.
    Returns a warning dict if sparse.
    """
    if len(docs) == 0:
        return {
            "sparse": True,
            "warning": "No relevant documents found in our knowledge base for this query. "
                       "Try ingesting more data first with POST /api/news/ingest."
        }
    elif len(docs) < MIN_DOCS_FOR_CONFIDENT_ANSWER:
        return {
            "sparse": True,
            "warning": f"Only {len(docs)} relevant document(s) found (we recommend at least "
                       f"{MIN_DOCS_FOR_CONFIDENT_ANSWER} for a confident answer). "
                       f"Answer may be incomplete."
        }
    return {"sparse": False, "warning": None}
```

Update the RAG chain response to include this:
```python
# In rag_service.py get_rag_answer() function, update the return dict to include:
retrieval_quality = check_retrieval_quality(source_docs, query)
return {
    "answer": result["result"],
    "sources": [
        {
            "content": doc.page_content[:300],
            "metadata": doc.metadata
        }
        for doc in source_docs
    ],
    "retrieval_warning": retrieval_quality.get("warning"),
    "source_count": len(source_docs)
}
```

---

**8. Update app/api/routes/stocks.py — complete the stock endpoints**

```python
from fastapi import APIRouter, HTTPException, Query
from app.services.stock_service import get_stock_info, get_stock_history, normalize_ticker
from backend.data.nifty500_tickers import is_supported

router = APIRouter()

@router.get("/api/stocks/{ticker}")
async def get_stock(ticker: str):
    """Get current stock info for a ticker."""
    t = normalize_ticker(ticker)
    result = get_stock_info(t)
    if "error" in result and not result.get("supported", True):
        # Not in Nifty 500 — return 200 with warning, not 404
        return result
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/api/stocks/{ticker}/history")
async def get_stock_history_endpoint(
    ticker: str,
    period: str = Query(default="1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y)$")
):
    """Get OHLCV price history for a ticker."""
    t = normalize_ticker(ticker)
    history = get_stock_history(t, period=period)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for {t}")
    return {"ticker": t, "period": period, "data": history, "points": len(history)}

@router.get("/api/stocks")
async def list_supported_stocks():
    """Return list of all supported tickers (Nifty 500 universe)."""
    from backend.data.nifty500_tickers import NIFTY_500_TICKERS
    return {
        "tickers": NIFTY_500_TICKERS,
        "total": len(NIFTY_500_TICKERS),
        "note": "Only these tickers are supported in Phase 1. Other stocks will return a limited data warning."
    }

@router.post("/api/stocks/ingest/bulk")
async def trigger_bulk_ingest():
    """
    Manually trigger Nifty 500 bulk ingest.
    WARNING: Takes 5-10 minutes. Do not call this frequently.
    """
    from app.services.bulk_ingest_service import ingest_all_nifty500_stocks
    result = ingest_all_nifty500_stocks()
    return result
```

---

**9. Create tests/test_sprint2_retrieval.py — 10 test queries to verify pipeline**

```python
"""
Sprint 2 retrieval test script.
Run after bulk ingest to verify data quality.
Usage: python -m pytest tests/test_sprint2_retrieval.py -v -s
"""
import requests

BASE_URL = "http://localhost:8000"

def chat(question: str) -> dict:
    resp = requests.post(f"{BASE_URL}/api/chat", json={"message": question})
    return resp.json()

def test_large_cap_stock_info():
    """TCS should return real price data."""
    resp = requests.get(f"{BASE_URL}/api/stocks/TCS.NS")
    data = resp.json()
    assert data.get("current_price") is not None, "TCS price should not be None"
    assert data.get("pe_ratio") is not None, "TCS PE ratio should be available"
    print(f"TCS: ₹{data['current_price']} | PE: {data['pe_ratio']}")

def test_nifty50_company_rag():
    """RAG query about a large-cap stock."""
    result = chat("What is the current price and PE ratio of Reliance Industries?")
    assert len(result.get("sources", [])) > 0, "Should have sources"
    print(f"Reliance query: {result['answer'][:200]}")
    print(f"Sources: {len(result['sources'])}")

def test_it_sector_query():
    """RAG query about IT sector."""
    result = chat("How are TCS and Infosys performing in the IT sector?")
    print(f"IT sector: {result['answer'][:200]}")
    print(f"Warning: {result.get('retrieval_warning')}")

def test_banking_sector_query():
    """RAG about banking stocks."""
    result = chat("What is happening with HDFC Bank and ICICI Bank?")
    print(f"Banking: {result['answer'][:200]}")

def test_market_news_query():
    """Should retrieve news articles."""
    result = chat("What is the latest news about the Indian stock market?")
    sources = result.get("sources", [])
    print(f"News sources: {len(sources)}")
    for s in sources[:2]:
        print(f"  - {s['metadata'].get('source', 'unknown')}: {s['content'][:100]}")

def test_unsupported_ticker():
    """Mid-cap outside Nifty 500 should return warning, not crash."""
    resp = requests.get(f"{BASE_URL}/api/stocks/SOME_RANDOM_MIDCAP.NS")
    data = resp.json()
    assert data.get("supported") == False or "error" in data, "Should warn about unsupported ticker"
    print(f"Unsupported ticker response: {data.get('error', 'no error key')[:100]}")

def test_stock_history():
    """Should return OHLCV data."""
    resp = requests.get(f"{BASE_URL}/api/stocks/INFY.NS/history?period=1mo")
    data = resp.json()
    assert data.get("points", 0) > 15, "Should have at least 15 trading days in 1 month"
    print(f"Infosys history: {data['points']} data points")

def test_sparse_data_warning():
    """Asking about something obscure should trigger sparse warning."""
    result = chat("Tell me about the carbon credit trading market in India")
    print(f"Sparse warning: {result.get('retrieval_warning')}")
    # sparse warning may or may not fire depending on data — just check it doesn't crash

def test_scheduler_jobs():
    """Scheduler should have 3 jobs registered."""
    resp = requests.get(f"{BASE_URL}/api/scheduler/jobs")
    data = resp.json()
    assert data.get("total", 0) >= 3, "Should have morning news, evening news, and stock update jobs"
    for job in data["jobs"]:
        print(f"Job: {job['name']} | Next: {job['next_run']}")

def test_etf_query():
    """ETFs should be in the supported universe."""
    resp = requests.get(f"{BASE_URL}/api/stocks/NIFTYBEES.NS")
    data = resp.json()
    print(f"NiftyBEES: {data}")
    assert data.get("supported") != False, "NIFTYBEES should be in supported universe"
```

---

After creating all the above files, please:

1. Make sure `backend/data/` directory exists and has an `__init__.py`
2. Install any missing dependencies:
   ```
   pip install apscheduler
   ```
3. Verify the import structure works — run: `python -c "from backend.data.nifty500_tickers import NIFTY_500_TICKERS; print(len(NIFTY_500_TICKERS))"`
4. Start the server: `uvicorn app.main:app --reload`
5. Verify scheduler started — you should see scheduler log lines in the console
6. Trigger manual bulk ingest: `curl -X POST http://localhost:8000/api/stocks/ingest/bulk`
   (This takes 5-10 minutes — watch the logs for progress every 50 stocks)
7. After ingest finishes, run the test suite: `python -m pytest tests/test_sprint2_retrieval.py -v -s`
8. Verify `GET /api/scheduler/jobs` shows 3 scheduled jobs

Make all code production-quality with proper type hints, error handling, and logging throughout.
The `.NS` suffix must be handled consistently — normalize_ticker() should be called at the API boundary
so internals always work with normalized tickers.
```

---

## After Claude Code finishes

Verify everything in this order:

```powershell
# Terminal 1 — Ollama (already running as service, but confirm)
curl http://localhost:11434/api/tags

# Terminal 2 — Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Watch for these lines in startup logs:
# "Scheduler configured: morning news (9AM), evening news (6PM)..."
# "APScheduler started — scheduled jobs active"
```

Then test the key endpoints:

```powershell
# 1. Check scheduler is wired up
curl http://localhost:8000/api/scheduler/jobs

# 2. Trigger bulk ingest (takes 5-10 minutes — grab a coffee)
curl -X POST http://localhost:8000/api/stocks/ingest/bulk

# 3. After ingest finishes, test stock data
curl http://localhost:8000/api/stocks/TCS.NS
curl http://localhost:8000/api/stocks/INFY.NS/history?period=1mo

# 4. Test unsupported ticker warning
curl "http://localhost:8000/api/stocks/SOME_RANDOM.NS"

# 5. Run retrieval test suite
python -m pytest tests/test_sprint2_retrieval.py -v -s

# 6. Commit when green
git add .
git commit -m "Sprint 2 complete: Nifty 500 pipeline, APScheduler, sparse data detection"
```

---

## Sprint 2 Troubleshooting

**yfinance returns None for current_price**  
Market is closed — yfinance returns None outside NSE trading hours (9:15 AM–3:30 PM IST weekdays). Test during market hours, or check `previousClose` which is always available.

**APScheduler logs show "Execution of job missed"**  
The server was down when the scheduled time hit. That's fine — jobs run on next scheduled time. No data loss.

**Bulk ingest hangs at a specific ticker**  
yfinance occasionally hangs on delisted tickers. Add a timeout: `yf.Ticker(t).info` has no built-in timeout — wrap in a threading timeout if this becomes a problem. For now, just Ctrl+C and restart — the ChromaDB writes that completed before the hang are persisted.

**"ModuleNotFoundError: No module named 'backend'"**  
You need to run uvicorn from the project root, not from inside backend/. The import path `from backend.data.nifty500_tickers import ...` assumes the project root is in the Python path. Fix: `cd finance-assistant` then `uvicorn backend.app.main:app --reload` OR add a `pyproject.toml` with the package config.

**ChromaDB has duplicate stock data after multiple ingests**  
Expected — each bulk ingest adds new documents. ChromaDB doesn't deduplicate by default. For Phase 1 this is fine (latest data just gets more weight). In Phase 2 we'll add upsert logic with ticker+date as the unique key.

**Only 80/100 stocks ingested successfully**  
Normal. Some tickers (especially newly listed or recently delisted) return empty data from yfinance. The `failed_tickers` list in the bulk ingest response shows which ones. Don't chase every failure — 80%+ coverage is good enough for Sprint 2.
