from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


LOCAL_PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKER_PROJECT_ROOT = Path("/opt/airflow/hermes-orbital-data-pipeline")
PROJECT_ROOT = DOCKER_PROJECT_ROOT if DOCKER_PROJECT_ROOT.exists() else LOCAL_PROJECT_ROOT
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from config import ensure_directories
from extract_iss import extract_iss_position
from extract_spacex import extract_spacex_launches
from generate_mock_telemetry import generate_mock_telemetry
from load_database import load_to_database
from run_analytical_queries import run_analytical_queries
from transform_data import transform_iss_data, transform_spacex_data, transform_telemetry_data


default_args = {
    "owner": "Projeto Hermes",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="hermes_orbital_pipeline",
    description="Pipeline de dados orbital do Projeto Hermes para FIAP GS 2026",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["fiap", "hermes", "orbital", "space"],
) as dag:
    create_directories = PythonOperator(task_id="create_directories", python_callable=ensure_directories)

    extract_spacex_launches_task = PythonOperator(
        task_id="extract_spacex_launches",
        python_callable=extract_spacex_launches,
        execution_timeout=timedelta(seconds=30),
    )
    extract_iss_position_task = PythonOperator(
        task_id="extract_iss_position",
        python_callable=extract_iss_position,
    )
    generate_mock_telemetry_task = PythonOperator(
        task_id="generate_mock_telemetry",
        python_callable=generate_mock_telemetry,
    )

    transform_spacex_data_task = PythonOperator(
        task_id="transform_spacex_data",
        python_callable=transform_spacex_data,
    )
    transform_iss_data_task = PythonOperator(
        task_id="transform_iss_data",
        python_callable=transform_iss_data,
    )
    transform_telemetry_data_task = PythonOperator(
        task_id="transform_telemetry_data",
        python_callable=transform_telemetry_data,
    )

    load_to_database_task = PythonOperator(task_id="load_to_database", python_callable=load_to_database)
    run_analytical_queries_task = PythonOperator(
        task_id="run_analytical_queries",
        python_callable=run_analytical_queries,
    )

    create_directories >> [extract_spacex_launches_task, extract_iss_position_task, generate_mock_telemetry_task]
    extract_spacex_launches_task >> transform_spacex_data_task
    extract_iss_position_task >> transform_iss_data_task
    generate_mock_telemetry_task >> transform_telemetry_data_task
    [transform_spacex_data_task, transform_iss_data_task, transform_telemetry_data_task] >> load_to_database_task
    load_to_database_task >> run_analytical_queries_task
