select
  date_trunc('month', o.order_purchase_date)::date as order_month,
  p.payment_type,
  count(distinct o.order_id) as orders,
  sum(p.payment_value) as payment_value,
  avg(p.payment_installments) as avg_installments
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_payments') }} p using (order_id)
where o.order_status = 'delivered'
group by 1, 2
