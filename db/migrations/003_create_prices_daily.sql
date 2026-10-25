CREATE TABLE IF NOT EXISTS prices_daily (
    ticker       TEXT          NOT NULL REFERENCES companies(ticker),
    trade_date   DATE          NOT NULL,
    open         NUMERIC(18,6),
    high         NUMERIC(18,6),
    low          NUMERIC(18,6),
    close        NUMERIC(18,6) NOT NULL CHECK (close > 0),
    adj_close    NUMERIC(18,6),
    volume       BIGINT,
    currency     TEXT          NOT NULL DEFAULT 'GBP',
    source       TEXT          NOT NULL DEFAULT 'yfinance',
    ingested_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    PRIMARY KEY (ticker, trade_date)
);

SELECT create_hypertable(
    'prices_daily',
    by_range('trade_date', INTERVAL '1 year'),
    if_not_exists => TRUE
);