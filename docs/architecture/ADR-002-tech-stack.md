# ADR-002: Tech Stack Decision

**Status:** Accepted  
**Date:** April 2026  
**Deciders:** Ronit Jain  

---

## Context

We need to choose the full technology stack for FinanceAssistant. Key constraints:

- Free or near-free to run locally
- Python-friendly (best AI/ML ecosystem)
- Should be learnable and portfolio-worthy
- Must support async data ingestion (stock prices, news updates)
- Frontend needs charting capabilities (stock prices, portfolio graphs)

---

## Decision: The Chosen Stack

```
Layer              | Technology          | Why
─────────────────────────────────────────────────────────────────
Backend API        | FastAPI (Python)    | Best AI/ML ecosystem, async, auto docs
AI / RAG           | LangChain           | Industry standard, great abstractions
LLM                | Claude API          | Best reasoning, structured output
Embeddings         | sentence-transformers| Free, runs locally, no API cost
Vector Store       | ChromaDB → Qdrant   | Local first, migrate later
Relational DB      | SQLite → PostgreSQL  | Zero setup locally, migrate for cloud
Frontend           | Next.js + TypeScript | Full-stack, great dashboard libs
Charts             | Recharts / TradingView Lightweight | Financial charts
Styling            | Tailwind CSS        | Fast, consistent UI
Task Scheduler     | APScheduler (Phase 1) → Celery (Phase 2) | Background ingestion
Containerization   | Docker + Docker Compose | Reproducible local dev
```

---

## Backend: FastAPI

### Why FastAPI over Flask, Django, Node/Express?

**vs Flask**: FastAPI is async by default, which matters enormously for I/O-heavy tasks like fetching stock prices, calling LLMs, and reading from vector DBs simultaneously. Flask is synchronous by default. FastAPI also gives you automatic OpenAPI docs, which is great for debugging and for when you want to let family members integrate.

**vs Django**: Django is overkill — it's designed for CMS-style apps with complex ORMs. We don't need that weight. FastAPI gives us what we need with far less boilerplate.

**vs Node/Express**: Python wins decisively for AI/ML. Every AI library (LangChain, sentence-transformers, yfinance, pandas) is Python-native. Running them from Node means subprocess calls or separate services — not worth it.

```python
# FastAPI example — this is how clean the code looks
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class StockQuery(BaseModel):
    question: str
    ticker: str | None = None

@app.post("/ask")
async def ask_finance_question(query: StockQuery):
    answer = await rag_chain.ainvoke(query.question)
    return {"answer": answer}
```

---

## AI/RAG Layer: LangChain

LangChain is the most widely adopted RAG framework. It provides:

- **Document loaders**: Load PDFs, web pages, CSV files, APIs into a standard format
- **Text splitters**: Chunk documents intelligently for embedding
- **Embedding integrations**: Plug in any embedding model
- **Vector store integrations**: ChromaDB, Qdrant, Pinecone — all one interface
- **Chains**: Pre-built RAG patterns (RetrievalQA, ConversationalRetrievalChain)
- **Agents**: Tool-using AI that can call yfinance, do math, search news

```python
# The entire RAG pipeline in ~10 lines
from langchain.chains import RetrievalQA
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma

llm = ChatAnthropic(model="claude-haiku-4-5")
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

answer = qa_chain.invoke("What was Reliance's revenue last quarter?")
```

---

## LLM Strategy: Two-Phase Approach

We use different LLMs for development vs production. This keeps development completely free while ensuring production quality.

### Phase 1 (Development): Ollama — local, free, offline

**Ollama** runs open-source LLMs directly on your machine. No API key, no internet connection needed, no cost ever.

**Environment**: Windows 11, 16GB RAM  
**Recommended models** (in order of preference):

| Model | Size on disk | RAM needed | Speed | Quality |
|-------|-------------|------------|-------|---------|
| `mistral:7b` | 4.1 GB | ~6 GB | Fast | Great for finance Q&A |
| `llama3.1:8b` | 4.7 GB | ~7 GB | Fast | Excellent reasoning |
| `llama3.2:3b` | 2.0 GB | ~3 GB | Very fast | Good for quick tests |

**Recommended**: Start with `mistral:7b` — best balance of quality and speed for financial text.

```bash
# Install Ollama on Windows: download from https://ollama.com
# Then pull the model (one-time download):
ollama pull mistral

# Verify it works:
ollama run mistral "What is a P/E ratio?"
```

**LangChain integration** — Ollama uses the exact same interface as Claude:

```python
# Development (free, local, Ollama)
from langchain_ollama import OllamaLLM
llm = OllamaLLM(model="mistral", temperature=0)

# Production (swap this one line, everything else stays identical)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-haiku-4-5", temperature=0)
```

We handle this with an environment variable so switching is automatic:

```python
# app/core/llm.py
import os
from langchain_ollama import OllamaLLM
from langchain_anthropic import ChatAnthropic

def get_llm():
    env = os.getenv("LLM_PROVIDER", "ollama")  # default to ollama
    if env == "ollama":
        return OllamaLLM(model=os.getenv("OLLAMA_MODEL", "mistral"), temperature=0)
    elif env == "anthropic":
        return ChatAnthropic(model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5"), temperature=0)
    raise ValueError(f"Unknown LLM_PROVIDER: {env}")
```

`.env` file controls which LLM is active — no code changes needed:
```env
# .env (development)
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral

# .env (production)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-haiku-4-5
```

### Phase 2+ (Production): Claude API (Anthropic)

When deploying to cloud or sharing with family, switch to Claude API. Specific models:

- **claude-haiku-4-5**: Fast and cheap — simple stock lookups, news summaries, routine Q&A
- **claude-sonnet-4-6**: Smarter — complex portfolio analysis, multi-stock comparisons

Cost estimate: 1000 questions/month on haiku ≈ $1–2. Very manageable.

### Why Ollama over other free options?
- **vs Groq free tier**: Groq has rate limits (30 req/min) that break scheduled ingestion jobs. Ollama is unlimited.
- **vs Google Gemini free**: API key required, internet needed, privacy concern with financial data.
- **vs Hugging Face inference**: Slower, rate-limited, internet-dependent.
- **Ollama wins**: Truly offline, unlimited, fast enough on 16GB RAM, and teaches you how local LLMs work — a valuable skill.

---

## Embeddings: sentence-transformers (free, local)

Embeddings convert text into vectors so we can do semantic search in ChromaDB.

**Model chosen**: `all-MiniLM-L6-v2`  
- 384-dimensional vectors
- Runs on CPU (no GPU needed)
- Free forever, no API calls
- Good enough for financial text retrieval

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Reliance Q4 revenue beat expectations")
# Returns a 384-dimensional vector like [0.23, -0.11, 0.87, ...]
```

**Alternative**: OpenAI `text-embedding-ada-002` — better quality but costs money per embedding call. Switch to this in Phase 2 if retrieval quality feels lacking.

---

## Frontend: Next.js + TypeScript

Next.js gives us:
- React for UI components
- Server-side rendering (useful for SEO if we ever make it public)
- API routes (can proxy calls to FastAPI)
- File-based routing (easy to add new pages)
- TypeScript for catching bugs early

Key libraries on top:
- **Recharts** or **TradingView Lightweight Charts** — stock price charts
- **Tailwind CSS** — utility-first styling, fast to build with
- **SWR or React Query** — data fetching with caching
- **shadcn/ui** — pre-built accessible components

---

## Database: SQLite → PostgreSQL

### Phase 1 (local): SQLite
- Zero setup — just a file
- Perfect for: portfolio holdings, watchlists, transaction history, user settings
- Python's built-in `sqlite3` or SQLAlchemy ORM

### Phase 2 (cloud): PostgreSQL
- When we deploy and add family users, we need a proper DB
- Free options: Supabase (512MB free), Railway, Render

---

## What we are NOT using (and why)

| Technology | Reason skipped |
|-----------|----------------|
| Redis (Phase 1) | Overkill locally. APScheduler handles scheduled jobs fine. Add in Phase 2. |
| GraphQL | REST is simpler. No need for GraphQL complexity at this scale. |
| Kafka / message queues | Same — too heavy for local dev. |
| Kubernetes | Way too early. Docker Compose is enough. |
| Microservices | Monolith first. Split only when there's a real reason. |

---

## Windows-Specific Setup Notes

Since we're on Windows, a few things are different from Linux/Mac guides you'll find online:

```bash
# Python virtual environment on Windows
python -m venv venv
venv\Scripts\activate          # NOT source venv/bin/activate

# Running uvicorn
uvicorn app.main:app --reload  # same command, works fine on Windows

# ChromaDB works fine on Windows without Docker in Phase 1
# Qdrant (Phase 2) needs Docker Desktop for Windows
```

Recommend installing **Git Bash** or **WSL2** if you want Linux-style commands. Either works — the code is identical.

---

## Action Items

- [x] Decide LLM strategy: Ollama (dev) → Claude API (production)
- [ ] Install Ollama on Windows: https://ollama.com
- [ ] Pull mistral model: `ollama pull mistral`
- [ ] Initialize FastAPI project with requirements.txt
- [ ] Set up Next.js app with TypeScript + Tailwind
- [ ] Configure LangChain with Ollama (get_llm() factory function)
- [ ] Download sentence-transformers model locally (auto-downloads on first run)
- [ ] Set up Docker Compose for local dev (optional in Phase 1)
