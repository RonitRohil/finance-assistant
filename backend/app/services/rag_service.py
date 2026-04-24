import logging
from typing import Any

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from app.core.llm import get_llm
from app.core.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a financial analyst assistant specializing in Indian stock markets (NSE/BSE) and ETFs.

Instructions:
1. Answer ONLY using the provided context documents
2. If you don't have enough information to answer, clearly state that
3. Always cite which sources/documents you used
4. Be factual and avoid speculation
5. For stock recommendations, include relevant metrics like P/E ratio, market cap, dividend yield

If the user asks about a specific stock, provide:
- Current price
- Performance metrics
- Risk assessment based on available data
- Any recent news or events"""


def get_rag_chain(collection_name: str = "stock_news"):
    """Create a RAG chain for answering finance questions."""
    llm = get_llm()
    vectorstore = get_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    prompt = PromptTemplate(
        template=SYSTEM_PROMPT
        + "\n\nContext documents:\n{context}\n\nQuestion: {question}",
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    return chain


async def answer_question(
    question: str, collection_name: str = "stock_news"
) -> dict[str, Any]:
    """
    Answer a question using the RAG chain.

    Returns:
        dict with "answer" and "sources" keys
    """
    try:
        chain = get_rag_chain(collection_name)
        result = chain.invoke(question)

        sources = []
        if result.get("source_documents"):
            for doc in result["source_documents"]:
                sources.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                    }
                )

        return {"answer": result["result"], "sources": sources}

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return {
            "answer": "I encountered an error processing your question. Please try again.",
            "sources": [],
        }
