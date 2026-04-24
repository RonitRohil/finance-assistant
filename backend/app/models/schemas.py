from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict] = []
    session_id: Optional[str] = None


class StockInfoResponse(BaseModel):
    ticker: str
    currentPrice: Optional[float] = None
    previousClose: Optional[float] = None
    change_pct: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[int] = None
    dividend_yield: Optional[float] = None


class StockHistoryResponse(BaseModel):
    ticker: str
    period: str
    data: list[dict]


class HoldingBase(BaseModel):
    ticker: str
    quantity: float
    avg_buy_price: float


class HoldingCreate(HoldingBase):
    pass


class Holding(HoldingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    ticker: str
    action: str  # 'buy' or 'sell'
    quantity: float
    price: float
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True
