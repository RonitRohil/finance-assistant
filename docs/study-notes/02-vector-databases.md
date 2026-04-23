# Study Notes: Vector Databases

**Topic**: What vector databases are, how they work, and how we use ChromaDB and Qdrant  
**Prerequisites**: Read `01-rag-fundamentals.md` first

---

## What is a Vector Database?

A regular database stores structured data: rows, columns, integers, strings. You query it with exact matches or ranges: `WHERE price > 100 AND sector = 'IT'`.

A vector database stores **high-dimensional vectors** and answers questions like: *"Which vectors are most similar to this query vector?"*

This is fundamentally different — there are no exact matches. Everything is about *distance* and *similarity*.

Think of it this way: in a normal DB, you find the exact record. In a vector DB, you find the most *semantically similar* records.

---

## How Similarity Search Works Internally

Imagine you have 3-dimensional vectors (real ones have 384 or 1536 dimensions, but 3D is easier to visualize):

```
Documents stored:
  Doc A: [0.9, 0.1, 0.2]  ← "TCS Q4 revenue grew 15%"
  Doc B: [0.8, 0.2, 0.1]  ← "Infosys revenue increased 12% this quarter"
  Doc C: [0.1, 0.9, 0.8]  ← "Reliance retail business expansion news"

Query: "IT company earnings results"
Query vector: [0.85, 0.15, 0.15]

Distances:
  To Doc A: cosine similarity = 0.98  ← Very similar (both about IT earnings)
  To Doc B: cosine similarity = 0.97  ← Very similar
  To Doc C: cosine similarity = 0.24  ← Not similar (retail, not IT)

Top 2 results: Doc A, Doc B  ✓ Correct!
```

The database does this comparison efficiently across millions of vectors using **Approximate Nearest Neighbor (ANN)** algorithms — specifically HNSW (Hierarchical Navigable Small World), which is what ChromaDB and Qdrant both use.

---

## ChromaDB — Deep Dive

### How ChromaDB Stores Data

ChromaDB organizes data into **Collections** (similar to tables in SQL).

Each item in a collection has:
- **ID**: unique identifier
- **embedding**: the vector (list of numbers)
- **document**: the original text
- **metadata**: key-value pairs (ticker, date, source, etc.)

```python
import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB (persists to local file)
client = chromadb.PersistentClient(path="./chroma_db")

# Create a collection with embedding function
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.create_collection(
    name="stock_news",
    embedding_function=embedding_fn
)
```

### Adding Documents

```python
# Add documents (ChromaDB auto-generates embeddings)
collection.add(
    ids=["news_001", "news_002", "news_003"],
    documents=[
        "TCS Q4 FY24 revenue grew 15.4% to ₹61,237 crore driven by BFSI and hi-tech verticals",
        "Infosys narrows FY25 revenue guidance to 3.5-4% citing macro uncertainty in US markets",
        "Reliance Industries planning major retail expansion in tier-2 cities by 2026"
    ],
    metadatas=[
        {"ticker": "TCS.NS", "date": "2024-04-18", "source": "moneycontrol", "type": "earnings"},
        {"ticker": "INFY.NS", "date": "2024-04-12", "source": "economictimes", "type": "guidance"},
        {"ticker": "RELIANCE.NS", "date": "2024-04-15", "source": "businessstandard", "type": "expansion"}
    ]
)
```

### Querying

```python
# Simple semantic search
results = collection.query(
    query_texts=["IT company quarterly results"],
    n_results=2
)

print(results['documents'])   # [["TCS Q4 FY24...", "Infosys narrows..."]]
print(results['metadatas'])   # ticker, date, source
print(results['distances'])   # similarity scores

# Query with metadata filter (only get TCS news)
results = collection.query(
    query_texts=["revenue growth"],
    n_results=3,
    where={"ticker": "TCS.NS"}  # Metadata filter
)

# Date range filter
results = collection.query(
    query_texts=["earnings"],
    n_results=5,
    where={"$and": [
        {"date": {"$gte": "2024-01-01"}},
        {"date": {"$lte": "2024-12-31"}}
    ]}
)
```

### ChromaDB Architecture Internals

```
ChromaDB on disk:
├── chroma_db/
│   ├── chroma.sqlite3          ← Metadata store (IDs, document text, metadata)
│   └── [collection_id]/
│       ├── data_level0.bin     ← HNSW index (the actual vector index)
│       └── header.bin          ← Index metadata
```

When you query, ChromaDB:
1. Embeds your query text using the embedding function
2. Searches the HNSW index to find approximate nearest neighbors
3. Fetches the document text and metadata from SQLite
4. Returns ranked results

---

## Qdrant — Phase 2 Vector DB

Qdrant is more production-ready than ChromaDB. Run it with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Key Advantages Over ChromaDB

1. **Better filtering**: Qdrant has a rich payload filter system — filter by date ranges, multiple conditions, nested fields
2. **Hybrid search**: Combines vector search with full-text (BM25) search for better retrieval
3. **Larger scale**: Handles hundreds of millions of vectors
4. **Named vectors**: Store multiple vectors per point (e.g., title embedding + body embedding)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="stock_news",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Insert points
client.upsert(
    collection_name="stock_news",
    points=[
        PointStruct(
            id=1,
            vector=[0.23, -0.11, 0.87, ...],  # 384 dims
            payload={
                "text": "TCS Q4 revenue grew 15.4%...",
                "ticker": "TCS.NS",
                "date": "2024-04-18",
                "source": "moneycontrol"
            }
        )
    ]
)

# Search with filter
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="stock_news",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[FieldCondition(key="ticker", match=MatchValue(value="TCS.NS"))]
    ),
    limit=5
)
```

---

## ChromaDB vs Qdrant — When to Use Which

| Situation | Use |
|-----------|-----|
| Learning / prototyping | ChromaDB |
| < 100K vectors, local use | ChromaDB |
| Need advanced date/ticker filtering | Qdrant |
| > 100K vectors | Qdrant |
| Deploying to cloud | Qdrant |
| Need hybrid (vector + keyword) search | Qdrant |
| Prefer zero Docker setup | ChromaDB |

---

## Our Collections Plan

```
ChromaDB (Phase 1):
├── stock_news        → News articles, press releases, market commentary
├── stock_data        → Daily summaries, price + volume + key metrics
├── earnings_reports  → Quarterly/annual results, management commentary
└── etf_data          → NAV history, fund summaries, holdings changes

Qdrant (Phase 2, same collections):
Same structure, but with richer payload filtering and hybrid search
```

---

## Troubleshooting ChromaDB

**Problem**: Query returns irrelevant results  
**Diagnosis**: Print the distance scores — if all scores are between 0.4–0.6, your embedding model may not be good enough for financial text. Consider upgrading to OpenAI embeddings.

**Problem**: ChromaDB is slow  
**Diagnosis**: Check collection size with `collection.count()`. If > 50K, time to migrate to Qdrant.

**Problem**: After re-starting, data is gone  
**Fix**: Make sure you're using `PersistentClient` with `path` argument, not `EphemeralClient`.

**Problem**: Metadata filter returns no results  
**Fix**: Check that metadata keys match exactly (case-sensitive). Print `collection.get(limit=1)` to see actual metadata format.

---

## Quick Reference: ChromaDB API

```python
# Create client
client = chromadb.PersistentClient(path="./chroma_db")

# Collection operations
collection = client.create_collection("name")       # Create
collection = client.get_collection("name")          # Get existing
collection = client.get_or_create_collection("name")# Safe get/create
client.delete_collection("name")                    # Delete

# Document operations
collection.add(ids=[...], documents=[...], metadatas=[...])  # Add
collection.upsert(ids=[...], documents=[...])                # Add or update
collection.delete(ids=["id1", "id2"])                        # Delete by ID
collection.get(ids=["id1"])                                  # Get by ID

# Query
collection.query(query_texts=["..."], n_results=5)           # Semantic search
collection.query(query_texts=["..."], where={"key": "val"}) # Filtered search
collection.count()                                           # Total documents
```

---

*Next: Read `03-embeddings.md` to understand how text gets converted to vectors.*
