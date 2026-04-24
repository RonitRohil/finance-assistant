import logging
from typing import Any, Optional

from langchain_chroma import Chroma

from app.core.config import settings
from app.core.embeddings import get_embeddings

logger = logging.getLogger(__name__)


def get_vectorstore(collection_name: str) -> Chroma:
    """Get or create a ChromaDB vector store collection."""
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )
    logger.debug(f"Loaded ChromaDB collection: {collection_name}")
    return vectorstore


def add_documents(
    collection_name: str, texts: list[str], metadatas: list[dict[str, Any]]
) -> None:
    """Add documents to a ChromaDB collection."""
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    logger.info(f"Added {len(texts)} documents to {collection_name}")


def similarity_search(
    collection_name: str,
    query: str,
    k: int = 5,
    filter: Optional[dict[str, Any]] = None,
) -> list[tuple[Any, float]]:
    """Search for similar documents in ChromaDB."""
    vectorstore = get_vectorstore(collection_name)
    results = vectorstore.similarity_search_with_score(query, k=k, filter=filter)
    logger.debug(f"Found {len(results)} results for query in {collection_name}")
    return results
