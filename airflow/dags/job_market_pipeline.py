from datetime import datetime, timezone

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"

with DAG(
    dag_id="job_market_intelligence_pipeline",
    description="Process job data and load it into the PostgreSQL warehouse",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    tags=["data-engineering", "postgres", "s3"],
) as dag:

    process_jobs = BashOperator(
        task_id="process_jobs",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python process_jobs.py"
        ),
    )

    load_warehouse = BashOperator(
        task_id="load_warehouse",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python load_warehouse.py"
        ),
    )

    process_jobs >> load_warehouse