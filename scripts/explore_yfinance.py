import yfinance as yf
from sqlalchemy import text

from ftse_analyst.db.connection import get_engine

# Read our universe from the database instead of hardcoding it
with get_engine().connect() as conn:
    tickers = conn.execute(text("SELECT ticker FROM companies ORDER BY ticker")).scalars().all()

# 1. Raw daily data for one stock
shel = yf.Ticker("SHEL.L")
print(shel.history(period="5d", auto_adjust=False))

# 2. The quote currency of every stock
print()
for t in tickers:
    print(f"{t:8} {yf.Ticker(t).fast_info.currency}")