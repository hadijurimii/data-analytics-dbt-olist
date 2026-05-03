# Architecture

```mermaid
flowchart LR
  csv[Olist CSV files] --> ingest[Python ingestion]
  api[Nager.Date BR holidays API] --> ingest
  ingest --> duck[(DuckDB local warehouse)]
  duck --> stg[dbt staging views]
  stg --> int[dbt intermediate facts]
  int --> marts[dbt marts]
  marts --> exports[CSV + Markdown outputs]
  prefect[Prefect local flow] --> ingest
  prefect --> stg
  prefect --> exports
```

The architecture is intentionally small: one local warehouse file, one dbt project, one orchestrated command. This is enough to demonstrate production habits without creating services that the client team would not need for a local hand-off.
