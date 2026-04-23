from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="FinanceAssistant API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "finance-assistant", "docs": "/docs"}
