import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import StockHistoryResponse, StockInfoResponse
from app.services.stock_service import get_stock_history, get_stock_info

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{ticker}", response_model=StockInfoResponse)
async def get_stock(ticker: str) -> StockInfoResponse:
    """Fetch basic stock information."""
    result = get_stock_info(ticker)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return StockInfoResponse(**result)


@router.get("/{ticker}/history", response_model=StockHistoryResponse)
async def get_stock_price_history(
    ticker: str, period: str = Query("1y", regex="^[0-9]+(d|mo|y)$")
) -> StockHistoryResponse:
    """Fetch historical OHLCV data for a stock."""
    result = get_stock_history(ticker, period)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return StockHistoryResponse(**result)
