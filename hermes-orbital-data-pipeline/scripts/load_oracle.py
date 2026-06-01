from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from config import PROCESSED_DIR, SQL_DIR, configure_logging
from transform_data import generate_mission_analytics


LOGGER = configure_logging("load_oracle")

TABLE_FILES = {
    "HERMES_SPACEX_LAUNCHES": PROCESSED_DIR / "spacex_launches.csv",
    "HERMES_ISS_POSITION": PROCESSED_DIR / "iss_position.csv",
    "HERMES_ORBITAL_OBJECTS": PROCESSED_DIR / "orbital_objects.csv",
    "HERMES_MISSION_ANALYTICS": PROCESSED_DIR / "mission_analytics.csv",
}


def _connect():
    import oracledb

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    host = os.getenv("ORACLE_HOST", "oracle.fiap.com.br")
    port = os.getenv("ORACLE_PORT", "1521")
    sid = os.getenv("ORACLE_SID", "ORCL")
    if not user or not password:
        raise EnvironmentError("Defina ORACLE_USER e ORACLE_PASSWORD para usar Oracle")
    dsn = oracledb.makedsn(host, int(port), sid=sid)
    return oracledb.connect(user=user, password=password, dsn=dsn)


def _run_schema(cursor) -> None:
    statements = (SQL_DIR / "01_create_tables_oracle.sql").read_text(encoding="utf-8").split(";")
    for statement in statements:
        sql = statement.strip()
        if sql:
            try:
                cursor.execute(sql)
            except Exception as exc:
                LOGGER.info("Schema Oracle: instrucao ignorada ou ja existente: %s", exc)


def _insert_dataframe(cursor, table_name: str, df: pd.DataFrame) -> None:
    if df.empty:
        return
    columns = list(df.columns)
    placeholders = ", ".join([f":{index + 1}" for index in range(len(columns))])
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.executemany(sql, [tuple(None if pd.isna(value) else value for value in row) for row in df.to_numpy()])


def load_oracle() -> None:
    generate_mission_analytics()
    with _connect() as connection:
        cursor = connection.cursor()
        _run_schema(cursor)
        for table_name, csv_file in TABLE_FILES.items():
            if not Path(csv_file).exists():
                LOGGER.warning("Arquivo processado ausente, carga ignorada: %s", csv_file)
                continue
            df = pd.read_csv(csv_file)
            cursor.execute(f"DELETE FROM {table_name}")
            _insert_dataframe(cursor, table_name, df)
            LOGGER.info("%s registros carregados em %s", len(df), table_name)
        connection.commit()
    LOGGER.info("Carga Oracle finalizada")


if __name__ == "__main__":
    load_oracle()
