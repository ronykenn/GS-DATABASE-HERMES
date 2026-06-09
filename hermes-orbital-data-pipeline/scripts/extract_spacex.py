from __future__ import annotations

import json
from pathlib import Path
import os

import requests

from config import MOCK_DIR, RAW_DIR, configure_logging, ensure_directories


LOGGER = configure_logging("extract_spacex")
SPACEX_LAUNCHES_URL = "https://api.spacexdata.com/v4/launches"
OUTPUT_FILE = RAW_DIR / "spacex_launches.json"
FALLBACK_FILE = MOCK_DIR / "spacex_launches_fallback.json"


def extract_spacex_launches(output_file: Path = OUTPUT_FILE) -> str:
    ensure_directories()
    use_api = os.getenv("USE_SPACEX_API", "false").lower() in ("1", "true", "yes")
    if not use_api:
        LOGGER.info("USE_SPACEX_API disabled — usando fallback local %s", FALLBACK_FILE)
        if not FALLBACK_FILE.exists():
            raise FileNotFoundError(f"Fallback nao encontrado: {FALLBACK_FILE}")
        launches = json.loads(FALLBACK_FILE.read_text(encoding="utf-8"))
        source = "fallback"
    else:
        try:
            LOGGER.info("Consultando SpaceX API: %s", SPACEX_LAUNCHES_URL)
            # shorter timeout so task fails fast when API is unavailable
            response = requests.get(SPACEX_LAUNCHES_URL, timeout=10)
            response.raise_for_status()
            launches = response.json()
            if not isinstance(launches, list) or not launches:
                raise ValueError("Resposta da SpaceX API vazia ou invalida")
            source = "api"
        except Exception as exc:
            LOGGER.warning("Falha ao consultar SpaceX API. Usando fallback local: %s", exc)
            if not FALLBACK_FILE.exists():
                raise FileNotFoundError(f"Fallback nao encontrado: {FALLBACK_FILE}") from exc
            launches = json.loads(FALLBACK_FILE.read_text(encoding="utf-8"))
            source = "fallback"

    output_file.write_text(json.dumps(launches, ensure_ascii=True, indent=2), encoding="utf-8")
    LOGGER.info("SpaceX launches salvos em %s (%s, %s registros)", output_file, source, len(launches))
    return str(output_file)


if __name__ == "__main__":
    extract_spacex_launches()
