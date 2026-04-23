# ADR-003: Vector Database Selection

**Status:** Accepted  
**Date:** April 2026  
**Deciders:** Ronit Jain  

---

## Context

The vector database is the heart of our RAG system. It stores embeddings (numerical representations) of all our financial documents — news articles, earnings reports, stock summaries, analyst notes. When the user asks a question, we search this database to find the most relevant documents and pass them to Claude as context.

We need to choose which vector database to use. The options evaluated:

1. **ChromaDB** — open-source, runs in-process or as a server, zero config
2. **Qdrant** — open-source, Docker-based, production-grade, excellent filtering
3. **Pinecone** — fully managed cloud, excellent performance, paid
4. **FAISS** — Facebook's library, purely in-memory, no persistence without custom code
5. **Weaviate** — open-source, has hybrid search, more complex setup

---

## Decision: ChromaDB (Phase 1) → Qdrant (Phase 2+)

### Phase 1: ChromaDB
Use ChromaDB locally while building and learning. It runs inside your Python process — no separate server to manage. Perfect for fast iteration.

### Phase 2: Qdrant
When we add more data, need better filtering (e.g., "only retrieve news from the last 7 days about HDFC Bank"), or deploy to cloud — switch to Qdrant running in Docker.

---

## Detailed Comparison

| Dimension | ChromaDB | Qdrant | Pinecone | FAISS |
|-----------|----------|--------|----------|-------|
| Setup effort | Zero — pip install | Docker run | Sign up + API key | Zero |
| Persistence | Yes (local file) | Yes (Docker volume) | Yes (cloud) | Manual |
| Filtering | Basic | Excellent | Good | None |
| Scale | Small-medium | Large | Very large | Medium |
| Cost | Free forever | Free (self-hosted) | Free tier: 1 index | Free |
| Production-ready | Partial | Yes | Yes | No |
| LangChain support | Yes | Yes | Yes | Yes |
| Learning curve | Very low | Low | Very low | Medium |

---

## Why NOT Pinecone for Phase 1?

Pinecone's free tier gives you 1 index with 100K vectors. That sounds like a lot until you realize:
- Each news article = ~5–20 chunks = 5–20 vectors
- 1 month of Indian stock news = thousands of articles
- You'll hit the limit quickly and start paying

More importantly — running a managed cloud DB while developing locally adds latency and requires internet. ChromaDB is instant.

---

## Why NOT FAISS?

FAISS is a pure library — it has no persistence, no server, no filtering. You'd have to build save/load logic yourself, and there's no metadata filtering (critical for "give me only news from this week"). Not worth it.

---

## How ChromaDB Works (Conceptual)

```
Document: "Reliance Industries Q4 FY24 revenue grew 11% YoY to ₹2.3L Cr..."

Step 1 — Chunking:
  Chunk 1: "Reliance Industries Q4 FY24 revenue grew 11% YoY to ₹2.3L Cr"
  Chunk 2: "Jio segment contributed ₹24,000 Cr to consolidated EBITDA..."
  Chunk 3: "Retail business saw 16% growth driven by strong footfall..."

Step 2 — Embedding (sentence-transformers):
  Chunk 1 → [0.23, -0.11, 0.87, ... 384 numbers]
  Chunk 2 → [0.54, 0.21, -0.33, ... 384 numbers]
  Chunk 3 → [0.18, 0.67, 0.02, ... 384 numbers]

Step 3 — Store in ChromaDB with metadata:
  {
    "vector": [0.23, -0.11, 0.87, ...],
    "text": "Reliance Industries Q4 FY24 revenue grew...",
    "metadata": {
      "ticker": "RELIANCE.NS",
      "source": "earnings_report",
      "date": "2024-04-28",
      "type": "earnings"
    }
  }

Step 4 — Query time ("What was Reliance's revenue?"):
  User question → embed → [0.25, -0.09, 0.84, ...]
  ChromaDB: find top 5 vectors closest to this query vector
  Returns: the 5 most relevant chunks
  Feed to Claude as context → Claude answers accurately
```

---

## Collections Strategy (how we organize data in ChromaDB)

We'll use separate collections for different data types so retrieval stays focused:

```
Collections:
├── stock_news          ← news articles, press releases
├── earnings_reports    ← quarterly results, annual reports
├── stock_summaries     ← daily price summaries, key metrics
├── etf_data            ← ETF NAV, holdings, fund summaries
└── personal_notes      ← user's own notes about stocks (Phase 2)
```

At query time, we retrieve from the relevant collection(s) based on query type.

---

## Migration Plan: ChromaDB → Qdrant

When to switch:
- Total vectors exceed ~50K (ChromaDB slows down)
- We need advanced payload filtering (date ranges, ticker-specific retrieval)
- We deploy to cloud

Migration script (one-time): read all documents from ChromaDB, re-insert into Qdrant. LangChain abstracts the interface so the RAG chain code doesn't change — just swap the vectorstore object.

```python
# Phase 1 — ChromaDB
from langchain_community.vectorstores import Chroma
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Phase 2 — Qdrant (only this line changes)
from langchain_community.vectorstores import Qdrant
vectorstore = Qdrant(client=qdrant_client, collection_name="finance_docs", embeddings=embeddings)

# Everything else (retriever, chain, etc.) stays identical
```

---

## Action Items

- [ ] Install ChromaDB: `pip install chromadb`
- [ ] Create ChromaDB collections for stock_news and earnings_reports
- [ ] Write ingestion script to embed and store news articles
- [ ] Test similarity search with 10 sample queries
- [ ] Document Qdrant Docker setup for Phase 2 migration reference
