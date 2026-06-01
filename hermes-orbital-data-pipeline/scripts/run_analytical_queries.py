from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd

from config import PROJECT_ROOT, SQL_DIR, configure_logging


LOGGER = configure_logging("run_analytical_queries")
RESULTS_DIR = PROJECT_ROOT / "data" / "processed" / "query_results"


def _split_queries(sql_text: str) -> list[str]:
    cleaned_lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        cleaned_lines.append(line)
    return [query.strip() for query in "\n".join(cleaned_lines).split(";") if query.strip()]


def run_sqlite_queries(db_path: Path = PROJECT_ROOT / "hermes_orbital.db") -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    queries = _split_queries((SQL_DIR / "04_analytical_queries_sqlite.sql").read_text(encoding="utf-8"))
    with sqlite3.connect(db_path) as connection:
        for index, query in enumerate(queries, start=1):
            df = pd.read_sql_query(query, connection)
            output_file = RESULTS_DIR / f"query_{index:02d}.csv"
            df.to_csv(output_file, index=False)
            LOGGER.info("Consulta %s salva em %s", index, output_file)
    return RESULTS_DIR


def run_analytical_queries() -> Path:
    target = os.getenv("HERMES_DB_TARGET", "sqlite").lower()
    if target == "oracle":
        LOGGER.info("Para Oracle, execute as consultas do arquivo %s", SQL_DIR / "03_analytical_queries_oracle.sql")
    return run_sqlite_queries()


if __name__ == "__main__":
    run_analytical_queries()
