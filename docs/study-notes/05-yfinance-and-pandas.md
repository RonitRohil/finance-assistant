# Study Notes: yfinance and pandas for Financial Data

**Date:** April 2026
**Sprint:** Sprint 2 — Data Pipeline
**Status:** Pre-reading before Sprint 2 implementation
**What this is:** Everything you need to know about pulling real stock data with yfinance and working with pandas DataFrames — written so it connects directly to what we're building.

---

## Why These Two Libraries Go Together

`yfinance` fetches stock data from Yahoo Finance. Almost everything it returns comes back as a **pandas DataFrame** — a table-like data structure used throughout Python's data science ecosystem. You don't need to become a pandas expert, but you do need to know enough to convert that data into dicts and lists so FastAPI can send it as JSON.

Think of it this way:
- **yfinance** = the librarian who gets your book (the stock data)
- **pandas DataFrame** = the book itself (rows and columns of numbers)
- **Your job** = photocopying the pages you need into JSON format

---

## yfinance Basics

### Installing and importing

```python
pip install yfinance
import yfinance as yf
```

### The Ticker object — your main entry point

```python
stock = yf.Ticker("TCS.NS")
```

This creates a `Ticker` object. It doesn't fetch any data yet — it just sets up the connection. Data is fetched lazily when you access properties.

### Three things you'll use constantly

```python
# 1. .info — a dict with everything: price, PE, sector, market cap...
info = stock.info
print(info["regularMarketPrice"])   # Current price
print(info["trailingPE"])           # P/E ratio
print(info["sector"])               # "Technology"
print(info["marketCap"])            # Market cap in rupees

# 2. .history() — OHLCV data as a DataFrame
hist = stock.history(period="1y")   # 1 year of daily data
# Returns a DataFrame with columns: Open, High, Low, Close, Volume, Dividends, Stock Splits

# 3. .fast_info — lightweight version of .info, faster to fetch
fast = stock.fast_info
print(fast.last_price)              # Current price (faster than .info)
```

---

## Indian Ticker Format

This is the most common gotcha. Indian stocks on NSE use a `.NS` suffix:

```python
# CORRECT — NSE (National Stock Exchange)
yf.Ticker("TCS.NS")
yf.Ticker("RELIANCE.NS")
yf.Ticker("HDFCBANK.NS")

# BSE alternative (Bombay Stock Exchange, less common)
yf.Ticker("TCS.BO")

# Indices (no suffix, starts with ^)
yf.Ticker("^NSEI")    # Nifty 50 index
yf.Ticker("^BSESN")   # Sensex index

# ETFs (same .NS suffix)
yf.Ticker("NIFTYBEES.NS")
yf.Ticker("GOLDBEES.NS")
```

**Rule of thumb:** If someone types "TCS" or "Reliance", auto-append `.NS` before calling yfinance.

```python
def normalize_ticker(ticker: str) -> str:
    t = ticker.upper().strip()
    if not t.endswith(".NS") and not t.endswith(".BO") and not t.startswith("^"):
        t = t + ".NS"
    return t
```

---

## Understanding the `.info` Dict

The `info` dict has 50+ keys. Here are the ones we actually use:

```python
info = yf.Ticker("TCS.NS").info

# Price data
info["regularMarketPrice"]     # Current/last traded price (None when market closed)
info["previousClose"]          # Previous day closing price (always available)
info["open"]                   # Today's opening price
info["dayHigh"]                # Today's high
info["dayLow"]                 # Today's low
info["regularMarketVolume"]    # Today's volume

# Valuation
info["trailingPE"]             # P/E ratio (trailing 12 months)
info["priceToBook"]            # P/B ratio
info["marketCap"]              # Market cap in ₹
info["enterpriseValue"]        # Enterprise value

# Company info
info["longName"]               # "Tata Consultancy Services Limited"
info["sector"]                 # "Technology"
info["industry"]               # "Information Technology Services"
info["website"]                # "https://www.tcs.com"
info["longBusinessSummary"]    # Long description paragraph

# Performance
info["fiftyTwoWeekHigh"]       # 52-week high
info["fiftyTwoWeekLow"]        # 52-week low
info["fiftyDayAverage"]        # 50-day moving average
info["twoHundredDayAverage"]   # 200-day moving average

# Dividends
info["dividendYield"]          # e.g., 0.018 = 1.8%
info["dividendRate"]           # Annual dividend per share
```

**Important:** Many of these keys return `None` when:
- The market is closed (for real-time prices)
- The company doesn't pay dividends (dividendYield = None)
- The stock is newly listed (no historical moving averages yet)

Always use `.get()` with a default value instead of direct key access:
```python
# BAD — throws KeyError if missing
pe = info["trailingPE"]

# GOOD — returns None instead of crashing
pe = info.get("trailingPE")
```

---

## pandas DataFrames — What You Actually Need to Know

A DataFrame is basically an Excel spreadsheet in Python: rows, columns, index.

```python
hist = yf.Ticker("TCS.NS").history(period="1mo")

# What it looks like:
#              Open      High       Low     Close      Volume
# 2026-03-01  3850.0    3920.0    3840.0   3890.0   4500000
# 2026-03-02  3895.0    3910.0    3870.0   3875.0   3800000
# ...

# The index (row labels) is dates
# The columns are Open, High, Low, Close, Volume, Dividends, Stock Splits
```

### The key operations you need

**1. Iterate over rows** (to convert to JSON):
```python
data = []
for date_index, row in hist.iterrows():
    data.append({
        "date": str(date_index.date()),   # Convert pandas Timestamp → string
        "open": round(float(row["Open"]), 2),
        "high": round(float(row["High"]), 2),
        "low": round(float(row["Low"]), 2),
        "close": round(float(row["Close"]), 2),
        "volume": int(row["Volume"])
    })
# data is now a list of dicts — JSON-serializable, FastAPI can return it
```

**2. Check if DataFrame is empty** (no data returned):
```python
if hist.empty:
    return []   # Handle gracefully, don't crash
```

**3. Get the most recent row** (latest price from history):
```python
latest = hist.iloc[-1]   # .iloc[-1] = last row
latest_price = float(latest["Close"])
latest_date = str(hist.index[-1].date())
```

**4. Get a specific column as a list**:
```python
closing_prices = hist["Close"].tolist()
# [3890.0, 3875.0, 3901.0, ...]
```

### The most important conversion: Timestamp → string

pandas dates are `Timestamp` objects, not Python `datetime` or `str`. FastAPI can't serialize them directly. Always convert:

```python
# BAD — FastAPI throws "Object of type Timestamp is not JSON serializable"
{"date": date_index}

# GOOD
{"date": str(date_index.date())}      # "2026-03-01"
# OR
{"date": date_index.strftime("%Y-%m-%d")}   # same result
```

### The most important conversion: numpy types → Python types

yfinance uses numpy numbers internally (numpy.float64, numpy.int64). These can cause JSON serialization issues. Use `float()` and `int()` to convert:

```python
# BAD — might fail with "Object of type float64 is not JSON serializable"
{"close": row["Close"]}

# GOOD
{"close": float(row["Close"])}
{"volume": int(row["Volume"])}
```

---

## Common yfinance Pitfalls

### 1. `regularMarketPrice` is None outside market hours

NSE trades 9:15 AM – 3:30 PM IST, weekdays. Outside those hours, `info["regularMarketPrice"]` returns `None`. Use `previousClose` as a fallback:

```python
price = info.get("regularMarketPrice") or info.get("previousClose")
```

### 2. Rate limiting on bulk fetches

If you call `yf.Ticker(t).info` for 500 stocks in a tight loop, Yahoo Finance will throttle you. Add a small delay:

```python
import time
for ticker in all_tickers:
    info = yf.Ticker(ticker).info
    time.sleep(0.5)   # 500ms delay between calls
```

For even faster bulk fetches, yfinance supports `yf.download()` for multiple tickers at once (but only for price history, not `.info`):

```python
# Fetch closing prices for multiple stocks at once
data = yf.download(["TCS.NS", "INFY.NS", "WIPRO.NS"], period="1y")
# Returns a multi-level DataFrame — more complex to parse, but much faster
```

### 3. Delisted or invalid tickers return empty `.info`

```python
info = yf.Ticker("FAKE_TICKER.NS").info
# Returns {} or a dict with very few keys — no error thrown!

# Always validate:
if not info or info.get("regularMarketPrice") is None and info.get("previousClose") is None:
    return {"error": f"No data found for {ticker}"}
```

### 4. `.history()` period formats

```python
stock.history(period="1d")    # Today only
stock.history(period="5d")    # Last 5 trading days
stock.history(period="1mo")   # Last month
stock.history(period="3mo")   # Last quarter
stock.history(period="6mo")   # Last 6 months
stock.history(period="1y")    # Last year (most common)
stock.history(period="2y")    # Last 2 years
stock.history(period="5y")    # Last 5 years
stock.history(period="max")   # All available history

# Or specify exact date range:
stock.history(start="2025-01-01", end="2026-01-01")
```

---

## How We Use yfinance in FinanceAssistant

### Pattern 1: Real-time stock info for `/api/stocks/{ticker}`

```python
def get_stock_info(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Build a clean, JSON-safe dict
    return {
        "ticker": ticker,
        "name": info.get("longName", ticker),
        "current_price": info.get("regularMarketPrice") or info.get("previousClose"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector", "Unknown"),
    }
```

### Pattern 2: Historical data for price charts

```python
def get_stock_history(ticker: str, period: str = "1y") -> list[dict]:
    hist = yf.Ticker(ticker).history(period=period)
    if hist.empty:
        return []
    return [
        {
            "date": str(idx.date()),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        }
        for idx, row in hist.iterrows()
    ]
```

### Pattern 3: Text summary for ChromaDB embedding

This is the key Sprint 2 pattern — we convert stock data into a text paragraph that gets embedded as a vector:

```python
def get_stock_summary_text(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    return (
        f"Stock: {info.get('longName', ticker)} ({ticker})\n"
        f"Sector: {info.get('sector', 'Unknown')} | "
        f"Industry: {info.get('industry', 'Unknown')}\n"
        f"Current Price: ₹{info.get('regularMarketPrice') or info.get('previousClose')}\n"
        f"P/E Ratio: {info.get('trailingPE')} | "
        f"Market Cap: ₹{info.get('marketCap', 0):,}\n"
        f"52W High: ₹{info.get('fiftyTwoWeekHigh')} | "
        f"52W Low: ₹{info.get('fiftyTwoWeekLow')}"
    )
    # This text gets embedded → stored in ChromaDB → retrieved when user asks about this stock
```

The reason we convert to text (not store raw numbers) is that our embedding model works on text. When a user asks "How is TCS performing?", the semantic similarity between that question and the text summary is what drives retrieval.

---

## Quick Reference Card

| Task | Code |
|------|------|
| Get current price | `yf.Ticker("TCS.NS").info.get("regularMarketPrice")` |
| Get PE ratio | `yf.Ticker("TCS.NS").info.get("trailingPE")` |
| Get 1-year history | `yf.Ticker("TCS.NS").history(period="1y")` |
| Check if DataFrame empty | `if hist.empty: return []` |
| Convert DataFrame row to dict | `{"date": str(idx.date()), "close": float(row["Close"])}` |
| Normalize ticker for India | append `.NS` if no exchange suffix |
| Fallback when market closed | `price = info.get("regularMarketPrice") or info.get("previousClose")` |

---

## What to Try Before Sprint 2

Run this in a Python shell to get comfortable before building the full pipeline:

```python
import yfinance as yf

# 1. Fetch TCS data
tcs = yf.Ticker("TCS.NS")

# 2. Look at the info dict — explore what's available
info = tcs.info
print(info.keys())           # See all available fields
print(info.get("longName"))
print(info.get("regularMarketPrice"))
print(info.get("trailingPE"))

# 3. Get 1 month of price history
hist = tcs.history(period="1mo")
print(hist.head())           # First 5 rows
print(hist.tail())           # Last 5 rows
print(hist.shape)            # (rows, columns) — should be ~22 x 7

# 4. Convert to JSON-friendly format
for idx, row in hist.iterrows():
    print(str(idx.date()), float(row["Close"]))
    break  # Just look at the first row
```

If this runs without errors and you see real TCS prices, yfinance is working correctly on your machine.

---

*Updated: April 2026 | Next: `06-apscheduler.md`*
