# Backend

FastAPI + LangChain service.

## Local dev

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload
```

Health check: http://localhost:8000/health
