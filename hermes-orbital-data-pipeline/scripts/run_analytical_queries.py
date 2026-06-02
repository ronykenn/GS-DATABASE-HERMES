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
            output_file = RESULTS_DIR / f"sqlite_query_{index:02d}.csv"
            df.to_csv(output_file, index=False)
            LOGGER.info("Consulta %s salva em %s", index, output_file)
    return RESULTS_DIR


def _connect_oracle():
    import oracledb

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    host = os.getenv("ORACLE_HOST", "oracle.fiap.com.br")
    port = os.getenv("ORACLE_PORT", "1521")
    sid = os.getenv("ORACLE_SID", "ORCL")
    if not user or not password:
        raise EnvironmentError("Defina ORACLE_USER e ORACLE_PASSWORD para consultar Oracle")
    dsn = oracledb.makedsn(host, int(port), sid=sid)
    return oracledb.connect(user=user, password=password, dsn=dsn)


def run_oracle_queries() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    queries = _split_queries((SQL_DIR / "03_analytical_queries_oracle.sql").read_text(encoding="utf-8"))
    with _connect_oracle() as connection:
        with connection.cursor() as cursor:
            for index, query in enumerate(queries, start=1):
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                output_file = RESULTS_DIR / f"oracle_query_{index:02d}.csv"
                df.to_csv(output_file, index=False)
                LOGGER.info("Consulta Oracle %s salva em %s", index, output_file)
    return RESULTS_DIR


def run_analytical_queries() -> Path:
    target = os.getenv("HERMES_DB_TARGET", "sqlite").lower()
    if target == "oracle":
        return run_oracle_queries()
    return run_sqlite_queries()


if __name__ == "__main__":
    run_analytical_queries()
