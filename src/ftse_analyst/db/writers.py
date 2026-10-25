import pandas as pd
from sqlalchemy import Connection, MetaData, Table, func, text
from sqlalchemy.dialects.postgresql import insert

BATCH_SIZE = 1000
UPDATE_COLUMNS = ["open", "high", "low", "close", "adj_close", "volume", "currency", "source"]


def _to_records(df: pd.DataFrame) -> list[dict]:
    """Turn a DataFrame into plain Python dicts the database driver understands."""
    records = []
    for row in df.to_dict("records"):
        clean = {}
        for key, value in row.items():
            if pd.isna(value):
                clean[key] = None
            elif hasattr(value, "item"):
                clean[key] = value.item()
            else:
                clean[key] = value
        records.append(clean)
    return records


def upsert_prices(conn: Connection, df: pd.DataFrame) -> int:
    """Insert new price rows, overwrite existing ones. Returns rows written."""
    if df.empty:
        return 0
    table = Table("prices_daily", MetaData(), autoload_with=conn)
    records = _to_records(df)
    for i in range(0, len(records), BATCH_SIZE):
        stmt = insert(table).values(records[i : i + BATCH_SIZE])
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker", "trade_date"],
            set_={**{c: stmt.excluded[c] for c in UPDATE_COLUMNS}, "ingested_at": func.now()},
        )
        conn.execute(stmt)
    return len(records)


def set_quote_currency(conn: Connection, ticker: str, currency: str) -> None:
    conn.execute(
        text("UPDATE companies SET quote_currency = :currency WHERE ticker = :ticker"),
        {"currency": currency, "ticker": ticker},
    )