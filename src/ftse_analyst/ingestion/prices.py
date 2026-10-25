import pandas as pd
import yfinance as yf
import warnings
from ftse_analyst.db.connection import get_engine
from ftse_analyst.db.writers import set_quote_currency, upsert_prices
import logging
import time
from sqlalchemy import text
from ftse_analyst.config import settings

log = logging.getLogger(__name__)

# yfinance uses pandas' deprecated inplace= style; harmless, so hide it to keep logs readable
warnings.filterwarnings("ignore", message=".*inplace keyword.*", module="yfinance")

PENCE_CURRENCIES = {"GBp", "GBX"}
POUND_CURRENCIES = {"GBP"}

COLUMN_MAP = {
    "Open": "open", "High": "high", "Low": "low",
    "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
}
PRICE_COLUMNS = ["open", "high", "low", "close", "adj_close"]
OUTPUT_COLUMNS = ["ticker", "trade_date", *PRICE_COLUMNS, "volume", "currency", "source"]


def fetch_raw(ticker: str, period: str | None = None, start: str | None = None) -> tuple[pd.DataFrame, str]:
    """Download raw daily data. Default: from the configured history start date."""
    t = yf.Ticker(ticker)
    if period:
        raw = t.history(period=period, auto_adjust=False)
    else:
        raw = t.history(start=start or settings.price_history_start, auto_adjust=False)
    return raw, t.fast_info.currency


def normalise(raw: pd.DataFrame, ticker: str, currency: str) -> pd.DataFrame:
    """Convert raw yfinance data into rows matching the prices_daily table, in pounds."""
    if raw.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    if currency in PENCE_CURRENCIES:
        factor = 0.01
    elif currency in POUND_CURRENCIES:
        factor = 1.0
    else:
        raise ValueError(f"{ticker}: unsupported quote currency {currency!r}")

    df = raw.rename(columns=COLUMN_MAP)[list(COLUMN_MAP.values())].copy()
    df[PRICE_COLUMNS] = (df[PRICE_COLUMNS] * factor).round(6)
    df["trade_date"] = df.index.date
    df["ticker"] = ticker
    df["currency"] = "GBP"
    df["source"] = "yfinance"
    df = df.dropna(subset=["close"])
    df["volume"] = df["volume"].astype("Int64")
    return df.reset_index(drop=True)[OUTPUT_COLUMNS]

def ingest_ticker(ticker: str, period: str | None = None, start: str | None = None) -> int:
    """Fetch, normalise and load one ticker. Returns rows written."""
    raw, currency = fetch_raw(ticker, period=period, start=start)
    df = normalise(raw, ticker, currency)
    with get_engine().begin() as conn:
        set_quote_currency(conn, ticker, currency)
        return upsert_prices(conn, df)
    
def active_tickers() -> list[str]:
    """The universe, read from the companies table."""
    with get_engine().connect() as conn:
        rows = conn.execute(text("SELECT ticker FROM companies WHERE is_active ORDER BY ticker"))
        return list(rows.scalars())


def ingest_universe(period: str | None = None, start: str | None = None, pause_seconds: float = 1.0) -> dict[str, int]:
    """Ingest every active ticker. Keeps going on failure, raises at the end if any failed."""
    loaded: dict[str, int] = {}
    failed: dict[str, str] = {}
    for ticker in active_tickers():
        try:
            loaded[ticker] = ingest_ticker(ticker, period=period, start=start)
            log.info("%s: %d rows", ticker, loaded[ticker])
        except Exception as exc:
            failed[ticker] = str(exc)
            log.exception("%s: failed", ticker)
        time.sleep(pause_seconds)

    log.info("Finished: %d succeeded, %d failed", len(loaded), len(failed))
    if failed:
        raise RuntimeError(f"Price ingestion failed for: {sorted(failed)}")
    return loaded