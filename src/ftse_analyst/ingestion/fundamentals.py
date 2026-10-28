import warnings

import pandas as pd
import yfinance as yf

from ftse_analyst.db.connection import get_engine
from ftse_analyst.db.writers import upsert_financials
from ftse_analyst.ingestion.universe import run_for_universe

warnings.filterwarnings("ignore", message=".*inplace keyword.*", module="yfinance")

# (statement, period_type) -> yfinance attribute name
STATEMENTS = {
    ("income", "annual"): "income_stmt",
    ("income", "quarterly"): "quarterly_income_stmt",
    ("balance", "annual"): "balance_sheet",
    ("balance", "quarterly"): "quarterly_balance_sheet",
    ("cashflow", "annual"): "cashflow",
    ("cashflow", "quarterly"): "quarterly_cashflow",
}
OUTPUT_COLUMNS = [
    "ticker", "statement", "period_type", "period_end",
    "line_item", "value", "currency", "source",
]


def fetch_raw_statements(ticker: str) -> tuple[dict[tuple[str, str], pd.DataFrame], str | None]:
    """Download all six wide statements plus the reporting currency."""
    t = yf.Ticker(ticker)
    frames = {key: getattr(t, attr) for key, attr in STATEMENTS.items()}
    return frames, t.info.get("financialCurrency")


def to_long(wide: pd.DataFrame, ticker: str, statement: str, period_type: str, currency: str) -> pd.DataFrame:
    """Reshape one wide statement (line items x dates) into long rows. Values untouched."""
    if wide is None or wide.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    long = (
        wide.rename_axis("line_item")
        .reset_index()
        .melt(id_vars="line_item", var_name="period_end", value_name="value")
        .dropna(subset=["value"])
    )
    long["period_end"] = pd.to_datetime(long["period_end"]).dt.date
    long["value"] = long["value"].astype(float)
    long["ticker"] = ticker
    long["statement"] = statement
    long["period_type"] = period_type
    long["currency"] = currency
    long["source"] = "yfinance"
    return long.reset_index(drop=True)[OUTPUT_COLUMNS]


def normalise_statements(frames: dict[tuple[str, str], pd.DataFrame], ticker: str, currency: str | None) -> pd.DataFrame:
    """Combine all six statements into one long DataFrame."""
    if not currency:
        raise ValueError(f"{ticker}: yfinance returned no reporting currency")
    parts = [to_long(df, ticker, s, p, currency) for (s, p), df in frames.items()]
    parts = [p for p in parts if not p.empty]
    if not parts:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return pd.concat(parts, ignore_index=True)

def ingest_ticker_fundamentals(ticker: str) -> int:
    """Fetch, reshape and load all statements for one ticker. Returns rows written."""
    frames, currency = fetch_raw_statements(ticker)
    df = normalise_statements(frames, ticker, currency)
    with get_engine().begin() as conn:
        return upsert_financials(conn, df)


def ingest_universe_fundamentals(pause_seconds: float = 1.0) -> dict[str, int]:
    return run_for_universe(ingest_ticker_fundamentals, "fundamentals", pause_seconds)