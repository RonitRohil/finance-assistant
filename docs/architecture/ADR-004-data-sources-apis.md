# ADR-004: Data Sources & API Strategy

**Status:** Accepted  
**Date:** April 2026  
**Deciders:** Ronit Jain  

---

## Context

FinanceAssistant needs real financial data to be useful. Without good data, even the best RAG pipeline returns garbage. We need data for:

1. Indian stock prices and historical data (NSE/BSE)
2. ETF NAV and holdings data
3. Fundamental data (P/E ratio, revenue, EPS, etc.)
4. News and market sentiment
5. Personal portfolio tracking (manual input or broker API)

Constraint: **free tier wherever possible**. We'll investigate paid options only when a free alternative is genuinely inadequate.

---

## Decision: Phased Data Source Strategy

### Phase 1 — Core Data (All Free)

| Data Need | Source | Library / Method | Free Limit | Notes |
|-----------|--------|-----------------|------------|-------|
| NSE/BSE stock prices | Yahoo Finance | `yfinance` | Unlimited* | Add `.NS` suffix (RELIANCE.NS) |
| Historical OHLCV | Yahoo Finance | `yfinance` | Unlimited* | Up to 20 years history |
| ETF data (India) | Yahoo Finance | `yfinance` | Unlimited* | NIFTYBEES.NS, GOLDBEES.NS |
| Fundamentals (basic) | Yahoo Finance | `yfinance` | Unlimited* | P/E, EPS, revenue |
| Market news | NewsAPI | REST API | 100 req/day | Developer plan, free forever |
| Financial news | GNews | REST API | 100 req/day | Free tier |
| Global macro news | Alpha Vantage | REST API | 25 req/day | Has India coverage |
| NSE specific data | nsepy | Python library | Unlimited | Historical NSE data |

*Yahoo Finance is technically unofficial (no SLA), but `yfinance` is used by hundreds of thousands of developers and is extremely reliable for personal projects.

### Phase 2 — Enhanced Data (Some Paid)

| Data Need | Source | Cost | Trigger |
|-----------|--------|------|---------|
| Real-time NSE/BSE prices | Upstox API or Angel One SmartAPI | Free (need demat account) | When live data matters |
| Premium fundamentals | Financial Modeling Prep | $0 (250 req/day free) | When yfinance fundamentals aren't enough |
| Broker portfolio sync | Zerodha Kite Connect | ₹2000/month | Only if manual entry is too painful |
| Institutional data | NSE official APIs | Free (rate limited) | Phase 3 |

---

## Data Source Deep Dives

### 1. yfinance — The Workhorse

`yfinance` is a Python wrapper around Yahoo Finance's backend. It's the most reliable free source of Indian stock data.

```python
import yfinance as yf

# Fetch Reliance Industries data
reliance = yf.Ticker("RELIANCE.NS")

# Current price info
info = reliance.info
print(info['currentPrice'])        # ₹2,847
print(info['trailingPE'])          # 24.3
print(info['marketCap'])           # 1.9T

# Historical data (DataFrame)
hist = reliance.history(period="1y")  # Last 1 year
hist = reliance.history(start="2023-01-01", end="2024-01-01")

# Earnings
earnings = reliance.quarterly_earnings

# ETF example
niftybees = yf.Ticker("NIFTYBEES.NS")
```

**Indian market tickers format:**
- NSE stocks: `TICKER.NS` (e.g., TCS.NS, HDFCBANK.NS, INFY.NS)
- BSE stocks: `TICKER.BO` (e.g., 500325.BO for Reliance on BSE)
- Indian ETFs: NIFTYBEES.NS, GOLDBEES.NS, BANKBEES.NS, JUNIORBEES.NS
- Nifty 50 index: `^NSEI`
- Sensex: `^BSESN`

**What yfinance gives us for free:**
- OHLCV data (daily, weekly, monthly, up to 20 years)
- Real-time quote (15-min delayed for India)
- P/E ratio, P/B ratio, EV/EBITDA
- Revenue, net income, EPS (quarterly + annual)
- Dividend history
- Major holders, institutional holders
- Analyst recommendations and price targets
- Options chain (for US markets)

---

### 2. nsepy — NSE Historical Data

`nsepy` gives direct access to NSE India's historical data API.

```python
from nsepy import get_history
from datetime import date

# Get historical data for a stock
tcs_data = get_history(
    symbol="TCS",
    start=date(2024, 1, 1),
    end=date(2024, 12, 31)
)

# Get index data
nifty_data = get_history(
    symbol="NIFTY",
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    index=True
)
```

Useful for: precise NSE data, F&O data, circuit breakers, delivery percentage.

---

### 3. NewsAPI — Market News Ingestion

NewsAPI gives 100 free requests/day on the developer plan. We'll use it to ingest news and embed it into ChromaDB.

```python
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='YOUR_KEY')

# Get top financial headlines
headlines = newsapi.get_top_headlines(
    q='Nifty OR Sensex OR NSE',
    category='business',
    language='en',
    country='in'
)

# Search for company-specific news
reliance_news = newsapi.get_everything(
    q='Reliance Industries',
    from_param='2024-01-01',
    language='en',
    sort_by='publishedAt'
)
```

**Strategy to maximize 100 req/day:**
- Schedule ingestion runs: morning (pre-market), afternoon (mid-session), evening (post-close)
- Use batch queries: combine multiple tickers in one query with OR operators
- Cache results locally — don't refetch the same articles

---

### 4. Alpha Vantage — Supplementary Data

25 free requests/day. Use sparingly for data yfinance doesn't cover well:

```python
import requests

def get_fundamental_data(ticker: str, api_key: str):
    # Company overview (P/E, sector, description)
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    return requests.get(url).json()

# Good for: company overviews, global news sentiment scores
```

---

### 5. Indian Broker APIs (Phase 2)

When you want real-time data and portfolio sync, Indian broker APIs are the best option. All are free with a trading account:

**Angel One SmartAPI (Recommended for Phase 2)**
- Free with Angel One demat account
- WebSocket for real-time tick data
- Historical data up to 365 days
- Portfolio and order history sync

```python
from SmartApi import SmartConnect

obj = SmartConnect(api_key="YOUR_KEY")
data = obj.generateSession("CLIENT_ID", "PASSWORD", "TOTP")

# Real-time LTP
ltpData = obj.ltpData("NSE", "RELIANCE-EQ", "3045")
```

**Upstox API**
- Free with Upstox account
- Good documentation
- Real-time and historical data

**Zerodha Kite Connect**
- ₹2000/month (not free, but cheap)
- Best documentation, largest community
- Most reliable real-time data

---

## Data Ingestion Architecture

```
Scheduled Jobs (APScheduler):
├── Every morning (9:00 AM):
│   ├── Fetch previous day's price data for watchlist
│   ├── Fetch overnight news → embed → store in ChromaDB
│   └── Update portfolio valuations in SQLite
├── Every evening (4:00 PM, post-market):
│   ├── Fetch end-of-day data for all tracked stocks
│   ├── Fetch post-market news
│   └── Compute daily P&L for portfolio
└── Weekly (Sunday):
    ├── Fetch quarterly earnings reports if available
    ├── Update fundamentals data
    └── Refresh ETF holdings data
```

---

## Data We Do NOT Have (and how to handle it)

| Data Gap | Our Workaround |
|----------|---------------|
| Intraday tick data | Use 15-min delayed Yahoo Finance or broker API (Phase 2) |
| BSE live feed | Use NSE equivalent; most large caps list on both |
| Options chain India | nsepy has this; add in Phase 2 |
| Mutual fund NAV | AMFI website (free, daily NAV) — add script in Phase 2 |
| Personal bank data | Manual CSV upload (Phase 1), Plaid/account aggregator API (Phase 2) |
| Credit card statements | Manual PDF upload → parse with pdfplumber (Phase 1) |

---

## Rate Limit Management Plan

```python
# We'll build a simple rate limiter decorator
import time
from functools import wraps

def rate_limit(calls_per_day: int):
    """Ensure we never exceed free tier limits"""
    interval = 86400 / calls_per_day  # seconds between calls
    def decorator(func):
        last_called = [0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < interval:
                time.sleep(interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_day=90)  # Leave buffer below 100
def fetch_news(query: str):
    return newsapi.get_everything(q=query)
```

---

## API Keys Needed (Phase 1)

| Service | Free Tier | Where to Sign Up |
|---------|-----------|-----------------|
| Anthropic (Claude) | $5 free credits | console.anthropic.com |
| NewsAPI | 100 req/day | newsapi.org |
| Alpha Vantage | 25 req/day | alphavantage.co |
| GNews | 100 req/day | gnews.io |

yfinance, nsepy, sentence-transformers — **no API key needed**.

---

## Action Items

- [ ] Install and test `yfinance` with 5 Indian stocks (TCS, RELIANCE, HDFCBANK, INFY, NIFTYBEES)
- [ ] Sign up for NewsAPI free tier
- [ ] Sign up for Alpha Vantage free tier
- [ ] Write data ingestion script: yfinance → ChromaDB
- [ ] Write news ingestion script: NewsAPI → embed → ChromaDB
- [ ] Build rate limiter utility
- [ ] Test all free tier limits — document actual limits found empirically
