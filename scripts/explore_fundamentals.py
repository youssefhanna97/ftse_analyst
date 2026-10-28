import time
import warnings

import pandas as pd
import yfinance as yf
from sqlalchemy import text

from ftse_analyst.db.connection import get_engine

warnings.filterwarnings("ignore", message=".*inplace keyword.*", module="yfinance")
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 100)

shel = yf.Ticker("SHEL.L")

print("=== 1. Annual income statement (SHEL.L) ===")
print(shel.income_stmt)

print("\n=== 2. Quarterly income statement, first 10 rows (SHEL.L) ===")
print(shel.quarterly_income_stmt.head(10))

print("\n=== 3. Balance sheet line items available (SHEL.L) ===")
print(list(shel.balance_sheet.index))

print("\n=== 4. Quote currency vs reporting currency, all stocks ===")
with get_engine().connect() as conn:
    tickers = conn.execute(text("SELECT ticker FROM companies ORDER BY ticker")).scalars().all()
for t in tickers:
    info = yf.Ticker(t).info
    print(f"{t:8} quote={info.get('currency')}  financials={info.get('financialCurrency')}")
    time.sleep(1)