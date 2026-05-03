select
  review_id,
  order_id,
  review_score,
  review_comment_title,
  review_comment_message,
  try_cast(review_creation_date as timestamp) as review_creation_ts,
  try_cast(review_answer_timestamp as timestamp) as review_answer_ts
from {{ source('raw','order_reviews') }}
