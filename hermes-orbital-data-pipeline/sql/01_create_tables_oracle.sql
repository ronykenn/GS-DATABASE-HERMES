CREATE TABLE HERMES_SPACEX_LAUNCHES (
    launch_id VARCHAR2(100) PRIMARY KEY,
    mission_name VARCHAR2(255),
    flight_number NUMBER,
    launch_date_utc TIMESTAMP,
    success NUMBER(1),
    rocket_id VARCHAR2(100),
    launchpad_id VARCHAR2(100),
    payloads_count NUMBER,
    details VARCHAR2(1000),
    data_source VARCHAR2(50),
    ingestion_date TIMESTAMP
);

CREATE TABLE HERMES_ISS_POSITION (
    position_id VARCHAR2(100) PRIMARY KEY,
    latitude NUMBER(10,6),
    longitude NUMBER(10,6),
    timestamp_unix NUMBER,
    collected_at TIMESTAMP,
    data_source VARCHAR2(50),
    ingestion_date TIMESTAMP
);

CREATE TABLE HERMES_ORBITAL_OBJECTS (
    object_id VARCHAR2(100) PRIMARY KEY,
    object_name VARCHAR2(255),
    object_type VARCHAR2(50),
    orbit_zone VARCHAR2(50),
    altitude_km NUMBER(10,2),
    velocity_kmh NUMBER(10,2),
    estimated_mass_kg NUMBER(10,2),
    collision_risk_score NUMBER(5,2),
    operational_status VARCHAR2(50),
    priority_level VARCHAR2(20),
    recommended_action VARCHAR2(100),
    fuel_required_kg NUMBER(10,2),
    observed_at TIMESTAMP,
    data_source VARCHAR2(50),
    ingestion_date TIMESTAMP
);

CREATE TABLE HERMES_MISSION_ANALYTICS (
    analytic_id VARCHAR2(100) PRIMARY KEY,
    reference_date DATE,
    total_objects NUMBER,
    high_risk_objects NUMBER,
    avg_collision_risk NUMBER(5,2),
    total_fuel_required_kg NUMBER(10,2),
    generated_at TIMESTAMP
);
