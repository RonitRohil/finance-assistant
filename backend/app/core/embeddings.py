import logging

from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

_embeddings_instance = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings_instance
    if _embeddings_instance is not None:
        return _embeddings_instance

    logger.info("Loading embeddings model: all-MiniLM-L6-v2...")
    _embeddings_instance = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    logger.info("Embeddings model loaded successfully")
    return _embeddings_instance
