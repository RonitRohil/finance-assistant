# Study Notes: APScheduler — Automated Background Jobs

**Date:** April 2026
**Sprint:** Sprint 2 — Data Pipeline
**Status:** Pre-reading before Sprint 2 implementation
**What this is:** How to run recurring background jobs inside a FastAPI app — without a separate process, cron daemon, or Celery setup.

---

## The Problem APScheduler Solves

Our finance assistant needs to do things automatically:
- Fetch morning news at 9 AM IST before Indian market opens
- Fetch evening news at 6 PM IST after market close
- Update Nifty 500 stock prices at 6:30 PM IST

You could do this with a separate Python script and Windows Task Scheduler, but that means maintaining two separate processes. APScheduler lets you define these schedules **inside your FastAPI app** — they start when the server starts, stop when it stops, and you don't need anything else.

---

## How APScheduler Works

```
Your FastAPI app starts
       ↓
APScheduler starts in the background (same process)
       ↓
You register jobs: "run function X at time Y"
       ↓
Scheduler runs in a background thread/event loop
       ↓
When the scheduled time hits → your function runs
       ↓
Function finishes → scheduler waits for next scheduled time
```

The scheduler runs in the same Python process as FastAPI, but in a separate async task. Your API endpoints are not blocked while jobs run.

---

## The Three Pieces You Need

### 1. The Scheduler — `AsyncIOScheduler`

For FastAPI (which uses Python's `asyncio` event loop), use `AsyncIOScheduler`:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
```

The `timezone` parameter is critical — it means "treat all times as IST". Without it, times are UTC by default, which would fire your 9 AM job at 3:30 AM IST.

### 2. The Trigger — `CronTrigger`

Triggers define *when* a job runs. `CronTrigger` lets you specify time using cron-style syntax (hour, minute, day of week, etc.):

```python
from apscheduler.triggers.cron import CronTrigger

# Every day at 9:00 AM
CronTrigger(hour=9, minute=0)

# Every day at 6:30 PM
CronTrigger(hour=18, minute=30)

# Every Monday at 8 AM
CronTrigger(day_of_week="mon", hour=8, minute=0)

# Every 30 minutes (useful for testing)
CronTrigger(minute="*/30")

# On specific days — last Thursday of each month (F&O expiry reminder)
CronTrigger(day="last thu", hour=15, minute=30)
```

Other trigger types you won't use in Sprint 2 but good to know:
- `IntervalTrigger(hours=1)` — runs every hour, starting now
- `DateTrigger(run_date="2026-05-01 09:00")` — runs once at a specific datetime

### 3. The Job — any Python function

```python
def my_job():
    print("I ran!")

scheduler.add_job(
    func=my_job,
    trigger=CronTrigger(hour=9, minute=0),
    id="morning_job",        # Unique ID — used to modify/remove later
    name="Morning job",      # Human-readable description
    replace_existing=True    # If ID already exists, replace it (important on server restart)
)
```

---

## Integrating with FastAPI

The standard pattern: start the scheduler on app startup, stop it on shutdown.

```python
# app/main.py
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

app = FastAPI()
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

@app.on_event("startup")
async def startup():
    # Register all jobs
    scheduler.add_job(
        func=morning_news_job,
        trigger=CronTrigger(hour=9, minute=0),
        id="morning_news",
        name="Morning news ingest (9 AM IST)",
        replace_existing=True
    )
    scheduler.add_job(
        func=evening_news_job,
        trigger=CronTrigger(hour=18, minute=0),
        id="evening_news",
        name="Evening news ingest (6 PM IST)",
        replace_existing=True
    )
    # Start the scheduler
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()
```

**Why `replace_existing=True`?**
When you restart the server (which happens constantly during development with `--reload`), APScheduler would try to register the same job ID again. Without `replace_existing=True`, it throws an error. With it, the old job is cleanly replaced by the new one.

---

## Our FinanceAssistant Scheduler Setup

```python
# app/core/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

def setup_scheduler():
    """Register all scheduled jobs. Call once from app startup."""
    
    # Import here to avoid circular imports
    from app.services.news_service import ingest_news_batch, MORNING_QUERIES, EVENING_QUERIES
    from app.services.bulk_ingest_service import ingest_all_nifty500_stocks

    # 9:00 AM IST — pre-market news
    scheduler.add_job(
        func=lambda: ingest_news_batch(MORNING_QUERIES),
        trigger=CronTrigger(hour=9, minute=0),
        id="morning_news_ingest",
        name="Morning news ingest (9 AM IST)",
        replace_existing=True
    )

    # 6:00 PM IST — post-market news
    scheduler.add_job(
        func=lambda: ingest_news_batch(EVENING_QUERIES),
        trigger=CronTrigger(hour=18, minute=0),
        id="evening_news_ingest",
        name="Evening news ingest (6 PM IST)",
        replace_existing=True
    )

    # 6:30 PM IST — stock price update (after market close at 3:30 PM)
    scheduler.add_job(
        func=ingest_all_nifty500_stocks,
        trigger=CronTrigger(hour=18, minute=30),
        id="daily_stock_update",
        name="Daily Nifty 500 price update (6:30 PM IST)",
        replace_existing=True
    )

    logger.info(
        "Scheduler configured: morning news (9AM IST), "
        "evening news (6PM IST), stock update (6:30PM IST)"
    )
    return scheduler
```

---

## Inspecting the Scheduler — Useful at Runtime

### Via FastAPI endpoint (what we built)

```bash
GET /api/scheduler/jobs
```

Returns:
```json
{
  "jobs": [
    {
      "id": "morning_news_ingest",
      "name": "Morning news ingest (9 AM IST)",
      "next_run": "2026-05-02 09:00:00+05:30"
    },
    {
      "id": "evening_news_ingest",
      "name": "Evening news ingest (6 PM IST)",
      "next_run": "2026-05-01 18:00:00+05:30"
    },
    {
      "id": "daily_stock_update",
      "name": "Daily Nifty 500 price update (6:30 PM IST)",
      "next_run": "2026-05-01 18:30:00+05:30"
    }
  ],
  "total": 3
}
```

### Via Python (in code)

```python
# List all jobs
for job in scheduler.get_jobs():
    print(job.id, job.next_run_time)

# Check if a specific job exists
job = scheduler.get_job("morning_news_ingest")
if job:
    print(f"Next run: {job.next_run_time}")

# Pause a job (stops it from running without removing it)
scheduler.pause_job("morning_news_ingest")

# Resume a paused job
scheduler.resume_job("morning_news_ingest")

# Remove a job entirely
scheduler.remove_job("morning_news_ingest")

# Trigger a job immediately (without waiting for schedule)
scheduler.get_job("morning_news_ingest").func()   # Or just call the function directly
```

---

## What "Execution of job missed" Means

When the server is down at the time a job was supposed to run, APScheduler logs this:

```
Execution of job "Morning news ingest (9 AM IST)" missed by 0:01:23
```

**This is not an error you need to fix.** It just means the server was down at 9 AM. The job will run at the next scheduled time. For a locally-running dev app, this happens all the time — your laptop is off, or you haven't started the server yet.

If you need guaranteed execution even after missed runs, look up `misfire_grace_time` in APScheduler docs. For Phase 1, we don't need this.

---

## Testing Scheduled Jobs Without Waiting

You don't want to wait until 9 AM to confirm the morning job works. Two ways to test immediately:

### Option 1: Call the function directly

```python
# In a Python shell or test script
from app.services.news_service import ingest_news_batch, MORNING_QUERIES
result = ingest_news_batch(MORNING_QUERIES)
print(result)
```

### Option 2: Trigger via a test endpoint (add temporarily during dev)

```python
# Add to main.py temporarily during Sprint 2 development
@app.post("/api/scheduler/run/{job_id}")
async def trigger_job_now(job_id: str):
    """Dev-only endpoint to trigger a scheduled job immediately."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job.func()   # Call the job function directly
    return {"triggered": job_id, "status": "running"}
```

```bash
curl -X POST http://localhost:8000/api/scheduler/run/morning_news_ingest
```

Remove this endpoint before sharing the app.

---

## Common Mistakes

### Mistake 1: Forgetting the timezone

```python
# BAD — fires at 9 AM UTC = 2:30 PM IST. Very confusing.
scheduler = AsyncIOScheduler()
scheduler.add_job(func, CronTrigger(hour=9, minute=0))

# GOOD — fires at 9 AM IST
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(func, CronTrigger(hour=9, minute=0))
```

### Mistake 2: Not calling `scheduler.start()`

Registering jobs with `add_job()` doesn't start the scheduler. You must call `scheduler.start()`:

```python
# This registers jobs but nothing ever runs:
scheduler.add_job(...)

# This is required:
scheduler.start()  # ← Don't forget this!
```

### Mistake 3: Importing inside job functions causes circular imports

If your job function imports from modules that import from `scheduler.py`, you get a circular import. Solution: move imports inside the function body:

```python
# GOOD — import at call time, not at module load time
def setup_scheduler():
    from app.services.news_service import ingest_news_batch   # ← import here
    scheduler.add_job(func=ingest_news_batch, ...)
```

### Mistake 4: Using the wrong scheduler type

```python
# For FastAPI (asyncio event loop) — use this:
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# For regular Python scripts (no event loop) — use this:
from apscheduler.schedulers.background import BackgroundScheduler

# Using BackgroundScheduler with FastAPI causes thread conflicts
```

---

## Log Lines to Confirm It's Working

When the scheduler starts correctly, you'll see:

```
INFO:apscheduler.scheduler:Scheduler started
INFO:app.core.scheduler:Scheduler configured: morning news (9AM IST), evening news (6PM IST), stock update (6:30PM IST)
INFO:app.main:APScheduler started — scheduled jobs active
```

When a job runs:
```
INFO:apscheduler.executors.default:Running job "Morning news ingest (9 AM IST)" (scheduled at 2026-05-01 09:00:00+05:30)
INFO:app.services.news_service:Fetching news: "Nifty Sensex Indian stock market today" (limit=20)
INFO:app.services.news_service:Ingested 18 articles into stock_news
INFO:apscheduler.executors.default:Job "Morning news ingest (9 AM IST)" executed successfully
```

When a job is missed (server was down):
```
WARNING:apscheduler.scheduler:Execution of job "Morning news ingest" missed by 0:04:22
```

---

## Quick Reference Card

| Task | Code |
|------|------|
| Create scheduler (IST) | `AsyncIOScheduler(timezone="Asia/Kolkata")` |
| Schedule daily at 9 AM | `CronTrigger(hour=9, minute=0)` |
| Schedule every 30 mins | `CronTrigger(minute="*/30")` |
| Add a job | `scheduler.add_job(func, trigger, id="...", replace_existing=True)` |
| Start scheduler | `scheduler.start()` |
| Stop scheduler | `scheduler.shutdown()` |
| List all jobs | `scheduler.get_jobs()` |
| Get next run time | `scheduler.get_job("id").next_run_time` |
| Pause a job | `scheduler.pause_job("id")` |

---

## What Comes in Phase 2

In Phase 2 we'll consider:
- **Celery + Redis** — if jobs need to be distributed across multiple workers (not needed for single-user local app)
- **APScheduler with persistent job store** — so jobs survive server restarts with their state intact (using SQLAlchemy job store backed by our database)
- **Job retry on failure** — currently if a news ingest fails, it's just missed. Phase 2 can add retry logic.

For Phase 1: APScheduler with `AsyncIOScheduler` is exactly right. No overengineering needed.

---

*Updated: April 2026 | Part of Sprint 2 pre-reading | Next: Sprint 2 implementation*
