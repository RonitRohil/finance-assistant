import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, news, portfolio, stocks
from app.core.config import settings
from app.core.llm import test_llm

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinanceAssistant API",
    version="0.1.0",
    description="RAG-based AI finance assistant for Indian stock markets",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000", "127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(news.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "llm": settings.llm_provider,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "finance-assistant",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.on_event("startup")
async def startup_event():
    """On startup events."""
    logger.info("=" * 50)
    logger.info("FinanceAssistant API Starting")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"ChromaDB Dir: {settings.chroma_persist_dir}")
    logger.info("=" * 50)

    # Test LLM connection
    try:
        test_llm()
    except Exception as e:
        logger.warning(f"LLM test failed at startup: {e}")
