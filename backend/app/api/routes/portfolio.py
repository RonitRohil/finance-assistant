import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("")
async def list_holdings():
    """List all holdings."""
    return {"holdings": [], "message": "Portfolio service not yet implemented"}


@router.post("")
async def add_holding():
    """Add a new holding."""
    return {"message": "Portfolio service not yet implemented"}
