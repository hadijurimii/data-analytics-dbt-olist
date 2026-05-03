"""Prefect orchestration: ingest -> dbt run -> dbt test -> export analysis."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from prefect import flow, task

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


@task
def ingest() -> None:
    run_cmd([sys.executable, "scripts/ingest.py"])


@task
def dbt_run() -> None:
    run_cmd(["dbt", "run", "--profiles-dir", "."])


@task
def dbt_test() -> None:
    run_cmd(["dbt", "test", "--profiles-dir", "."])


@task
def export_analysis() -> None:
    run_cmd([sys.executable, "scripts/export_analysis.py"])


@flow(name="lance-data-local-analytics")
def pipeline() -> None:
    ingest()
    dbt_run()
    dbt_test()
    export_analysis()


if __name__ == "__main__":
    pipeline()
