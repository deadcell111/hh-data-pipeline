import logging
import subprocess
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT_DIR = "/opt/airflow/project"
DBT_PROJECT_DIR = "/opt/airflow/dbt_project"
DBT_BIN = "/home/airflow/dbt_venv/bin/dbt"

log = logging.getLogger(__name__)


def alert_on_failure(context):
    ti = context["task_instance"]
    log.error(
        "Task failed: dag=%s task=%s run_id=%s",
        ti.dag_id, ti.task_id, context["run_id"],
    )


default_args = {
    "owner": "talgat",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": alert_on_failure,
}


def extract_hh_vacancies():
    subprocess.run(["python3", "fetch.py"], cwd=PROJECT_DIR, check=True)


def load_raw_to_postgres():
    subprocess.run(["python3", "load_raw.py"], cwd=PROJECT_DIR, check=True)


with DAG(
    dag_id="hh_pipeline",
    description="Fetch HH.ru vacancies, load raw, run dbt staging + marts",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["hh", "dbt"],
) as dag:

    extract = PythonOperator(
        task_id="extract_hh_vacancies",
        python_callable=extract_hh_vacancies,
    )

    load_raw = PythonOperator(
        task_id="load_raw_to_postgres",
        python_callable=load_raw_to_postgres,
    )

    run_dbt_staging = BashOperator(
        task_id="run_dbt_staging",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} run --select staging",
    )

    run_dbt_marts = BashOperator(
        task_id="run_dbt_marts",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} run --select marts",
    )

    extract >> load_raw >> run_dbt_staging >> run_dbt_marts
