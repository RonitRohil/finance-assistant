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
