"""Idempotent ingestion for the Lance Data Olist analytics project."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import duckdb
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "data" / "warehouse" / "olist.duckdb"
HOLIDAY_JSON = RAW_DIR / "reference" / "br_public_holidays_2016_2018.json"

CSV_TABLES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

FALLBACK_HOLIDAYS = {
    "2016": [
        ("2016-01-01", "New Year's Day"), ("2016-04-21", "Tiradentes"),
        ("2016-05-01", "Labour Day"), ("2016-09-07", "Independence Day"),
        ("2016-10-12", "Our Lady of Aparecida"), ("2016-11-02", "All Souls' Day"),
        ("2016-11-15", "Republic Proclamation Day"), ("2016-12-25", "Christmas Day"),
    ],
    "2017": [
        ("2017-01-01", "New Year's Day"), ("2017-04-21", "Tiradentes"),
        ("2017-05-01", "Labour Day"), ("2017-09-07", "Independence Day"),
        ("2017-10-12", "Our Lady of Aparecida"), ("2017-11-02", "All Souls' Day"),
        ("2017-11-15", "Republic Proclamation Day"), ("2017-12-25", "Christmas Day"),
    ],
    "2018": [
        ("2018-01-01", "New Year's Day"), ("2018-04-21", "Tiradentes"),
        ("2018-05-01", "Labour Day"), ("2018-09-07", "Independence Day"),
        ("2018-10-12", "Our Lady of Aparecida"), ("2018-11-02", "All Souls' Day"),
        ("2018-11-15", "Republic Proclamation Day"), ("2018-12-25", "Christmas Day"),
    ],
}


def ensure_dirs() -> None:
    for path in [RAW_DIR, RAW_DIR / "reference", WAREHOUSE.parent]:
        path.mkdir(parents=True, exist_ok=True)


def locate_csv(filename: str) -> Path:
    candidates = [RAW_DIR / filename, RAW_DIR / "olist" / filename]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Missing {filename}. Download with: uv run kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip")


def fetch_holidays(years: Iterable[int] = range(2016, 2019)) -> list[dict]:
    rows: list[dict] = []
    for year in years:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/BR"
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            source = "nager.date"
        except Exception:
            data = [
                {"date": date, "localName": name, "name": name, "types": ["Public"]}
                for date, name in FALLBACK_HOLIDAYS[str(year)]
            ]
            source = "fallback_static"
        for item in data:
            rows.append(
                {
                    "holiday_date": item["date"],
                    "local_name": item.get("localName"),
                    "english_name": item.get("name"),
                    "country_code": item.get("countryCode", "BR"),
                    "holiday_types": ",".join(item.get("types") or []),
                    "source": source,
                }
            )
    HOLIDAY_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


def load() -> None:
    ensure_dirs()
    con = duckdb.connect(str(WAREHOUSE))
    con.execute("create schema if not exists raw")
    con.execute("create schema if not exists metadata")

    manifest: list[tuple[str, str, int]] = []
    for table, filename in CSV_TABLES.items():
        csv_path = locate_csv(filename)
        con.execute(f"drop table if exists raw.{table}")
        con.execute(
            f"""
            create table raw.{table} as
            select * from read_csv_auto(?, header=true, sample_size=-1, ignore_errors=false)
            """,
            [str(csv_path)],
        )
        count = con.execute(f"select count(*) from raw.{table}").fetchone()[0]
        manifest.append((table, filename, count))

    holidays = fetch_holidays()
    con.execute("drop table if exists raw.public_holidays_br")
    con.execute(
        """
        create table raw.public_holidays_br (
            holiday_date date,
            local_name varchar,
            english_name varchar,
            country_code varchar,
            holiday_types varchar,
            source varchar
        )
        """
    )
    con.executemany(
        "insert into raw.public_holidays_br values (?, ?, ?, ?, ?, ?)",
        [(r["holiday_date"], r["local_name"], r["english_name"], r["country_code"], r["holiday_types"], r["source"]) for r in holidays],
    )
    manifest.append(("public_holidays_br", str(HOLIDAY_JSON.relative_to(ROOT)), len(holidays)))

    con.execute("drop table if exists metadata.ingestion_manifest")
    con.execute("create table metadata.ingestion_manifest (table_name varchar, source_file varchar, row_count bigint, loaded_at timestamp)")
    con.executemany("insert into metadata.ingestion_manifest values (?, ?, ?, current_timestamp)", manifest)
    con.close()
    print(f"Loaded {len(manifest)} raw tables into {WAREHOUSE}")


if __name__ == "__main__":
    load()
