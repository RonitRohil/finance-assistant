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

## LLM: Claude API (Anthropic)

We're using Anthropic's Claude API. Specific models:

- **claude-haiku-4-5**: Fast and cheap — use for simple stock lookups, news summaries, routine Q&A
- **claude-sonnet-4-6**: Smarter — use for complex portfolio analysis, multi-stock comparisons, financial reasoning

### Cost estimate for local use
At haiku pricing, 1000 questions/month ≈ $1–2. Sonnet ≈ $5–10. Very manageable.

### Why not OpenAI GPT-4?
Claude has better reasoning on financial documents and is better at following structured output instructions. Also, you're already using Claude products — keeping consistency makes sense.

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

## Action Items

- [ ] Initialize FastAPI project with pyproject.toml / requirements.txt
- [ ] Set up Next.js app with TypeScript + Tailwind
- [ ] Configure LangChain with Claude API key
- [ ] Download sentence-transformers model locally
- [ ] Set up Docker Compose for local dev
