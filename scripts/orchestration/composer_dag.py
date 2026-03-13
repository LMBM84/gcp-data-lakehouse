"""
Cloud Composer (Airflow) DAG: CO2 Emissions Data Pipeline
Orchestrates the full pipeline: Ingest → Process → Load → Notify
Schedule: Daily at 02:00 UTC
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.functions import CloudFunctionInvokeFunctionOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago

# ── Config ────────────────────────────────────────────────────────────────────
GCP_PROJECT_ID       = "your-project-id"
GCP_REGION           = "us-central1"
GCS_RAW_BUCKET       = "your-project-raw"
GCS_PROCESSED_BUCKET = "your-project-processed"
BQ_DATASET           = "co2_emissions"
DATAPROC_CLUSTER     = "co2-processing-cluster"
CLOUD_FUNCTION_NAME  = "ingest_co2_data"
PYSPARK_JOB_FILE     = f"gs://{GCS_RAW_BUCKET}/scripts/pyspark_transform.py"

CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-2",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 50},
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-2",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 50},
    },
    "software_config": {"image_version": "2.1-debian11"},
}

PYSPARK_JOB = {
    "reference": {"project_id": GCP_PROJECT_ID},
    "placement": {"cluster_name": DATAPROC_CLUSTER},
    "pyspark_job": {
        "main_python_file_uri": PYSPARK_JOB_FILE,
        "properties": {
            "spark.executor.memory": "2g",
            "spark.driver.memory": "1g",
        },
    },
}

BQ_LOAD_QUERY = f"""
CREATE OR REPLACE TABLE `{GCP_PROJECT_ID}.{BQ_DATASET}.vehicles_processed`
PARTITION BY RANGE_BUCKET(co2_emissions_g_km, GENERATE_ARRAY(0, 600, 50))
CLUSTER BY make, fuel_type
AS
SELECT *, CURRENT_TIMESTAMP() AS ingested_at
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.vehicles_external`
"""

# ── Default args ──────────────────────────────────────────────────────────────
default_args = {
    "owner": "LMBM84",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": days_ago(1),
}

# ── DAG definition ────────────────────────────────────────────────────────────
with DAG(
    dag_id="co2_lakehouse_pipeline",
    default_args=default_args,
    description="End-to-end CO2 emissions data lakehouse pipeline",
    schedule_interval="0 2 * * *",  # Daily at 02:00 UTC
    catchup=False,
    max_active_runs=1,
    tags=["co2", "gcp", "lakehouse", "portfolio"],
) as dag:

    # Task 1: Trigger Cloud Function to ingest from Kaggle → GCS
    ingest_data = CloudFunctionInvokeFunctionOperator(
        task_id="ingest_kaggle_to_gcs",
        function_id=CLOUD_FUNCTION_NAME,
        location=GCP_REGION,
        project_id=GCP_PROJECT_ID,
        input_data={},
    )

    # Task 2: Create Dataproc cluster for PySpark processing
    create_cluster = DataprocCreateClusterOperator(
        task_id="create_dataproc_cluster",
        project_id=GCP_PROJECT_ID,
        cluster_config=CLUSTER_CONFIG,
        region=GCP_REGION,
        cluster_name=DATAPROC_CLUSTER,
    )

    # Task 3: Submit PySpark ETL job
    run_pyspark = DataprocSubmitJobOperator(
        task_id="run_pyspark_etl",
        job=PYSPARK_JOB,
        region=GCP_REGION,
        project_id=GCP_PROJECT_ID,
    )

    # Task 4: Delete cluster (save costs immediately after job)
    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_dataproc_cluster",
        project_id=GCP_PROJECT_ID,
        cluster_name=DATAPROC_CLUSTER,
        region=GCP_REGION,
        trigger_rule="all_done",  # Always delete even if job fails
    )

    # Task 5: Load processed data into BigQuery
    load_to_bigquery = BigQueryInsertJobOperator(
        task_id="load_to_bigquery",
        configuration={
            "query": {
                "query": BQ_LOAD_QUERY,
                "useLegacySql": False,
            }
        },
        project_id=GCP_PROJECT_ID,
    )

    # ── Pipeline DAG ──────────────────────────────────────────
    ingest_data >> create_cluster >> run_pyspark >> delete_cluster >> load_to_bigquery
