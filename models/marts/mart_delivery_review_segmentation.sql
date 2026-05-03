select
  product_category,
  shipment_scope,
  case when is_on_time then 'on_time' else 'late_or_unknown' end as delivery_status,
  count(distinct order_id) as orders,
  avg(review_score) as avg_review_score,
  median(review_score) as median_review_score,
  avg(days_late) as avg_days_late,
  sum(case when review_score <= 2 then 1 else 0 end)::double / nullif(count(*), 0) as low_review_share
from {{ ref('int_order_items_enriched') }}
where review_score is not null
group by 1, 2, 3
