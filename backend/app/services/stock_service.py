import logging
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


def normalize_ticker(ticker: str) -> str:
    """Auto-append .NS for Indian stocks if no exchange suffix present."""
    ticker = ticker.upper().strip()
    if "." not in ticker:
        ticker = f"{ticker}.NS"
    return ticker


def get_stock_info(ticker: str) -> dict[str, Any]:
    """Fetch basic stock info using yfinance."""
    try:
        ticker = normalize_ticker(ticker)
        stock = yf.Ticker(ticker)

        # Fetch historical data for context
        hist = stock.history(period="1d")
        if hist.empty:
            return {"error": f"Ticker {ticker} not found or no data available"}

        info = stock.info or {}

        return {
            "ticker": ticker,
            "currentPrice": info.get("currentPrice", hist["Close"].iloc[-1] if not hist.empty else None),
            "previousClose": info.get("previousClose", None),
            "open": hist["Open"].iloc[-1] if not hist.empty else None,
            "high": hist["High"].iloc[-1] if not hist.empty else None,
            "low": hist["Low"].iloc[-1] if not hist.empty else None,
            "volume": hist["Volume"].iloc[-1] if not hist.empty else None,
            "pe_ratio": info.get("trailingPE", None),
            "market_cap": info.get("marketCap", None),
            "dividend_yield": info.get("dividendYield", None),
            "52_week_high": info.get("fiftyTwoWeekHigh", None),
            "52_week_low": info.get("fiftyTwoWeekLow", None),
        }

    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {e}")
        return {"error": str(e)}


def get_stock_history(
    ticker: str, period: str = "1y"
) -> dict[str, Any]:
    """Fetch historical OHLCV data."""
    try:
        ticker = normalize_ticker(ticker)
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No historical data found for {ticker}"}

        # Convert to list of dicts for JSON serialization
        records = []
        for date, row in hist.iterrows():
            records.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }
            )

        return {"ticker": ticker, "period": period, "data": records}

    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {e}")
        return {"error": str(e)}
