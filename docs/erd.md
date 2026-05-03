# ERD

```mermaid
erDiagram
  CUSTOMERS ||--o{ ORDERS : places
  ORDERS ||--o{ ORDER_ITEMS : contains
  ORDERS ||--o{ ORDER_PAYMENTS : has
  ORDERS ||--o{ ORDER_REVIEWS : receives
  PRODUCTS ||--o{ ORDER_ITEMS : describes
  SELLERS ||--o{ ORDER_ITEMS : fulfils
  CATEGORY_TRANSLATION ||--o{ PRODUCTS : translates
  PUBLIC_HOLIDAYS_BR ||--o{ ORDERS : enriches_date
```

The dbt marts are derived from this operational shape but are modeled at analytical grains: monthly category revenue, customer cohorts by state, delivery/review segments, payment mix, and customer value by state.
