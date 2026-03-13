"""
Cloud Function: Ingest CO2 Emissions dataset from Kaggle → Google Cloud Storage
Deploy as a Google Cloud Function (Gen 2) triggered by Cloud Scheduler or Pub/Sub.
"""

import os
import zipfile
import tempfile
import logging
from pathlib import Path

import functions_framework
from google.cloud import storage
import kaggle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────────────────
GCP_PROJECT_ID   = os.environ.get("GCP_PROJECT_ID", "your-project-id")
GCS_RAW_BUCKET   = os.environ.get("GCS_RAW_BUCKET", "your-project-raw")
KAGGLE_DATASET   = "debajyotipodder/co2-emission-by-vehicles"
GCS_DESTINATION  = "raw/co2_emissions/"


def download_kaggle_dataset(destination_dir: str) -> list[str]:
    """Download the Kaggle dataset and return list of extracted file paths."""
    logger.info(f"Downloading Kaggle dataset: {KAGGLE_DATASET}")
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        KAGGLE_DATASET,
        path=destination_dir,
        unzip=True
    )
    files = list(Path(destination_dir).glob("*.csv"))
    logger.info(f"Downloaded {len(files)} file(s): {[f.name for f in files]}")
    return [str(f) for f in files]


def upload_to_gcs(local_path: str, bucket_name: str, gcs_path: str) -> str:
    """Upload a local file to Google Cloud Storage."""
    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    gcs_uri = f"gs://{bucket_name}/{gcs_path}"
    logger.info(f"Uploaded {local_path} → {gcs_uri}")
    return gcs_uri


@functions_framework.http
def ingest_co2_data(request):
    """
    HTTP Cloud Function entry point.
    Triggered by Cloud Scheduler via HTTP POST.
    """
    logger.info("Starting CO2 data ingestion")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Download from Kaggle
        local_files = download_kaggle_dataset(tmpdir)

        if not local_files:
            logger.error("No files downloaded from Kaggle")
            return {"status": "error", "message": "No files downloaded"}, 500

        # 2. Upload each file to GCS raw zone
        uploaded = []
        for local_path in local_files:
            filename = Path(local_path).name
            gcs_path = f"{GCS_DESTINATION}{filename}"
            uri = upload_to_gcs(local_path, GCS_RAW_BUCKET, gcs_path)
            uploaded.append(uri)

    logger.info(f"Ingestion complete. {len(uploaded)} file(s) uploaded.")
    return {
        "status": "success",
        "files_uploaded": len(uploaded),
        "uris": uploaded
    }, 200


# ── Local testing ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Download to ./data/raw/ instead of GCS")
    args = parser.parse_args()

    if args.local:
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        files = download_kaggle_dataset(str(output_dir))
        print(f"Downloaded locally: {files}")
    else:
        # Simulate an HTTP request object for local testing
        class FakeRequest:
            method = "POST"
        result, status = ingest_co2_data(FakeRequest())
        print(f"Status {status}: {result}")
