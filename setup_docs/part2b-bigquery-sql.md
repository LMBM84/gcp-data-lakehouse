# Part 2b — Data Processing Layer with BigQuery SQL

## Overview

After PySpark writes processed Parquet files to GCS, we create an external table in BigQuery pointing at those files, then load them into a native partitioned and clustered BigQuery table for fast querying.

---

## Step 1: Create BigQuery Dataset

```bash
bq --location=US mk \
  --dataset \
  --description="CO2 emissions by vehicles — Canada" \
  ${PROJECT_ID}:co2_emissions
```

---

## Step 2: Run the SQL transformations

Open the BigQuery console or use `bq query`:

```bash
bq query \
  --use_legacy_sql=false \
  --project_id=${PROJECT_ID} \
  < scripts/processing/bigquery_transform.sql
```

---

## Step 3: Verify the table

```bash
bq show ${PROJECT_ID}:co2_emissions.vehicles_processed

bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as rows FROM \`${PROJECT_ID}.co2_emissions.vehicles_processed\`"
```

Expected: ~7,260 rows after cleaning.

---

→ [Part 3 — Analytics Layer](part3-analytics.md)
