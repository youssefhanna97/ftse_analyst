with financials as (
    select * from {{ ref('stg_financials') }}
),

wide as (
    select
        ticker,
        period_type,
        period_end,
        currency,
        max(value) filter (where item = 'revenue')             as revenue,
        max(value) filter (where item = 'net_income')          as net_income,
        max(value) filter (where item = 'ebitda')              as ebitda,
        max(value) filter (where item = 'net_interest_income') as net_interest_income,
        max(value) filter (where item = 'total_equity')        as total_equity,
        max(value) filter (where item = 'tangible_book_value') as tangible_book_value,
        max(value) filter (where item = 'total_debt')          as total_debt,
        max(value) filter (where item = 'cash')                as cash,
        max(value) filter (where item = 'shares_outstanding')  as shares_outstanding,
        max(value) filter (where item = 'free_cash_flow')      as free_cash_flow
    from financials
    group by ticker, period_type, period_end, currency
)

select
    wide.*,
    (
        period_end + case period_type
            when 'annual' then interval '{{ var("annual_report_lag_months") }} months'
            else interval '{{ var("interim_report_lag_months") }} months'
        end
    )::date as report_date,
    'estimated_lag' as report_date_source
from wide