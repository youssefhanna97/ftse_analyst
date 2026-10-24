CREATE TABLE IF NOT EXISTS companies (
    ticker                 TEXT PRIMARY KEY,
    name                   TEXT NOT NULL,
    sector                 TEXT NOT NULL
        CHECK (sector IN ('Banks', 'Energy & Utilities', 'Miners',
                          'Consumer', 'Pharma & Health')),
    index_at_selection     TEXT CHECK (index_at_selection IN ('FTSE 100', 'FTSE 250')),
    quote_currency         TEXT,
    companies_house_number TEXT,
    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);