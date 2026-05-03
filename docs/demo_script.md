# Demo Script

1. Show the goal: local client hand-off analytics stack for Olist marketplace data.
2. Run `uv run python scripts/flow.py` or `docker compose up --build pipeline`.
3. Open DuckDB and show schemas: `raw`, `main_staging`, `main_intermediate`, `main_marts`.
4. Walk through `int_order_items_enriched` as the central analytical join.
5. Show marts answering the three fixed questions.
6. Open `report.md` and point to the two proposed stakeholder questions.
7. Explain tradeoffs: DuckDB for local analytics, dbt for modeling contracts, Prefect for simple orchestration.
8. Discuss what would change for production scale: object storage, warehouse, scheduler, CI, dashboard.
