select
  order_id,
  customer_id,
  order_status,
  try_cast(order_purchase_timestamp as timestamp) as order_purchase_ts,
  try_cast(order_approved_at as timestamp) as order_approved_ts,
  try_cast(order_delivered_carrier_date as timestamp) as order_delivered_carrier_ts,
  try_cast(order_delivered_customer_date as timestamp) as order_delivered_customer_ts,
  try_cast(order_estimated_delivery_date as timestamp) as order_estimated_delivery_ts,
  cast(try_cast(order_purchase_timestamp as timestamp) as date) as order_purchase_date
from {{ source('raw','orders') }}
