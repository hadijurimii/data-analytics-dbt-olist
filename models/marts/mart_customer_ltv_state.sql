with customer_value as (
  select
    customer_unique_id,
    any_value(customer_state) as customer_state,
    count(distinct order_id) as delivered_orders,
    sum(order_gmv) as lifetime_gmv,
    min(order_purchase_date) as first_purchase_date,
    max(order_purchase_date) as last_purchase_date
  from {{ ref('int_customer_orders') }}
  group by 1
)
select
  customer_state,
  count(*) as customers,
  avg(lifetime_gmv) as avg_customer_gmv,
  median(lifetime_gmv) as median_customer_gmv,
  sum(lifetime_gmv) as total_gmv,
  avg(delivered_orders) as avg_delivered_orders,
  sum(case when delivered_orders >= 2 then 1 else 0 end)::double / nullif(count(*), 0) as repeat_customer_share
from customer_value
group by 1
