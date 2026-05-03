with customers as (
  select
    customer_unique_id,
    any_value(customer_state) as customer_state,
    min(cohort_month) as cohort_month,
    min(first_purchase_ts) as first_purchase_ts,
    count(distinct order_id) as delivered_orders,
    max(case when customer_order_number >= 2 and days_since_first_purchase between 1 and 90 then 1 else 0 end) as repeated_within_90d
  from {{ ref('int_customer_orders') }}
  group by 1
)
select
  cohort_month,
  customer_state,
  count(*) as customers,
  sum(repeated_within_90d) as repeat_customers_90d,
  sum(repeated_within_90d)::double / nullif(count(*), 0) as repeat_rate_90d,
  avg(delivered_orders) as avg_delivered_orders_per_customer
from customers
group by 1, 2
