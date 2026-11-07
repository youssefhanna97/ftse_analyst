with raw as (
    select * from {{ source('bronze', 'financials_raw') }}
),

item_map as (
    select * from {{ ref('line_item_map') }}
)

select
    raw.ticker,
    raw.statement,
    raw.period_type,
    raw.period_end,
    item_map.item,
    raw.value,
    raw.currency
from raw
inner join item_map
    on  raw.statement = item_map.statement
    and raw.line_item = item_map.source_line_item