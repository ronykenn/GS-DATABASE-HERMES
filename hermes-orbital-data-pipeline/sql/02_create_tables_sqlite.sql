CREATE TABLE IF NOT EXISTS HERMES_SPACEX_LAUNCHES (
    launch_id TEXT PRIMARY KEY,
    mission_name TEXT,
    flight_number INTEGER,
    launch_date_utc TEXT,
    success INTEGER,
    rocket_id TEXT,
    launchpad_id TEXT,
    payloads_count INTEGER,
    details TEXT,
    data_source TEXT,
    ingestion_date TEXT
);

CREATE TABLE IF NOT EXISTS HERMES_ISS_POSITION (
    position_id TEXT PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    timestamp_unix INTEGER,
    collected_at TEXT,
    data_source TEXT,
    ingestion_date TEXT
);

CREATE TABLE IF NOT EXISTS HERMES_ORBITAL_OBJECTS (
    object_id TEXT PRIMARY KEY,
    object_name TEXT,
    object_type TEXT,
    orbit_zone TEXT,
    altitude_km REAL,
    velocity_kmh REAL,
    estimated_mass_kg REAL,
    collision_risk_score REAL,
    operational_status TEXT,
    priority_level TEXT,
    recommended_action TEXT,
    fuel_required_kg REAL,
    observed_at TEXT,
    data_source TEXT,
    ingestion_date TEXT
);

CREATE TABLE IF NOT EXISTS HERMES_MISSION_ANALYTICS (
    analytic_id TEXT PRIMARY KEY,
    reference_date TEXT,
    total_objects INTEGER,
    high_risk_objects INTEGER,
    avg_collision_risk REAL,
    total_fuel_required_kg REAL,
    generated_at TEXT
);
