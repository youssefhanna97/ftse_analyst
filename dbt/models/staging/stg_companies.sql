select
    ticker,
    name as company_name,
    sector,
    index_at_selection,
    quote_currency,
    is_active
from {{ source('bronze', 'companies') }}