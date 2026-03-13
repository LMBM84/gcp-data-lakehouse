# Part 4 — Orchestration Layer with Cloud Composer

## Overview

Google Cloud Composer (managed Apache Airflow) orchestrates the entire pipeline automatically on a daily schedule.

---

## Step 1: Create a Composer Environment

```bash
gcloud composer environments create co2-pipeline-env \
  --location=${REGION} \
  --image-version=composer-2.6.6-airflow-2.7.3 \
  --node-count=3 \
  --machine-type=n1-standard-2 \
  --disk-size=30GB \
  --project=${PROJECT_ID}
```

> ⚠️ This takes 15–20 minutes to provision.

---

## Step 2: Upload the DAG

```bash
# Get the Composer GCS bucket
COMPOSER_BUCKET=$(gcloud composer environments describe co2-pipeline-env \
  --location=${REGION} \
  --format="value(config.dagGcsPrefix)")

# Upload the DAG file
gcloud storage cp scripts/orchestration/composer_dag.py \
  ${COMPOSER_BUCKET}/
```

---

## Step 3: View in Airflow UI

```bash
# Get the Airflow web UI URL
gcloud composer environments describe co2-pipeline-env \
  --location=${REGION} \
  --format="value(config.airflowUri)"
```

Open the URL in your browser. You should see `co2_lakehouse_pipeline` in the DAG list.

---

## DAG Structure

```
ingest_kaggle_to_gcs
        │
        ▼
create_dataproc_cluster
        │
        ▼
run_pyspark_etl
        │
        ▼
delete_dataproc_cluster   ← always runs (trigger_rule=all_done)
        │
        ▼
load_to_bigquery
```

---

→ [Part 5 — Data Governance with Dataplex](part5-governance.md)
