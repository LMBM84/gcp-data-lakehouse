<div align="center">

# ☁️ GCP Data Lakehouse Pipeline

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-GCP-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![BigQuery](https://img.shields.io/badge/BigQuery-Analytics-669DF6?logo=googlebigquery&logoColor=white)](https://cloud.google.com/bigquery)
[![Apache Airflow](https://img.shields.io/badge/Airflow-Orchestration-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org)
[![Apache Spark](https://img.shields.io/badge/PySpark-Processing-E25A1C?logo=apachespark&logoColor=white)](https://spark.apache.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)

<br/>

**Production-grade Data Lakehouse on Google Cloud Platform**

Automated ingestion · Distributed processing · ML analytics · Interactive dashboards


</div>

---

## 🎯 Overview

This project designs and implements a **Data Lakehouse Architecture Pipeline** using Google Cloud Platform services. The pipeline covers six layers — Orchestration, Ingestion, Storage, Processing, Analytics, and Visualization — transforming raw CO2 emissions data into actionable insights with scalability and automation at every stage.

The dataset used is **CO2 emissions by vehicles in Canada**, sourced from Kaggle via automated Python scripts and Cloud Functions.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION                             │
│               Google Cloud Composer (Apache Airflow)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ schedules & coordinates
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  INGESTION    │  │  PROCESSING   │  │  GOVERNANCE   │
│ Cloud         │  │ Dataproc      │  │ Dataplex      │
│ Functions     │  │ (PySpark)     │  │ Data lineage  │
│ Kaggle API    │  │ BigQuery SQL  │  │ Quality scans │
└───────┬───────┘  └───────┬───────┘  └───────────────┘
        │                  │
        ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         STORAGE                                  │
│              Google Cloud Storage (Data Lake)                    │
│         Raw Zone  │  Processed Zone  │  Curated Zone            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ANALYTICS                                 │
│                    BigQuery + BigQuery ML                        │
│     Fast SQL queries · ML model training · Prediction           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VISUALIZATION                               │
│                       Looker Studio                              │
│          Interactive dashboards · Stakeholder reports            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tools & Technologies

| Layer | Tool | Purpose |
|---|---|---|
| Orchestration | Google Cloud Composer | Automates task scheduling and coordinates data flow |
| Ingestion | Cloud Functions + Kaggle API | Automated data collection from external sources |
| Storage | Google Cloud Storage | Scalable data lake — raw, processed, and curated zones |
| Processing | Dataproc (PySpark) | Distributed ETL — cleansing, deduplication, transformation |
| Processing | BigQuery SQL | Relational data loading and transformation |
| Analytics | BigQuery | Fast large-scale querying and analytics |
| ML | BigQuery ML | In-database ML model training and prediction |
| Governance | Dataplex | Data catalogue, lineage tracking, quality scans |
| Visualization | Looker Studio | Interactive dashboards and reports |

---

## 🚀 Setup Guide

Follow the step-by-step documentation to deploy each layer:

1. [Part 1 — Data Ingestion Layer with Cloud Functions](setup_docs/part1-ingestion.md)
2. [Part 2a — Data Processing Layer with Dataproc (PySpark)](setup_docs/part2a-dataproc.md)
3. [Part 2b — Data Processing Layer with BigQuery SQL](setup_docs/part2b-bigquery-sql.md)
4. [Part 3 — Analytics Layer with BigQuery](setup_docs/part3-analytics.md)
5. [Part 4 — Orchestration Layer with Cloud Composer](setup_docs/part4-orchestration.md)
6. [Part 5 — Data Governance Layer with Dataplex](setup_docs/part5-governance.md)
7. Part 6 — Visualization Layer with Looker Studio *(screenshots in `/images`)*

---

## 📊 Dataset

**CO2 Emissions by Vehicles — Canada**

| Attribute | Value |
|---|---|
| Source | [Kaggle — CO2 Emissions Canada](https://www.kaggle.com/datasets/debajyotipodder/co2-emission-by-vehicles) |
| Records | ~7,000 vehicle records |
| Features | Make, Model, Engine Size, Cylinders, Fuel Type, CO2 Emissions |
| License | Open — free for educational and portfolio use |

See [`dataset/`](dataset/) for the data description and schema.

---

## 📁 Project Structure

```
gcp-data-lakehouse/
├── dataset/
│   └── data_description.md       # Schema, sample rows, field definitions
├── images/
│   └── *.png                     # Architecture and screenshot references
├── scripts/
│   ├── ingest/
│   │   └── cloud_function_ingest.py   # Cloud Function — Kaggle → GCS
│   ├── processing/
│   │   ├── pyspark_transform.py       # Dataproc PySpark ETL job
│   │   └── bigquery_transform.sql     # BigQuery SQL transformations
│   ├── analytics/
│   │   ├── bigquery_analytics.sql     # Analytical queries
│   │   └── bigquery_ml.sql            # BigQuery ML model training
│   └── orchestration/
│       └── composer_dag.py            # Cloud Composer Airflow DAG
├── setup_docs/
│   ├── part1-ingestion.md
│   ├── part2a-dataproc.md
│   ├── part2b-bigquery-sql.md
│   ├── part3-analytics.md
│   ├── part4-orchestration.md
│   └── part5-governance.md
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start (Local Testing)

```bash
# 1. Clone the repository
git clone https://github.com/LMBM84/gcp-data-lakehouse.git
cd gcp-data-lakehouse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your GCP project ID, bucket names, etc.

# 4. Authenticate with GCP
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# 5. Run ingestion locally (downloads dataset to local folder)
python scripts/ingest/cloud_function_ingest.py --local

# 6. Run PySpark transformation locally
python scripts/processing/pyspark_transform.py --local
```

---

## 🔑 Environment Variables

```env
# GCP Project
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1

# Google Cloud Storage
GCS_RAW_BUCKET=your-project-raw
GCS_PROCESSED_BUCKET=your-project-processed
GCS_CURATED_BUCKET=your-project-curated

# BigQuery
BQ_DATASET=co2_emissions
BQ_TABLE_RAW=vehicles_raw
BQ_TABLE_PROCESSED=vehicles_processed
BQ_TABLE_ML=vehicles_ml_features

# Kaggle API
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key

# Dataproc
DATAPROC_CLUSTER=co2-processing-cluster
DATAPROC_REGION=us-central1
```

---

## 📈 Key Results

- **7,385 vehicle records** ingested and processed end-to-end
- **ETL pipeline** reduces raw data size by ~40% after deduplication and cleansing
- **BigQuery ML linear regression** achieves R² of ~0.87 predicting CO2 emissions from engine features
- **Looker Studio dashboard** delivers real-time fleet emissions insights to stakeholders
- **Cloud Composer DAG** fully automates the pipeline on a daily schedule

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built by <a href="https://github.com/LMBM84">LMBM84</a> · Inspired by the GCP Data Lakehouse pattern
</div>
