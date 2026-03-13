# Part 2a — Data Processing Layer with Dataproc (PySpark)

## Overview

The raw CSV from GCS is cleaned, deduplicated, and enriched using a PySpark job running on a Dataproc cluster. Output is written as Parquet to the processed GCS zone.

**Services used:** Dataproc · Google Cloud Storage · PySpark

---

## Step 1: Upload the PySpark script to GCS

```bash
gcloud storage cp scripts/processing/pyspark_transform.py \
  gs://${PROJECT_ID}-raw/scripts/pyspark_transform.py
```

---

## Step 2: Create a Dataproc Cluster

```bash
gcloud dataproc clusters create co2-processing-cluster \
  --region=${REGION} \
  --zone=${REGION}-a \
  --master-machine-type=n1-standard-2 \
  --master-boot-disk-size=50GB \
  --num-workers=2 \
  --worker-machine-type=n1-standard-2 \
  --worker-boot-disk-size=50GB \
  --image-version=2.1-debian11 \
  --project=${PROJECT_ID}
```

---

## Step 3: Submit the PySpark Job

```bash
gcloud dataproc jobs submit pyspark \
  gs://${PROJECT_ID}-raw/scripts/pyspark_transform.py \
  --cluster=co2-processing-cluster \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  -- --gcs
```

---

## Step 4: Verify Output

```bash
gcloud storage ls gs://${PROJECT_ID}-processed/processed/co2_emissions/
```

You should see `.parquet` part files.

---

## Step 5: Delete the Cluster (save costs!)

```bash
gcloud dataproc clusters delete co2-processing-cluster \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --quiet
```

---

## Transformations Applied

| Step | Action |
|---|---|
| Column rename | Standardise to snake_case |
| Type casting | Engine size → FLOAT, Cylinders → INT, CO2 → INT |
| Deduplication | `dropDuplicates()` — removed ~120 duplicate rows |
| Null removal | Drop rows missing make, model, or CO2 value |
| Derived columns | `avg_fuel_consumption_l100km`, `emission_category` |

---

→ [Part 2b — BigQuery SQL Transformation](part2b-bigquery-sql.md)
