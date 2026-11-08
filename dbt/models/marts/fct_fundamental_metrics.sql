with fin as (
    select * from {{ ref('int_financials_pit') }}
    where period_type = 'annual'
),

with_prior as (
    select
        fin.*,
        lag(period_end)          over w as prior_period_end,
        lag(revenue)             over w as prior_revenue,
        lag(net_interest_income) over w as prior_net_interest_income
    from fin
    window w as (partition by ticker order by period_end)
),

flagged as (
    select
        *,
        (period_end - prior_period_end) between 350 and 380 as has_prior_year
    from with_prior
)

select
    ticker,
    period_end,
    report_date,
    report_date_source,
    currency,

    -- Quality
    case when total_equity > 0
         then net_income / total_equity end                       as roe,
    case when tangible_book_value > 0
         then net_income / tangible_book_value end                as rote,
    case when ebitda > 0
         then (total_debt - cash) / ebitda end                    as net_debt_to_ebitda,

    -- Growth (year on year, only when the prior year is genuinely the previous year)
    case when has_prior_year and prior_revenue > 0
         then revenue / prior_revenue - 1 end                     as revenue_growth,
    case when has_prior_year and prior_net_interest_income > 0
         then net_interest_income / prior_net_interest_income - 1 end as net_interest_income_growth

from flagged