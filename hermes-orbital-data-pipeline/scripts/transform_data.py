from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config import MOCK_DIR, PROCESSED_DIR, RAW_DIR, configure_logging, ensure_directories


LOGGER = configure_logging("transform_data")


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo obrigatorio nao encontrado: {path}")


def _ingestion_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def priority_level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def recommended_action(priority: str, object_type: str | None = None) -> str:
    if priority == "CRITICAL":
        return "IMMEDIATE_DEORBIT"
    if priority == "HIGH":
        return "SCHEDULE_CAPTURE"
    if priority == "MEDIUM":
        return "ORBITAL_TAXI" if object_type == "ACTIVE_SATELLITE" else "MONITOR"
    return "NO_ACTION"


def transform_spacex_data(
    input_file: Path = RAW_DIR / "spacex_launches.json",
    output_file: Path = PROCESSED_DIR / "spacex_launches.csv",
) -> Path:
    ensure_directories()
    _require_file(input_file)
    launches = json.loads(input_file.read_text(encoding="utf-8"))
    records = []
    for item in launches:
        launch_id = item.get("id")
        name = item.get("name")
        date_utc = item.get("date_utc")
        if not launch_id or not name or not date_utc:
            continue
        records.append(
            {
                "launch_id": launch_id,
                "mission_name": name,
                "flight_number": item.get("flight_number") or 0,
                "launch_date_utc": pd.to_datetime(date_utc, errors="coerce", utc=True),
                "success": int(bool(item.get("success"))) if item.get("success") is not None else 0,
                "rocket_id": item.get("rocket") or "",
                "launchpad_id": item.get("launchpad") or "",
                "payloads_count": len(item.get("payloads") or []),
                "details": (item.get("details") or "")[:1000],
                "data_source": "SPACEX_API",
                "ingestion_date": _ingestion_timestamp(),
            }
        )

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.dropna(subset=["launch_date_utc"]).drop_duplicates(subset=["launch_id"])
        df["launch_date_utc"] = df["launch_date_utc"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(output_file, index=False)
    LOGGER.info("SpaceX transformado em %s (%s registros)", output_file, len(df))
    return output_file


def transform_iss_data(
    input_file: Path = RAW_DIR / "iss_position.json",
    output_file: Path = PROCESSED_DIR / "iss_position.csv",
) -> Path:
    ensure_directories()
    _require_file(input_file)
    payload = json.loads(input_file.read_text(encoding="utf-8"))
    position = payload.get("iss_position", {})
    collected = datetime.fromtimestamp(int(payload.get("timestamp", 0)), tz=timezone.utc)
    df = pd.DataFrame(
        [
            {
                "position_id": f"ISS-{payload.get('timestamp', uuid.uuid4().hex)}",
                "latitude": position.get("latitude"),
                "longitude": position.get("longitude"),
                "timestamp_unix": payload.get("timestamp"),
                "collected_at": collected,
                "data_source": "OPEN_NOTIFY_API",
                "ingestion_date": _ingestion_timestamp(),
            }
        ]
    )
    for column in ("latitude", "longitude", "timestamp_unix"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude", "timestamp_unix"])
    df["collected_at"] = pd.to_datetime(df["collected_at"], utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(output_file, index=False)
    LOGGER.info("ISS transformado em %s (%s registros)", output_file, len(df))
    return output_file


def transform_telemetry_data(
    input_file: Path = RAW_DIR / "hermes_orbital_telemetry.csv",
    output_file: Path = PROCESSED_DIR / "orbital_objects.csv",
) -> Path:
    ensure_directories()
    if not input_file.exists():
        input_file = MOCK_DIR / "hermes_orbital_telemetry.csv"
    _require_file(input_file)
    df = pd.read_csv(input_file)
    required = ["object_id", "object_name", "object_type", "orbit_zone", "collision_risk_score", "observed_at"]
    df = df.dropna(subset=[column for column in required if column in df.columns])

    numeric_columns = ["altitude_km", "velocity_kmh", "estimated_mass_kg", "collision_risk_score", "fuel_required_kg"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["observed_at"] = pd.to_datetime(df["observed_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["observed_at"]).drop_duplicates(subset=["object_id"])
    df["priority_level"] = df["collision_risk_score"].apply(priority_level)
    df["recommended_action"] = df.apply(
        lambda row: recommended_action(row["priority_level"], row.get("object_type")),
        axis=1,
    )
    df["operational_status"] = df["operational_status"].fillna("UNKNOWN")
    df["data_source"] = df.get("data_source", "HERMES_MOCK_TELEMETRY")
    df["ingestion_date"] = _ingestion_timestamp()
    df["observed_at"] = df["observed_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

    ordered_columns = [
        "object_id",
        "object_name",
        "object_type",
        "orbit_zone",
        "altitude_km",
        "velocity_kmh",
        "estimated_mass_kg",
        "collision_risk_score",
        "operational_status",
        "priority_level",
        "recommended_action",
        "fuel_required_kg",
        "observed_at",
        "data_source",
        "ingestion_date",
    ]
    df[ordered_columns].to_csv(output_file, index=False)
    LOGGER.info("Telemetria transformada em %s (%s registros)", output_file, len(df))
    return output_file


def generate_mission_analytics(
    input_file: Path = PROCESSED_DIR / "orbital_objects.csv",
    output_file: Path = PROCESSED_DIR / "mission_analytics.csv",
) -> Path:
    _require_file(input_file)
    df = pd.read_csv(input_file)
    generated_at = _ingestion_timestamp()
    reference_date = pd.Timestamp.utcnow().strftime("%Y-%m-%d")
    analytics = pd.DataFrame(
        [
            {
                "analytic_id": f"ANL-{uuid.uuid4().hex[:12].upper()}",
                "reference_date": reference_date,
                "total_objects": int(len(df)),
                "high_risk_objects": int((df["collision_risk_score"] >= 60).sum()),
                "avg_collision_risk": round(float(df["collision_risk_score"].mean()), 2) if not df.empty else 0,
                "total_fuel_required_kg": round(float(df["fuel_required_kg"].sum()), 2) if not df.empty else 0,
                "generated_at": generated_at,
            }
        ]
    )
    analytics.to_csv(output_file, index=False)
    LOGGER.info("Analytics gerado em %s", output_file)
    return output_file


if __name__ == "__main__":
    transform_spacex_data()
    transform_iss_data()
    transform_telemetry_data()
    generate_mission_analytics()
