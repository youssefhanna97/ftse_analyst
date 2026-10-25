import pandas as pd
import pytest

from ftse_analyst.ingestion.prices import normalise


def make_raw() -> pd.DataFrame:
    """Fake yfinance output: two days of Shell-like prices in pence."""
    idx = pd.DatetimeIndex(["2026-10-22", "2026-10-23"]).tz_localize("Europe/London")
    return pd.DataFrame(
        {
            "Open": [2700.0, 2710.0], "High": [2720.0, 2730.0], "Low": [2690.0, 2700.0],
            "Close": [2715.0, 2725.0], "Adj Close": [2715.0, 2725.0],
            "Volume": [1000, 2000], "Dividends": [0.0, 0.0], "Stock Splits": [0.0, 0.0],
        },
        index=idx,
    )


def test_pence_converted_to_pounds():
    df = normalise(make_raw(), "SHEL.L", "GBp")
    assert df["close"].tolist() == [27.15, 27.25]
    assert (df["currency"] == "GBP").all()


def test_dates_have_no_time_or_timezone():
    df = normalise(make_raw(), "SHEL.L", "GBp")
    assert str(df["trade_date"].iloc[0]) == "2026-10-22"


def test_unknown_currency_is_rejected():
    with pytest.raises(ValueError):
        normalise(make_raw(), "XYZ.L", "USD")