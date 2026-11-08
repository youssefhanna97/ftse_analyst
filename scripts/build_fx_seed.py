"""Turn the Bank of England monthly FX download into a dbt seed."""
import pandas as pd

SERIES_TO_CURRENCY = {"XUMAUSS": "USD", "XUMAERS": "EUR"}

raw = pd.read_csv("data/boe_fx_monthly.csv")
print("Columns found:", list(raw.columns))

date_col = raw.columns[0]
long = raw.melt(id_vars=date_col, var_name="series", value_name="units_per_gbp")
long["currency"] = long["series"].map(SERIES_TO_CURRENCY)
long["month"] = pd.to_datetime(long[date_col], format="%d %b %Y").dt.to_period("M").dt.to_timestamp().dt.date
long = long.dropna(subset=["currency", "units_per_gbp"])

seed = long[["month", "currency", "units_per_gbp"]].sort_values(["currency", "month"])
seed.to_csv("dbt/seeds/fx_rates_monthly.csv", index=False)
print(f"Wrote {len(seed)} rows")
print(seed.tail(4))