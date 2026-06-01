from __future__ import annotations

import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import MOCK_DIR, RAW_DIR, configure_logging, ensure_directories


LOGGER = configure_logging("generate_mock_telemetry")
OUTPUT_FILE = RAW_DIR / "hermes_orbital_telemetry.csv"
MOCK_OUTPUT_FILE = MOCK_DIR / "hermes_orbital_telemetry.csv"

OBJECT_TYPES = ["DEBRIS", "INACTIVE_SATELLITE", "ACTIVE_SATELLITE", "ROCKET_BODY", "SERVICE_MODULE"]
ORBIT_ZONES = ["LEO", "LEO", "LEO", "LEO", "MEO", "MEO", "GEO"]
STATUSES = ["ACTIVE", "INACTIVE", "UNKNOWN", "CRITICAL"]


def _risk_for_object(object_type: str, orbit_zone: str) -> float:
    base = {
        "DEBRIS": random.uniform(58, 96),
        "INACTIVE_SATELLITE": random.uniform(45, 88),
        "ROCKET_BODY": random.uniform(40, 84),
        "ACTIVE_SATELLITE": random.uniform(12, 62),
        "SERVICE_MODULE": random.uniform(18, 70),
    }[object_type]
    if orbit_zone == "LEO":
        base += random.uniform(3, 12)
    return round(min(base, 99.5), 2)


def _fuel_required(risk: float, estimated_mass_kg: float, object_type: str) -> float:
    multiplier = 0.018 if object_type in {"DEBRIS", "ROCKET_BODY"} else 0.011
    return round((risk / 100) * estimated_mass_kg * multiplier + random.uniform(2, 30), 2)


def generate_mock_telemetry(records: int = 120, output_file: Path = OUTPUT_FILE) -> Path:
    ensure_directories()
    random.seed(2026)
    rows = []
    now = datetime.now(timezone.utc)

    for index in range(records):
        object_type = random.choices(OBJECT_TYPES, weights=[34, 22, 24, 14, 6], k=1)[0]
        orbit_zone = random.choice(ORBIT_ZONES)
        altitude_range = {"LEO": (350, 2000), "MEO": (2000, 20000), "GEO": (35700, 35900)}[orbit_zone]
        altitude = round(random.uniform(*altitude_range), 2)
        velocity = round(random.uniform(10500, 28000) if orbit_zone != "GEO" else random.uniform(10500, 11200), 2)
        mass = round(random.uniform(20, 8500), 2)
        risk = _risk_for_object(object_type, orbit_zone)
        status = "CRITICAL" if risk >= 80 else random.choice(STATUSES)
        rows.append(
            {
                "object_id": f"HER-{uuid.uuid4().hex[:12].upper()}",
                "object_name": f"Hermes {object_type.replace('_', ' ').title()} {index + 1:03d}",
                "object_type": object_type,
                "orbit_zone": orbit_zone,
                "altitude_km": altitude,
                "velocity_kmh": velocity,
                "estimated_mass_kg": mass,
                "collision_risk_score": risk,
                "operational_status": status,
                "fuel_required_kg": _fuel_required(risk, mass, object_type),
                "observed_at": (now - timedelta(minutes=random.randint(0, 4320))).isoformat(),
                "data_source": "HERMES_MOCK_TELEMETRY",
            }
        )

    for target in (output_file, MOCK_OUTPUT_FILE):
        with target.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        LOGGER.info("Telemetria mockada salva em %s (%s registros)", target, len(rows))

    return output_file


if __name__ == "__main__":
    generate_mock_telemetry()
