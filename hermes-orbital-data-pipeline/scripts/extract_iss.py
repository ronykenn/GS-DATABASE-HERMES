from __future__ import annotations

import json
from pathlib import Path

import requests

from config import MOCK_DIR, RAW_DIR, configure_logging, ensure_directories


LOGGER = configure_logging("extract_iss")
ISS_NOW_URL = "http://api.open-notify.org/iss-now.json"
OUTPUT_FILE = RAW_DIR / "iss_position.json"
FALLBACK_FILE = MOCK_DIR / "iss_position_fallback.json"


def extract_iss_position(output_file: Path = OUTPUT_FILE) -> Path:
    ensure_directories()
    try:
        LOGGER.info("Consultando Open Notify API: %s", ISS_NOW_URL)
        response = requests.get(ISS_NOW_URL, timeout=15)
        response.raise_for_status()
        payload = response.json()
        if payload.get("message") != "success" or "iss_position" not in payload:
            raise ValueError("Resposta da Open Notify API invalida")
        source = "api"
    except Exception as exc:
        LOGGER.warning("Falha ao consultar Open Notify API. Usando fallback local: %s", exc)
        if not FALLBACK_FILE.exists():
            raise FileNotFoundError(f"Fallback nao encontrado: {FALLBACK_FILE}") from exc
        payload = json.loads(FALLBACK_FILE.read_text(encoding="utf-8"))
        source = "fallback"

    output_file.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    LOGGER.info("Posicao ISS salva em %s (%s)", output_file, source)
    return output_file


if __name__ == "__main__":
    extract_iss_position()
