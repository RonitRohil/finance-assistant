import logging
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

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

Context:
{context}

Question: {question}

Answer:"""


def _format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


async def answer_question(
    question: str, collection_name: str = "stock_news"
) -> dict[str, Any]:
    try:
        llm = get_llm()
        vectorstore = get_vectorstore(collection_name)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        docs = retriever.invoke(question)
        context = _format_docs(docs)

        prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        sources = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]
        return {"answer": answer, "sources": sources}

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return {
            "answer": "I encountered an error processing your question. Please try again.",
            "sources": [],
        }
