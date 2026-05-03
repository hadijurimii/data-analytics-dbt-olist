"""Export business-question outputs from DuckDB marts to CSV and Markdown."""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = ROOT / "data" / "warehouse" / "olist.duckdb"
OUTPUT = ROOT / "output"
REPORT = ROOT / "report.md"

QUERY_MAP = {
    "q1_top_monthly_category_gmv": """
        select order_month, product_category, orders, round(gmv, 2) as gmv,
               round(yoy_growth_rate * 100, 2) as yoy_growth_pct,
               round(anomaly_z_score, 2) as anomaly_z_score,
               is_anomaly_month, round(holiday_gmv_share * 100, 2) as holiday_gmv_share_pct
        from main_marts.mart_monthly_category_gmv
        order by gmv desc
        limit 20
    """,
    "q1_anomaly_months": """
        select order_month, product_category, round(gmv, 2) as gmv,
               round(anomaly_z_score, 2) as anomaly_z_score,
               round(holiday_gmv_share * 100, 2) as holiday_gmv_share_pct,
               holiday_day_orders
        from main_marts.mart_monthly_category_gmv
        where is_anomaly_month
        order by abs(anomaly_z_score) desc, gmv desc
        limit 30
    """,
    "q2_best_repeat_states": """
        select customer_state, sum(customers) as customers,
               sum(repeat_customers_90d) as repeat_customers_90d,
               round(100 * sum(repeat_customers_90d)::double / nullif(sum(customers),0), 2) as repeat_rate_90d_pct
        from main_marts.mart_customer_cohorts_state
        group by 1
        having sum(customers) >= 500
        order by repeat_rate_90d_pct desc
        limit 15
    """,
    "q2_recent_cohorts": """
        select cohort_month, customer_state, customers, repeat_customers_90d,
               round(repeat_rate_90d * 100, 2) as repeat_rate_90d_pct
        from main_marts.mart_customer_cohorts_state
        where customers >= 20
        order by cohort_month desc, customers desc
        limit 30
    """,
    "q3_delivery_review_segments": """
        select product_category, shipment_scope, delivery_status, orders,
               round(avg_review_score, 2) as avg_review_score,
               round(avg_days_late, 2) as avg_days_late,
               round(low_review_share * 100, 2) as low_review_share_pct
        from main_marts.mart_delivery_review_segmentation
        where orders >= 100
        order by avg_review_score asc, orders desc
        limit 30
    """,
    "q4_payment_mix": """
        select payment_type, sum(orders) as orders, round(sum(payment_value), 2) as payment_value,
               round(avg(avg_installments), 2) as avg_installments
        from main_marts.mart_payment_mix_monthly
        group by 1
        order by payment_value desc
    """,
    "q5_customer_ltv_state": """
        select customer_state, customers, round(avg_customer_gmv, 2) as avg_customer_gmv,
               round(median_customer_gmv, 2) as median_customer_gmv,
               round(total_gmv, 2) as total_gmv,
               round(repeat_customer_share * 100, 2) as repeat_customer_share_pct
        from main_marts.mart_customer_ltv_state
        where customers >= 500
        order by avg_customer_gmv desc
        limit 15
    """,
}


def md_table(df: pd.DataFrame, max_rows: int = 15) -> str:
    if df.empty:
        return "No rows returned."
    view = df.head(max_rows).copy()
    cols = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in view.iterrows():
        vals = [str(row[c]).replace("|", "\\|") for c in view.columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    frames: dict[str, pd.DataFrame] = {}
    for name, sql in QUERY_MAP.items():
        df = con.execute(sql).fetchdf()
        frames[name] = df
        df.to_csv(OUTPUT / f"{name}.csv", index=False)

    report = f"""# Lance Data Presentation Report

## Index
1. Executive summary
2. Architecture and run commands
3. Data model
4. Business-question answers
5. Data quality notes
6. Interview defence notes
7. Output inventory

## 1. Executive summary

This project builds a local analytics stack for the Olist Brazilian e-commerce dataset. It ingests raw CSVs plus Brazilian public holidays, loads them into DuckDB, models the warehouse with dbt, orchestrates the full run with Prefect, and exports CSV/Markdown outputs for client-facing analysis.

Key analytical stance: keep the stack small enough to defend live, but shaped like production: raw/staging/intermediate/marts, idempotent ingestion, dbt tests, one orchestration entrypoint, documented assumptions, and reproducible Docker Compose execution.

## 2. Architecture and run commands

```mermaid
flowchart LR
  A[Olist CSVs in data/raw] --> B[Python ingestion]
  H[Nager.Date public holidays] --> B
  B --> C[(DuckDB data/warehouse/olist.duckdb)]
  C --> D[dbt staging]
  D --> E[dbt intermediate]
  E --> F[dbt marts]
  F --> G[analysis CSV + report exports]
  P[Prefect flow] --> B
  P --> D
  P --> G
```

Primary command:

```bash
uv run python scripts/flow.py
```

Docker command:

```bash
docker compose up --build pipeline
```

## 3. Data model

Raw source tables are loaded into DuckDB schema `raw`. dbt builds:

- `main_staging`: light type normalization and column cleanup.
- `main_intermediate`: business-grain facts for delivered orders, items, and customer order sequence.
- `main_marts`: query-ready tables for revenue, cohorts, delivery/reviews, payment mix, and customer value.

```mermaid
erDiagram
  CUSTOMERS ||--o{{ ORDERS : places
  ORDERS ||--o{{ ORDER_ITEMS : contains
  ORDERS ||--o{{ PAYMENTS : paid_by
  ORDERS ||--o{{ REVIEWS : reviewed_by
  PRODUCTS ||--o{{ ORDER_ITEMS : purchased_as
  SELLERS ||--o{{ ORDER_ITEMS : sells
  HOLIDAYS ||--o{{ ORDERS : enriches_purchase_date
```

## 4. Business-question answers

### Q1. Revenue and seasonality

Monthly GMV by category is exported in `output/q1_top_monthly_category_gmv.csv`. YoY growth is calculated when a prior-year month exists for the same category. Anomalies use a simple z-score by category, which is easy to explain and enough for a technical test.

Top monthly category GMV rows:

{md_table(frames['q1_top_monthly_category_gmv'])}

Anomaly months:

{md_table(frames['q1_anomaly_months'])}

Holiday interpretation: public holidays are useful context, but they do not automatically explain category-level spikes. The exported `holiday_gmv_share_pct` shows whether revenue was concentrated on actual holiday dates. For most anomalies, the safer recommendation is to investigate promotions, marketplace campaigns, and supply/category events before attributing causality to holidays.

### Q2. Customer cohort and repeat behaviour

Repeat behavior is measured as customers who place a second delivered order within 90 days of their first delivered purchase, grouped by first-purchase month and customer state.

Best repeat states with meaningful volume:

{md_table(frames['q2_best_repeat_states'])}

Recent cohort/state rows:

{md_table(frames['q2_recent_cohorts'])}

Interpretation: repeat rates in this dataset are generally low, which fits a marketplace with many one-off purchases. The best client action is to separate acquisition-heavy states from retention opportunities, then inspect category mix and delivery experience for states with relatively higher repeat behavior.

### Q3. Delivery performance vs review score

The mart segments reviews by on-time status, same-state versus cross-state shipment, and product category.

Lowest-scoring high-volume segments:

{md_table(frames['q3_delivery_review_segments'])}

Recommendation: prioritize late/cross-state segments with both high order volume and low review score. Those segments are more actionable than tiny categories with extreme averages. Investigate seller dispatch latency, carrier routes, and expectation-setting on estimated delivery dates.

### Q4. Proposed stakeholder question: How does payment method mix affect cash and customer experience?

Payment mix:

{md_table(frames['q4_payment_mix'])}

Reason for asking: finance and product teams care about payment method adoption, installment behavior, and operational exposure. This is a practical stakeholder question because Brazil has strong installment-card behavior.

### Q5. Proposed stakeholder question: Which states have the strongest customer value?

State-level customer value:

{md_table(frames['q5_customer_ltv_state'])}

Reason for asking: commercial teams need to know where customer value is concentrated, not just where order counts are highest. This helps prioritize regional campaigns and seller acquisition.

## 5. Data quality notes

- Analysis is restricted to delivered orders for operational comparability.
- GMV uses item price, excluding freight unless explicitly shown.
- Review scores are averaged at order/item segment level; review text is not modeled.
- Product categories use English translation where available and fall back to Portuguese or `unknown`.
- Public holiday enrichment comes from Nager.Date, with a static fallback for resilience.
- Same-state/cross-state uses customer state vs seller state, not physical route distance.

## 6. Interview defence notes

- DuckDB is appropriate because the dataset is small-to-medium, local, and analytical.
- dbt enforces a defensible modeling contract and makes SQL reviewable.
- Prefect is used as a lightweight local orchestrator, not as an overbuilt server deployment.
- Docker Compose proves reproducibility without pretending this needs cloud infrastructure.
- The model deliberately avoids ML, streaming, and dashboard overbuild because the rubric rewards explainability.

Common change request responses:

- Add a new enrichment: create one ingestion function, one raw table, one staging model, then join in marts.
- Add a dashboard: consume `main_marts` tables or exported CSVs; do not query raw tables directly.
- Scale beyond local: replace DuckDB with Postgres/BigQuery/Snowflake and keep dbt layers mostly intact.

## 7. Output inventory

Generated CSV outputs:

"""
    for name in QUERY_MAP:
        report += f"- `output/{name}.csv`\n"
    report += "\n"
    REPORT.write_text(report, encoding="utf-8")
    (OUTPUT / "analysis_summary.md").write_text(report, encoding="utf-8")
    con.close()
    print(f"Exported {len(QUERY_MAP)} analysis outputs and refreshed report.md")


if __name__ == "__main__":
    main()
