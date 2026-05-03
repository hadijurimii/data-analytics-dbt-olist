with item_base as (
  select
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.price,
    oi.freight_value,
    coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as product_category,
    s.seller_state
  from {{ ref('stg_order_items') }} oi
  left join {{ ref('stg_products') }} p using (product_id)
  left join {{ ref('stg_product_category_translation') }} t using (product_category_name)
  left join {{ ref('stg_sellers') }} s using (seller_id)
), reviews as (
  select order_id, avg(review_score) as review_score
  from {{ ref('stg_order_reviews') }}
  group by 1
), payments as (
  select order_id, sum(payment_value) as payment_value
  from {{ ref('stg_order_payments') }}
  group by 1
), order_totals as (
  select order_id, sum(price) as order_gmv, sum(freight_value) as freight_value
  from item_base
  group by 1
)
select
  o.order_id,
  o.customer_id,
  c.customer_unique_id,
  c.customer_state,
  o.order_status,
  o.order_purchase_ts,
  o.order_purchase_date,
  date_trunc('month', o.order_purchase_date)::date as order_month,
  o.order_delivered_customer_ts,
  o.order_estimated_delivery_ts,
  case when o.order_delivered_customer_ts is not null and o.order_estimated_delivery_ts is not null
    then datediff('day', o.order_estimated_delivery_ts::date, o.order_delivered_customer_ts::date) end as days_late,
  case when o.order_delivered_customer_ts is not null and o.order_estimated_delivery_ts is not null
    then o.order_delivered_customer_ts <= o.order_estimated_delivery_ts end as is_on_time,
  ot.order_gmv,
  ot.freight_value,
  p.payment_value,
  r.review_score,
  h.holiday_date is not null as is_public_holiday,
  h.english_name as holiday_name
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c using (customer_id)
left join order_totals ot using (order_id)
left join payments p using (order_id)
left join reviews r using (order_id)
left join {{ ref('stg_public_holidays_br') }} h on o.order_purchase_date = h.holiday_date
where o.order_status = 'delivered'
