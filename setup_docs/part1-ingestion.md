# Part 1 — Data Ingestion Layer with Cloud Functions

## Overview

In this layer we automate the collection of the CO2 emissions dataset from Kaggle and store it in Google Cloud Storage (GCS) as our raw data lake zone.

**Services used:** Cloud Functions (Gen 2) · Google Cloud Storage · Cloud Scheduler · Kaggle API

---

## Architecture

```
Cloud Scheduler (daily cron)
        │
        ▼
Cloud Function (HTTP trigger)
        │  downloads via Kaggle API
        ▼
Google Cloud Storage
└── gs://your-project-raw/raw/co2_emissions/CO2_Emissions_Canada.csv
```

---

## Step 1: Create GCS Buckets

```bash
export PROJECT_ID=your-project-id
export REGION=us-central1

# Raw zone — stores original unmodified data
gcloud storage buckets create gs://${PROJECT_ID}-raw \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --uniform-bucket-level-access

# Processed zone — stores cleaned Parquet files
gcloud storage buckets create gs://${PROJECT_ID}-processed \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --uniform-bucket-level-access

# Curated zone — stores analytics-ready data
gcloud storage buckets create gs://${PROJECT_ID}-curated \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --uniform-bucket-level-access
```

---

## Step 2: Set Up Kaggle API Credentials

1. Go to https://www.kaggle.com/settings → **API** → **Create New Token**
2. This downloads `kaggle.json` containing your username and key
3. Store credentials securely in GCP Secret Manager:

```bash
# Create secrets
echo -n "your-kaggle-username" | gcloud secrets create kaggle-username --data-file=-
echo -n "your-kaggle-key"      | gcloud secrets create kaggle-key --data-file=-
```

---

## Step 3: Deploy the Cloud Function

```bash
# From project root
cd scripts/ingest/

# Create a requirements.txt for the function
cat > requirements.txt << EOF
functions-framework==3.*
google-cloud-storage==2.*
kaggle==1.6.*
EOF

# Deploy
gcloud functions deploy ingest_co2_data \
  --gen2 \
  --runtime=python311 \
  --region=${REGION} \
  --source=. \
  --entry-point=ingest_co2_data \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID},GCS_RAW_BUCKET=${PROJECT_ID}-raw \
  --set-secrets KAGGLE_USERNAME=kaggle-username:latest,KAGGLE_KEY=kaggle-key:latest \
  --memory=512MB \
  --timeout=300s
```

---

## Step 4: Schedule with Cloud Scheduler

```bash
# Create a daily schedule at 02:00 UTC
gcloud scheduler jobs create http co2-daily-ingest \
  --location=${REGION} \
  --schedule="0 2 * * *" \
  --uri="$(gcloud functions describe ingest_co2_data --region=${REGION} --format='value(serviceConfig.uri)')" \
  --http-method=POST \
  --message-body="{}" \
  --headers="Content-Type=application/json"
```

---

## Step 5: Test Manually

```bash
# Trigger the function manually to test
gcloud functions call ingest_co2_data \
  --region=${REGION} \
  --gen2 \
  --data='{}'

# Verify data landed in GCS
gcloud storage ls gs://${PROJECT_ID}-raw/raw/co2_emissions/
```

You should see `CO2_Emissions_Canada.csv` listed.

---

## Expected Output

```
gs://your-project-raw/raw/co2_emissions/CO2_Emissions_Canada.csv
```

File size: ~500KB · Rows: ~7,385 · Format: CSV with header row

---

## Next Step

→ [Part 2a — Process with Dataproc PySpark](part2a-dataproc.md)
