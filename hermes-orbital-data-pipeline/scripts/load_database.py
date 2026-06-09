from __future__ import annotations

import os

from config import configure_logging
from load_oracle import load_oracle
from load_sqlite import load_sqlite


LOGGER = configure_logging("load_database")


def load_to_database() -> str:
    target = os.getenv("HERMES_DB_TARGET", "sqlite").lower()
    if target == "oracle":
        load_oracle()
        return "oracle"
    load_sqlite()
    return "sqlite"


if __name__ == "__main__":
    load_to_database()
