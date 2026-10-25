import pandas as pd
import yfinance as yf
import warnings

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


def fetch_raw(ticker: str, period: str = "max", start: str | None = None) -> tuple[pd.DataFrame, str]:
    """Download raw daily data from yfinance. Returns (data, quote_currency)."""
    t = yf.Ticker(ticker)
    if start:
        raw = t.history(start=start, auto_adjust=False)
    else:
        raw = t.history(period=period, auto_adjust=False)
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