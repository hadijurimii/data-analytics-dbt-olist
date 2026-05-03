from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_files_exist():
    required = [
        "scripts/ingest.py",
        "scripts/flow.py",
        "scripts/export_analysis.py",
        "dbt_project.yml",
        "profiles.yml",
        "docker-compose.yml",
        "models/staging/stg_orders.sql",
        "models/intermediate/int_order_enriched.sql",
        "models/marts/mart_monthly_category_gmv.sql",
        "summary.md",
        "report.md",
        "progress.md",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing


def test_raw_data_is_gitignored():
    gitignore = (ROOT / ".gitignore").read_text()
    assert "data/raw/*.csv" in gitignore
    assert "data/warehouse/*.duckdb" in gitignore
