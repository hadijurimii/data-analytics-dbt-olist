select
  cast(holiday_date as date) as holiday_date,
  local_name,
  english_name,
  country_code,
  holiday_types,
  source
from {{ source('raw','public_holidays_br') }}
