import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
async def get_news():
    """Fetch market news."""
    return {"articles": [], "message": "News service not yet implemented"}
