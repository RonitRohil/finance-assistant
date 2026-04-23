# Study Notes: Embeddings

**Topic**: What embeddings are, how they work, and which to use  
**Prerequisites**: Read `01-rag-fundamentals.md` and `02-vector-databases.md`

---

## What Are Embeddings?

An embedding is a **numerical representation of meaning**. It converts text into a list of numbers (a vector) such that text with similar meaning produces vectors that are close together in space.

```
"Reliance Industries revenue grew 11% this quarter"
         ↓ embedding model
[0.23, -0.11, 0.87, 0.04, -0.55, 0.19, ... (384 numbers)]

"Reliance Q4 profit beats analyst estimates"
         ↓ embedding model
[0.21, -0.09, 0.84, 0.07, -0.51, 0.22, ... (384 numbers)]

"Today's weather in Mumbai is sunny"
         ↓ embedding model
[-0.12, 0.67, -0.23, 0.91, 0.14, -0.08, ... (384 numbers)]
```

The first two vectors are close together (both about Reliance financials).  
The third is far away (weather, unrelated topic).

This is how semantic search works — we find documents whose embeddings are close to the query embedding.

---

## The Intuition: Meaning Lives in Geometry

Think of embeddings as coordinates in a very high-dimensional map. Words and sentences that mean similar things cluster together:

```
In the "concept space":

Financial terms cluster:
  "revenue" ~ "turnover" ~ "sales" ~ "income"

Company clusters:
  "TCS", "Infosys", "Wipro" are near each other (IT companies)
  "Reliance", "ONGC", "BPCL" are near each other (energy/diversified)

Action clusters:
  "grew" ~ "increased" ~ "rose" ~ "surged" ~ "jumped"
  "fell" ~ "declined" ~ "dropped" ~ "plummeted"
```

This is why searching for "IT company quarterly earnings" retrieves documents containing "tech firm Q4 results" — they're close in embedding space even though no exact words match.

---

## How Embedding Models Work (Simplified)

Embedding models are neural networks trained on massive amounts of text. They learn to:
- Map text → dense vector
- Ensure similar text → similar vectors
- Ensure different text → different vectors

Training objective: Given sentences A and B that mean the same thing, their vectors should be close. Given sentences A and C that mean different things, their vectors should be far.

This is called **contrastive learning** — you train by showing the model pairs of similar and dissimilar sentences.

---

## The Embedding Models We Use

### Phase 1: `all-MiniLM-L6-v2` (sentence-transformers)

**What it is**: A small, fast transformer model trained for sentence similarity.

**Key specs**:
- Output dimensions: 384
- Context limit: 256 tokens (~190 words)
- Speed: ~14,000 sentences/second on CPU
- Cost: Free forever, runs locally

**How to use**:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Single sentence
embedding = model.encode("TCS Q4 revenue grew 15%")
print(embedding.shape)  # (384,)
print(embedding[:5])    # [0.234, -0.112, 0.876, 0.043, -0.551]

# Batch (much faster)
sentences = [
    "TCS Q4 revenue grew 15%",
    "Infosys narrows guidance for FY25",
    "Nifty 50 hits 22,000 mark"
]
embeddings = model.encode(sentences)
print(embeddings.shape)  # (3, 384)
```

**Limitation**: The 256-token context limit means if your chunk is longer than ~190 words, it gets truncated. Always chunk your documents before embedding.

### Phase 2: OpenAI `text-embedding-ada-002`

**What it is**: OpenAI's embedding model, significantly better quality than MiniLM.

**Key specs**:
- Output dimensions: 1536
- Context limit: 8191 tokens
- Cost: $0.0001 per 1000 tokens (~$0.10 per million tokens)
- Quality: Substantially better for financial text

**When to upgrade**: When your retrieval quality feels off — you're getting irrelevant chunks returned. The MiniLM model is good enough for Phase 1, but ada-002 meaningfully improves precision.

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    input="TCS Q4 revenue grew 15%",
    model="text-embedding-ada-002"
)
embedding = response.data[0].embedding
print(len(embedding))  # 1536
```

**Important**: If you switch from MiniLM to ada-002, you MUST re-embed ALL documents in ChromaDB. Mixing embeddings from different models in the same collection will produce garbage results.

---

## Chunking Strategy for Financial Text

Before embedding, you need to split documents into chunks. The chunking strategy significantly affects retrieval quality.

### LangChain RecursiveCharacterTextSplitter

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # ~500 characters per chunk
    chunk_overlap=50,      # 50 char overlap between chunks
    separators=["\n\n", "\n", ". ", " "]  # Try these splits in order
)

text = """
Tata Consultancy Services reported strong Q4 FY24 results with revenue 
growing 15.4% year-on-year to ₹61,237 crore. The company's EBIT margin 
improved to 26.1% from 24.5% in the same quarter last year.

The BFSI vertical was the strongest performer, contributing 32% of total 
revenue. Management cited continued demand for cloud transformation and 
AI integration projects as key growth drivers.

TCS declared a final dividend of ₹28 per share and announced a ₹17,000 
crore share buyback program at ₹4,150 per share.
"""

chunks = splitter.split_text(text)
# ['Tata Consultancy Services reported strong Q4 FY24 results with revenue...', 
#  'The BFSI vertical was the strongest performer...', 
#  'TCS declared a final dividend...']
```

### Chunking Guidelines for Financial Documents

| Document Type | Recommended Chunk Size | Notes |
|--------------|----------------------|-------|
| News articles | 400–600 chars | Usually short, don't over-split |
| Earnings reports | 600–800 chars | Rich in numbers, keep context |
| Analyst notes | 500–700 chars | Dense information |
| Stock summaries | 300–400 chars | Keep as one or two chunks |
| Annual reports | 800–1000 chars | Long, need bigger chunks |

Always add meaningful metadata to each chunk:
```python
chunks_with_metadata = [
    {
        "text": chunk,
        "metadata": {
            "ticker": "TCS.NS",
            "source_doc": "Q4_FY24_earnings_release",
            "chunk_index": i,
            "date": "2024-04-18",
            "type": "earnings_report"
        }
    }
    for i, chunk in enumerate(chunks)
]
```

---

## Measuring Embedding Quality

How do you know if your embeddings are working well?

### Method 1: Manual inspection
Take 5 queries you care about, run retrieval, read the returned chunks. Are they relevant? This is the fastest check.

### Method 2: Cosine similarity inspection
```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# These should have HIGH similarity
a = model.encode(["TCS quarterly revenue growth"])
b = model.encode(["Tata Consultancy Q4 earnings increase"])
print(cosine_similarity(a, b))  # Should be > 0.8

# These should have LOW similarity
c = model.encode(["Mumbai weather forecast"])
print(cosine_similarity(a, c))  # Should be < 0.3
```

### Method 3: Retrieval evaluation
Create a test set: 20 questions + their expected answers. For each question, run retrieval and check if the expected document is in the top-5. Track this as a metric called **Recall@5**.

---

## Embedding Pitfalls

**Don't embed very long documents without chunking**. At 256 tokens, MiniLM truncates. The last 80% of a long document gets ignored. Always chunk first.

**Don't mix embedding models in one collection**. If you embed some documents with MiniLM and query with OpenAI, the vectors live in different geometric spaces. Similarity scores will be wrong.

**Don't embed raw HTML or PDFs directly**. Extract clean text first. Tables, code blocks, and repeated headers contaminate the embedding.

**Token != Character**. 1 token ≈ 4 characters in English. A 256-token limit = ~1024 characters ≈ ~180 words. Financial numbers and terms are roughly similar.

---

## Quick Reference: Embedding Models Compared

| Model | Dimensions | Max Tokens | Cost | Quality | Best For |
|-------|-----------|-----------|------|---------|----------|
| all-MiniLM-L6-v2 | 384 | 256 | Free | Good | Phase 1, fast prototyping |
| all-mpnet-base-v2 | 768 | 384 | Free | Better | Upgrade if MiniLM not enough |
| text-embedding-ada-002 | 1536 | 8191 | $0.0001/1K tokens | Best | Phase 2, production |
| text-embedding-3-small | 1536 | 8191 | $0.00002/1K tokens | Great | Best value paid option |

---

*You now understand the three core concepts: RAG, vector databases, and embeddings. You're ready to start building.*

*Next when building: start with `ADR-002-tech-stack.md` setup instructions.*
