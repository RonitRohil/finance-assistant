import logging
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_newsapi_client = None


def _get_client():
    global _newsapi_client
    if not settings.newsapi_key:
        return None
    if _newsapi_client is None:
        from newsapi import NewsApiClient
        _newsapi_client = NewsApiClient(api_key=settings.newsapi_key)
    return _newsapi_client


async def fetch_news(query: str, limit: int = 10) -> dict[str, Any]:
    client = _get_client()
    if client is None:
        logger.warning("NewsAPI key not configured — set NEWSAPI_KEY in .env")
        return {"articles": [], "message": "NewsAPI key not configured"}

    try:
        response = client.get_everything(
            q=query,
            language="en",
            sort_by="publishedAt",
            page_size=min(limit, 100),
        )
        articles = [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", ""),
                "published_at": a.get("publishedAt", ""),
            }
            for a in response.get("articles", [])
        ]
        return {"articles": articles, "total": len(articles)}
    except Exception as e:
        logger.error(f"NewsAPI error: {e}")
        return {"articles": [], "error": str(e)}


async def ingest_news(articles: list[dict[str, Any]]) -> dict[str, int]:
    from app.core.vectorstore import add_documents

    if not articles:
        return {"ingested": 0, "failed": 0}

    try:
        texts = [
            f"Title: {a.get('title', '')}\n{a.get('description', '') or ''}"
            for a in articles
        ]
        metadatas = [
            {
                "ticker": "market",
                "date": a.get("published_at", ""),
                "source": a.get("source", "newsapi"),
                "type": "news",
            }
            for a in articles
        ]
        add_documents("stock_news", texts, metadatas)
        logger.info(f"Ingested {len(texts)} news articles into ChromaDB")
        return {"ingested": len(texts), "failed": 0}
    except Exception as e:
        logger.error(f"News ingestion error: {e}")
        return {"ingested": 0, "failed": len(articles)}
