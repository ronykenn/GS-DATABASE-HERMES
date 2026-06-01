from __future__ import annotations

import json
from pathlib import Path

import requests

from config import MOCK_DIR, RAW_DIR, configure_logging, ensure_directories


LOGGER = configure_logging("extract_spacex")
SPACEX_LAUNCHES_URL = "https://api.spacexdata.com/v4/launches"
OUTPUT_FILE = RAW_DIR / "spacex_launches.json"
FALLBACK_FILE = MOCK_DIR / "spacex_launches_fallback.json"


def extract_spacex_launches(output_file: Path = OUTPUT_FILE) -> Path:
    ensure_directories()
    try:
        LOGGER.info("Consultando SpaceX API: %s", SPACEX_LAUNCHES_URL)
        response = requests.get(SPACEX_LAUNCHES_URL, timeout=20)
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
    return output_file


if __name__ == "__main__":
    extract_spacex_launches()
