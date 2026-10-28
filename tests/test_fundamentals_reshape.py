import numpy as np
import pandas as pd
import pytest

from ftse_analyst.ingestion.fundamentals import normalise_statements, to_long


def make_wide() -> pd.DataFrame:
    """Fake yfinance statement: 2 line items x 2 periods, one period fully empty."""
    return pd.DataFrame(
        {
            pd.Timestamp("2025-12-31"): [100.0, 20.0],
            pd.Timestamp("2021-12-31"): [np.nan, np.nan],
        },
        index=["Total Revenue", "Net Income"],
    )


def test_wide_becomes_long_and_empty_cells_dropped():
    df = to_long(make_wide(), "SHEL.L", "income", "annual", "USD")
    assert len(df) == 2
    assert set(df["line_item"]) == {"Total Revenue", "Net Income"}


def test_values_and_dates_unchanged():
    df = to_long(make_wide(), "SHEL.L", "income", "annual", "USD")
    revenue = df[df["line_item"] == "Total Revenue"].iloc[0]
    assert revenue["value"] == 100.0
    assert str(revenue["period_end"]) == "2025-12-31"
    assert revenue["currency"] == "USD"


def test_missing_currency_is_rejected():
    frames = {("income", "annual"): make_wide()}
    with pytest.raises(ValueError):
        normalise_statements(frames, "SHEL.L", None)