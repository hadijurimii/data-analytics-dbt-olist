# Change Requests

| Request | Response |
|---|---|
| Add another enrichment source | Add ingestion function/table, staging model, then join into relevant marts. |
| Move from local to cloud | Keep dbt logic, swap DuckDB for warehouse adapter, schedule flow in managed orchestrator. |
| Add dashboard | Use marts or exported CSVs. Do not query raw tables directly. |
| Improve anomaly detection | Replace z-score with STL decomposition or rolling baselines after validating business calendar effects. |
| Add data freshness checks | Extend ingestion manifest and add dbt source freshness or custom audit queries. |
