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

```mermaid
flowchart LR
  A[Raw CSV Data] --> B[Python Ingestion]
  H[Public Holiday API] --> B
  B --> C[(DuckDB Warehouse)]
  C --> D[dbt Staging]
  D --> E[dbt Intermediate]
  E --> F[dbt Marts]
  F --> G[Analytics Outputs]
  P[Prefect Flow] --> B
  P --> D
  P --> G

## 🔑 Key Components
- DuckDB → Lightweight analytical warehouse
- dbt → Transformations + data modeling
- Prefect → Orchestration
- Docker → Reproducibility
- Python → Ingestion layer

## ⚙️ How to Run
## ▶️ Local Run
uv run python scripts/flow.py

## 🐳 Docker Run
docker compose up --build pipeline

## 🧠 Data Modeling Strategy

The warehouse follows a layered architecture:

Layer	Purpose
- raw	Source data ingestion
- staging	Clean + normalize
- intermediate	Business logic
- marts	Analytics-ready tables

## 📊 Entity Relationships
erDiagram
  CUSTOMERS ||--o{ ORDERS : places
  ORDERS ||--o{ ORDER_ITEMS : contains
  ORDERS ||--o{ PAYMENTS : paid_by
  ORDERS ||--o{ REVIEWS : reviewed_by
  PRODUCTS ||--o{ ORDER_ITEMS : purchased_as
  SELLERS ||--o{ ORDER_ITEMS : sells
  HOLIDAYS ||--o{ ORDERS : enriches

## 📈 Business Insights
💰 Revenue & Seasonality
- Strong growth in health_beauty and watches_gifts
- Some spikes detected using z-score anomaly detection
- Holidays alone don’t explain revenue spikes → promotions likely drivers

## 🔁 Customer Retention
- Repeat rate (90 days) is very low (~1–1.6%)
- Marketplace behavior → mostly one-time buyers
- Best-performing states:
  - ES
  - MT
  - SP
