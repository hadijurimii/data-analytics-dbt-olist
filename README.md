# data-analytics-dbt-olist

# 🚀 Lance Data Engineering Project  
**End-to-End Analytics Pipeline on Olist E-commerce Dataset**

---

## 🌟 Overview

This project builds a **production-style data platform (locally!)** to analyze the Olist Brazilian e-commerce dataset.

Instead of overengineering, the focus is on:
- ✅ Clean architecture  
- ✅ Reproducibility  
- ✅ Business-driven insights  
- ✅ Interview-ready explanations  

💡 *Think of this as a “mini data platform” you can confidently defend in front of senior engineers.*

---

## 🧱 Architecture

## 🧱 Architecture

```mermaid
flowchart LR
  A[Raw CSV Data] --> B[Python Ingestion]
  H[Public Holiday API] --> B
  B --> C[DuckDB Warehouse]
  C --> D[dbt Staging]
  D --> E[dbt Intermediate]
  E --> F[dbt Marts]
  F --> G[Analytics Outputs]
  P[Prefect Flow] --> B
  P --> D
  P --> G
