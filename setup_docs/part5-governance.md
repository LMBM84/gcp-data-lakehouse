# Part 5 — Data Governance Layer with Dataplex

## Overview

Dataplex provides automated data cataloguing, lineage tracking, and data quality scanning across all GCS zones and BigQuery tables.

---

## Step 1: Create a Dataplex Lake

```bash
gcloud dataplex lakes create co2-data-lake \
  --location=${REGION} \
  --project=${PROJECT_ID} \
  --display-name="CO2 Emissions Data Lake"
```

---

## Step 2: Add Zones

```bash
# Raw zone
gcloud dataplex zones create raw-zone \
  --lake=co2-data-lake \
  --location=${REGION} \
  --type=RAW \
  --resource-location-type=SINGLE_REGION \
  --display-name="Raw Zone"

# Curated zone (processed + BigQuery)
gcloud dataplex zones create curated-zone \
  --lake=co2-data-lake \
  --location=${REGION} \
  --type=CURATED \
  --resource-location-type=SINGLE_REGION \
  --display-name="Curated Zone"
```

---

## Step 3: Attach Assets

```bash
# Attach raw GCS bucket
gcloud dataplex assets create raw-co2-data \
  --lake=co2-data-lake \
  --zone=raw-zone \
  --location=${REGION} \
  --resource-type=STORAGE_BUCKET \
  --resource-name=projects/${PROJECT_ID}/buckets/${PROJECT_ID}-raw \
  --display-name="Raw CO2 CSV Files"

# Attach BigQuery dataset
gcloud dataplex assets create bq-co2-dataset \
  --lake=co2-data-lake \
  --zone=curated-zone \
  --location=${REGION} \
  --resource-type=BIGQUERY_DATASET \
  --resource-name=projects/${PROJECT_ID}/datasets/co2_emissions \
  --display-name="CO2 Emissions BigQuery Dataset"
```

---

## Step 4: Create a Data Quality Scan

```bash
gcloud dataplex datascans create data-quality co2-quality-scan \
  --location=${REGION} \
  --data-bigquery-table=projects/${PROJECT_ID}/datasets/co2_emissions/tables/vehicles_processed \
  --display-name="CO2 Data Quality Scan"
```

Quality rules to configure in the console:
- `co2_emissions_g_km` — Not null, range 0–1000
- `engine_size_l` — Not null, range 0.5–9.0
- `make` — Not null, not empty string
- `fuel_type` — One of: X, Z, D, E, N

---

## What Dataplex Gives You

| Feature | Benefit |
|---|---|
| Automated data catalogue | All assets discoverable in one place |
| Data lineage | Track how data flows from GCS → Dataproc → BigQuery |
| Quality scans | Automated checks run after every pipeline execution |
| Schema detection | Auto-detects column types from Parquet and CSV |
| Access control | Centrally manage who can read/write each zone |

---

→ Part 6 — Visualization with Looker Studio *(see `/images` folder for dashboard screenshots)*
