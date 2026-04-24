import logging

from fastapi import APIRouter, Query

from app.services.news_service import fetch_news, ingest_news

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
async def get_news(
    query: str = Query("Indian stock market NSE BSE", min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    return await fetch_news(query, limit)


@router.post("/ingest")
async def ingest_market_news(
    query: str = Query("Indian stock market NSE BSE ETF"),
    limit: int = Query(20, ge=1, le=50),
):
    news = await fetch_news(query, limit)
    articles = news.get("articles", [])
    if not articles:
        return {"message": "No articles found to ingest", "ingested": 0, "failed": 0}
    result = await ingest_news(articles)
    return {"message": f"Ingested {result['ingested']} articles", **result}
