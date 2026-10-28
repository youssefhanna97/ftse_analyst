CREATE TABLE IF NOT EXISTS financials_raw (
    ticker       TEXT        NOT NULL REFERENCES companies(ticker),
    statement    TEXT        NOT NULL CHECK (statement IN ('income', 'balance', 'cashflow')),
    period_type  TEXT        NOT NULL CHECK (period_type IN ('annual', 'quarterly')),
    period_end   DATE        NOT NULL,
    line_item    TEXT        NOT NULL,
    value        NUMERIC     NOT NULL,
    currency     TEXT        NOT NULL,
    source       TEXT        NOT NULL DEFAULT 'yfinance',
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (ticker, statement, period_type, period_end, line_item)
);

CREATE INDEX IF NOT EXISTS ix_financials_raw_line_item
    ON financials_raw (line_item);