# Suggested repo structure

This is a suggestion, not a requirement. You are free to organise your fork however makes sense to you. Your interviewers will adapt to whatever structure you choose — the goal here is to give you one reasonable starting point if you want it.

---

## Sample layout

```
your-fork/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── ingestion/              # dlt / Airbyte / custom ingestion code
├── transform/              # dbt project
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/
│   ├── macros/
│   └── dbt_project.yml
├── orchestration/          # Airflow / Prefect / Dagster DAGs
├── analysis/               # SQL queries + notebooks answering business questions
└── docs/
    ├── erd.md              # Mermaid ERD of dimensional model
    └── architecture.md     # Mermaid architecture diagram showing data flow
```

---

## Why each folder exists

**`ingestion/`**
Contains all code responsible for moving raw data from its source into your warehouse or storage layer. Keeping this separate from transformation code makes it easy to swap out ingestion tools (e.g., replace a custom script with `dlt`) without touching anything downstream.

**`transform/`**
Houses your `dbt` project (or equivalent). Staging, intermediate, and mart layers each serve a distinct purpose:

- `staging/` — one-to-one with source tables; light cleaning only, no business logic.
- `intermediate/` — joins and reshaping that serve multiple downstream models.
- `marts/` — business-facing fact and dimension tables; the output of your dimensional model.

Separating layers makes lineage clear and limits the blast radius of changes.

**`orchestration/`**
DAGs, flows, or job definitions that schedule and sequence your pipeline. Isolating orchestration from transformation keeps your `dbt` project portable — it can still be run with `dbt run` locally without any orchestrator present.

**`analysis/`**
SQL queries and notebooks that answer the business questions in `BUSINESS_QUESTIONS.md`. This folder lives outside `transform/` deliberately: answers to business questions should be traceable back to those questions and kept separate from the transformation pipeline, so reviewers can evaluate analytical thinking independently of engineering work.

**`docs/`**
Diagrams and written explanations of your design decisions. This is where your ERD and architecture diagram live.

---

## A note on diagrams

Commit diagrams as text — [Mermaid](https://mermaid.js.org/) is a good default because GitHub renders it natively in Markdown files. Text-based diagrams can be code-reviewed meaningfully, diffed, and updated without binary exports. If you prefer a different text format (e.g., PlantUML, D2), that is fine too.

---

## Closing note

This is guidance, not a rubric. There are no marks for folder names. Good structure simply helps your interviewers navigate your work quickly, which gives them more time to focus on the quality of what you have built.
