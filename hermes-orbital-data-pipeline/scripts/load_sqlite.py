from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from config import PROCESSED_DIR, PROJECT_ROOT, SQL_DIR, configure_logging
from transform_data import generate_mission_analytics


LOGGER = configure_logging("load_sqlite")
SQLITE_DB = PROJECT_ROOT / "hermes_orbital.db"

TABLE_FILES = {
    "HERMES_SPACEX_LAUNCHES": PROCESSED_DIR / "spacex_launches.csv",
    "HERMES_ISS_POSITION": PROCESSED_DIR / "iss_position.csv",
    "HERMES_ORBITAL_OBJECTS": PROCESSED_DIR / "orbital_objects.csv",
    "HERMES_MISSION_ANALYTICS": PROCESSED_DIR / "mission_analytics.csv",
}


def load_sqlite(db_path: Path = SQLITE_DB) -> Path:
    generate_mission_analytics()
    schema = (SQL_DIR / "02_create_tables_sqlite.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as connection:
        connection.executescript(schema)
        for table_name, csv_file in TABLE_FILES.items():
            if not csv_file.exists():
                LOGGER.warning("Arquivo processado ausente, carga ignorada: %s", csv_file)
                continue
            df = pd.read_csv(csv_file)
            connection.execute(f"DELETE FROM {table_name}")
            df.to_sql(table_name, connection, if_exists="append", index=False)
            LOGGER.info("%s registros carregados em %s", len(df), table_name)
    LOGGER.info("Banco SQLite atualizado em %s", db_path)
    return db_path


if __name__ == "__main__":
    load_sqlite()
