# Study Notes: RAG Fundamentals

**Topic**: Retrieval-Augmented Generation  
**Why this matters for our project**: RAG is the entire foundation of FinanceAssistant. Understanding it deeply will help you debug, improve, and explain the system.

---

## The Core Problem RAG Solves

When you ask an LLM like Claude or ChatGPT a question, it answers from its training data — knowledge frozen at a point in time. Two big problems:

1. **Stale data**: Training ended months or years ago. Stock prices, earnings, news — all outdated.
2. **Hallucination**: LLMs sometimes confidently make up facts that aren't real.

RAG fixes both by giving the LLM real, fresh documents at query time instead of relying on memorized knowledge.

---

## The RAG Pipeline — Step by Step

### Phase A: Ingestion (happens offline, on a schedule)

```
Raw Data                    Processing                  Storage
──────────                  ──────────                  ───────
News Article      →  Split into chunks  →  Embed each chunk  →  Store in Vector DB
Earnings Report   →  Split into chunks  →  Embed each chunk  →  Store in Vector DB
Stock Summary     →  Split into chunks  →  Embed each chunk  →  Store in Vector DB
```

**Chunking** means breaking a long document into smaller pieces. Why? Because embedding and retrieving a 50-page annual report as one unit doesn't work — you want to retrieve the specific paragraph about revenue, not the whole document.

Good chunk size for financial text: **500–800 tokens** (about 2–3 paragraphs), with **50-token overlap** between chunks so context isn't cut off mid-sentence.

### Phase B: Retrieval + Generation (happens at query time)

```
User Question
     ↓
Embed the question using the same embedding model
     ↓
Search vector DB for top-K most similar chunks
     ↓
Retrieve those chunks (the "context")
     ↓
Build a prompt:
  "You are a financial assistant. Answer based on this context:
   [retrieved chunks]
   Question: [user question]"
     ↓
Send prompt to LLM (Claude)
     ↓
LLM generates answer grounded in the retrieved context
     ↓
Return answer + source citations to user
```

---

## What Makes a Good RAG System

### 1. Retrieval quality (most important)
If you retrieve the wrong chunks, the LLM has wrong context and gives a wrong answer. Garbage in, garbage out. Ways to improve:

- **Better chunking**: Domain-aware splitting (e.g., split earnings reports by section, not just character count)
- **Better embeddings**: OpenAI ada-002 > sentence-transformers > bag-of-words
- **Hybrid search**: Combine semantic search (vector similarity) with keyword search (BM25). Qdrant has this built in.
- **Metadata filtering**: Only retrieve documents relevant to the query's time period or ticker

### 2. Context quality
The retrieved chunks need to actually contain the answer. If your question is "What was TCS revenue in Q4 FY24?" but you only ingested news articles and not earnings reports, retrieval fails.

**Lesson**: Data coverage matters as much as the RAG pipeline itself.

### 3. Prompt engineering
How you wrap the retrieved context in your prompt affects output quality significantly.

```python
# Bad prompt — no structure, LLM might hallucinate
prompt = f"Answer this: {question}"

# Good prompt — clear instructions, grounded in sources
prompt = f"""You are a financial analyst assistant. Your job is to answer questions 
about stocks using ONLY the provided context below. 

If the context doesn't contain enough information to answer the question, 
say "I don't have enough data to answer this" — never make up information.

Context:
{retrieved_context}

Question: {question}

Answer (include which sources you used):"""
```

---

## Key Terms You'll Encounter

**Embedding**: A numerical vector (list of numbers) that represents the "meaning" of a piece of text. Texts with similar meaning have similar vectors. This is what enables semantic search.

**Vector**: Just an array of numbers. `[0.23, -0.11, 0.87, 0.04, ...]`. In our system, each vector has 384 dimensions (sentence-transformers) or 1536 dimensions (OpenAI).

**Similarity search**: Finding vectors in the database that are "closest" to a query vector. "Closest" is measured by cosine similarity or dot product.

**Cosine similarity**: A measure of angle between two vectors. Score from -1 to 1. Score of 1 = identical meaning. Score of 0 = unrelated. Score of -1 = opposite meaning.

**Top-K retrieval**: We ask the vector DB for the K most similar documents to our query. In our system, K=5 is a good default (retrieve 5 most relevant chunks).

**Chunk**: A segment of a larger document. We split documents into chunks before embedding because:
(a) LLMs have context limits, (b) smaller chunks = more precise retrieval.

**Context window**: The maximum amount of text an LLM can process at once. Claude's window is large (~200K tokens), but we still want to keep retrieved context focused and relevant.

**Hallucination**: When an LLM generates text that sounds confident but is factually incorrect. RAG reduces this by grounding answers in real retrieved documents.

---

## RAG Variants (good to know)

**Naive RAG** (what we start with): Query → retrieve → generate. Simple, works well for most cases.

**Advanced RAG**: Query rewriting (rephrase question before retrieval), re-ranking (use a second model to score retrieved chunks by relevance), hypothetical document embedding (HyDE — generate a hypothetical answer, embed it, use it as the query vector).

**Agentic RAG** (Phase 2): Instead of one retrieval step, an agent decides whether to retrieve, which collection to retrieve from, whether to call a tool (like yfinance for live data), and how to combine multiple sources.

---

## Common Mistakes (avoid these)

1. **Chunking by fixed character count without sentence boundaries**: Breaks sentences mid-way, creates incoherent chunks. Use LangChain's `RecursiveCharacterTextSplitter` which respects sentence and paragraph boundaries.

2. **Not storing metadata with chunks**: Always store `ticker`, `date`, `source`, `type` alongside each chunk. This lets you filter by date range or ticker when retrieving.

3. **Using different embedding models for ingestion and retrieval**: If you embed documents with model A and the query with model B, similarity scores are meaningless. Always use the same model.

4. **Retrieving too many chunks (large K)**: More isn't better. 10 mediocre chunks dilute the good ones. 3–5 highly relevant chunks is better.

5. **Not evaluating retrieval separately from generation**: If answers are wrong, is retrieval failing (wrong chunks returned) or generation failing (right chunks, wrong answer)? Evaluate both independently.

---

## Code Pattern: LangChain RAG in 25 Lines

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Set up embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Load or create vector store
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# 3. Set up LLM
llm = ChatAnthropic(model="claude-haiku-4-5", temperature=0)

# 4. Create retriever (top 5 most similar chunks)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 5. Build RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "stuff" = dump all retrieved chunks into context
    retriever=retriever,
    return_source_documents=True  # So we can show citations
)

# 6. Ask a question
result = qa_chain.invoke({"query": "How did TCS perform in Q4 FY24?"})
print(result["result"])         # The answer
print(result["source_documents"])  # The chunks that were retrieved
```

---

## Further Reading

- LangChain RAG documentation: https://python.langchain.com/docs/tutorials/rag/
- "A Survey of RAG" paper: foundational academic overview
- LlamaIndex as alternative to LangChain (similar concept, different API style)

---

*Next: Read `02-vector-databases.md` to understand how ChromaDB works internally.*
