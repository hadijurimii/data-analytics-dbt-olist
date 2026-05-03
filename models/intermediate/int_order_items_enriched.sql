select
  o.order_id,
  o.customer_id,
  c.customer_unique_id,
  c.customer_state,
  o.order_purchase_ts,
  o.order_purchase_date,
  date_trunc('month', o.order_purchase_date)::date as order_month,
  oi.order_item_id,
  oi.product_id,
  oi.seller_id,
  oi.price,
  oi.freight_value,
  coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as product_category,
  s.seller_state,
  case when s.seller_state = c.customer_state then 'same_state' else 'cross_state' end as shipment_scope,
  case when o.order_delivered_customer_ts is not null and o.order_estimated_delivery_ts is not null
    then o.order_delivered_customer_ts <= o.order_estimated_delivery_ts end as is_on_time,
  case when o.order_delivered_customer_ts is not null and o.order_estimated_delivery_ts is not null
    then datediff('day', o.order_estimated_delivery_ts::date, o.order_delivered_customer_ts::date) end as days_late,
  r.review_score,
  h.holiday_date is not null as is_public_holiday,
  h.english_name as holiday_name
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_items') }} oi using (order_id)
left join {{ ref('stg_customers') }} c using (customer_id)
left join {{ ref('stg_products') }} p using (product_id)
left join {{ ref('stg_product_category_translation') }} t using (product_category_name)
left join {{ ref('stg_sellers') }} s using (seller_id)
left join {{ ref('stg_order_reviews') }} r using (order_id)
left join {{ ref('stg_public_holidays_br') }} h on o.order_purchase_date = h.holiday_date
where o.order_status = 'delivered'
