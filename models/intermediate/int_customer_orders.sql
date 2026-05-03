with orders as (
  select
    order_id,
    customer_unique_id,
    customer_state,
    order_purchase_ts,
    order_purchase_date,
    order_month,
    order_gmv,
    row_number() over (partition by customer_unique_id order by order_purchase_ts, order_id) as customer_order_number,
    min(order_purchase_ts) over (partition by customer_unique_id) as first_purchase_ts
  from {{ ref('int_order_enriched') }}
  where customer_unique_id is not null
)
select
  *,
  date_trunc('month', first_purchase_ts)::date as cohort_month,
  datediff('day', first_purchase_ts::date, order_purchase_ts::date) as days_since_first_purchase
from orders
