{{ config(severity='warn') }}

-- Warns if the FX seed hasn't been refreshed for over 2 months.
select max(month) as latest_fx_month
from {{ ref('fx_rates_monthly') }}
having max(month) < current_date - interval '62 days'