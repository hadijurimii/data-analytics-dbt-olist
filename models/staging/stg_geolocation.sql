select
  geolocation_zip_code_prefix,
  avg(cast(geolocation_lat as double)) as geolocation_lat,
  avg(cast(geolocation_lng as double)) as geolocation_lng,
  min(lower(geolocation_city)) as geolocation_city,
  upper(geolocation_state) as geolocation_state
from {{ source('raw','geolocation') }}
group by 1, 5
