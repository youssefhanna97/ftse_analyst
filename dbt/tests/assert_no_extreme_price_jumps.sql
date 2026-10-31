-- Fails if any day's close is more than 3x (or under a third of) the previous day's close.
-- Catches pence/pound mix-ups like the ones found in the 1990s ULVR data.
with prices as (
    select
        ticker,
        trade_date,
        close_price,
        lag(close_price) over (partition by ticker order by trade_date) as prev_close
    from {{ ref('stg_prices_daily') }}
)

select *
from prices
where prev_close is not null
  and (close_price / prev_close > 3 or close_price / prev_close < 0.33)