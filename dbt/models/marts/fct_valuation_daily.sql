with prices as (
    select ticker, trade_date, close_price
    from {{ ref('stg_prices_daily') }}
),

fundamentals as (
    select
        *,
        report_date as valid_from,
        lead(report_date) over (partition by ticker order by report_date) as valid_to
    from {{ ref('int_financials_pit') }}
    where period_type = 'annual'
),

fx as (
    select
        currency,
        units_per_gbp,
        (month + interval '1 month')::date as valid_from,
        (lead(month) over (partition by currency order by month) + interval '1 month')::date as valid_to
    from {{ ref('fx_rates_monthly') }}
),

joined as (
    select
        p.ticker,
        p.trade_date,
        p.close_price,
        f.period_end  as fundamentals_period_end,
        f.report_date as fundamentals_report_date,
        f.currency    as reporting_currency,
        case when f.currency = 'GBP' then 1 else fx.units_per_gbp end as units_per_gbp,
        f.net_income,
        f.total_equity,
        f.tangible_book_value,
        f.ebitda,
        f.total_debt,
        f.cash,
        f.free_cash_flow,
        f.shares_outstanding
    from prices p
    inner join fundamentals f
        on  f.ticker = p.ticker
        and p.trade_date >= f.valid_from
        and (f.valid_to is null or p.trade_date < f.valid_to)
    left join fx
        on  fx.currency = f.currency
        and p.trade_date >= fx.valid_from
        and (fx.valid_to is null or p.trade_date < fx.valid_to)
),

caps as (
    select
        *,
        close_price * shares_outstanding                 as market_cap_gbp,
        close_price * shares_outstanding * units_per_gbp as market_cap_rc
    from joined
)

select
    ticker,
    trade_date,
    close_price,
    fundamentals_period_end,
    fundamentals_report_date,
    reporting_currency,
    units_per_gbp,
    market_cap_gbp,
    market_cap_rc,
    market_cap_rc + total_debt - cash                                  as enterprise_value_rc,
    case when net_income > 0          then market_cap_rc / net_income end          as pe_ratio,
    case when total_equity > 0        then market_cap_rc / total_equity end        as pb_ratio,
    case when tangible_book_value > 0 then market_cap_rc / tangible_book_value end as ptb_ratio,
    case when ebitda > 0
         then (market_cap_rc + total_debt - cash) / ebitda end                     as ev_to_ebitda,
    case when market_cap_rc > 0       then free_cash_flow / market_cap_rc end      as fcf_yield
from caps