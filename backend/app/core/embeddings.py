import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_embeddings_instance = None


def get_embeddings():
    """Get or create HuggingFace embeddings instance (cached)."""
    global _embeddings_instance

    if _embeddings_instance is not None:
        return _embeddings_instance

    logger.info("Loading embeddings model: all-MiniLM-L6-v2...")
    from langchain_community.embeddings import HuggingFaceEmbeddings

    _embeddings_instance = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    logger.info("Embeddings model loaded successfully")
    return _embeddings_instance
