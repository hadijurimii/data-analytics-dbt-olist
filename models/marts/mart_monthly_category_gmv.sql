with monthly as (
  select
    order_month,
    product_category,
    count(distinct order_id) as orders,
    sum(price) as gmv,
    sum(freight_value) as freight_value,
    sum(case when is_public_holiday then price else 0 end) as holiday_day_gmv,
    count(distinct case when is_public_holiday then order_id end) as holiday_day_orders
  from {{ ref('int_order_items_enriched') }}
  group by 1, 2
), with_yoy as (
  select
    *,
    lag(gmv, 12) over (partition by product_category order by order_month) as gmv_prior_year
  from monthly
), stats as (
  select
    product_category,
    avg(gmv) as avg_gmv,
    stddev_samp(gmv) as sd_gmv
  from monthly
  group by 1
)
select
  w.*,
  case when gmv_prior_year > 0 then (gmv - gmv_prior_year) / gmv_prior_year end as yoy_growth_rate,
  case when s.sd_gmv > 0 then (w.gmv - s.avg_gmv) / s.sd_gmv end as anomaly_z_score,
  case when s.sd_gmv > 0 and abs((w.gmv - s.avg_gmv) / s.sd_gmv) >= 2 then true else false end as is_anomaly_month,
  case when w.gmv > 0 then holiday_day_gmv / w.gmv else 0 end as holiday_gmv_share
from with_yoy w
left join stats s using (product_category)
