import logging
from typing import Any

from app.core.vectorstore import add_documents

logger = logging.getLogger(__name__)


async def ingest_stock_data(
    ticker: str, data: list[dict[str, Any]], collection_name: str = "stock_data"
) -> dict[str, int]:
    """Ingest stock data into ChromaDB."""
    try:
        texts = []
        metadatas = []

        for record in data:
            text = (
                f"Stock: {ticker}\n"
                f"Date: {record.get('date')}\n"
                f"Open: {record.get('open')}\n"
                f"High: {record.get('high')}\n"
                f"Low: {record.get('low')}\n"
                f"Close: {record.get('close')}\n"
                f"Volume: {record.get('volume')}"
            )
            texts.append(text)
            metadatas.append(
                {
                    "ticker": ticker,
                    "date": record.get("date"),
                    "source": "yfinance",
                    "type": "price_data",
                }
            )

        add_documents(collection_name, texts, metadatas)
        logger.info(f"Ingested {len(texts)} stock records for {ticker}")
        return {"ingested": len(texts), "failed": 0}

    except Exception as e:
        logger.error(f"Error ingesting stock data: {e}")
        return {"ingested": 0, "failed": len(data)}
