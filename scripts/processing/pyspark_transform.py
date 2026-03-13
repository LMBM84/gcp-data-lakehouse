"""
Dataproc PySpark Job: Transform raw CO2 emissions CSV from GCS → processed Parquet
Submit via: gcloud dataproc jobs submit pyspark pyspark_transform.py --cluster=CLUSTER --region=REGION
"""

import os
import sys
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
GCS_RAW_BUCKET       = os.environ.get("GCS_RAW_BUCKET", "your-project-raw")
GCS_PROCESSED_BUCKET = os.environ.get("GCS_PROCESSED_BUCKET", "your-project-processed")
RAW_PATH             = f"gs://{GCS_RAW_BUCKET}/raw/co2_emissions/"
PROCESSED_PATH       = f"gs://{GCS_PROCESSED_BUCKET}/processed/co2_emissions/"

LOCAL_RAW_PATH       = "data/raw/"
LOCAL_PROCESSED_PATH = "data/processed/"


def create_spark_session(local: bool = False) -> SparkSession:
    builder = SparkSession.builder.appName("CO2EmissionsETL")
    if local:
        builder = builder.master("local[*]")
    return builder.getOrCreate()


def read_raw_data(spark: SparkSession, path: str):
    logger.info(f"Reading raw CSV from: {path}")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(path)
    logger.info(f"Raw data: {df.count()} rows, {len(df.columns)} columns")
    return df


def clean_column_names(df):
    """Standardise column names to snake_case."""
    rename_map = {
        "Make":                 "make",
        "Model":                "model",
        "Vehicle Class":        "vehicle_class",
        "Engine Size(L)":       "engine_size_l",
        "Cylinders":            "cylinders",
        "Transmission":         "transmission",
        "Fuel Type":            "fuel_type",
        "Fuel Consumption City (L/100 km)":    "fuel_city_l100km",
        "Fuel Consumption Hwy (L/100 km)":     "fuel_hwy_l100km",
        "Fuel Consumption Comb (L/100 km)":    "fuel_comb_l100km",
        "Fuel Consumption Comb (mpg)":         "fuel_comb_mpg",
        "CO2 Emissions(g/km)":  "co2_emissions_g_km",
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df = df.withColumnRenamed(old, new)
    return df


def cast_columns(df):
    """Cast numeric columns to correct types."""
    numeric_cols = [
        ("engine_size_l",    DoubleType()),
        ("cylinders",        IntegerType()),
        ("fuel_city_l100km", DoubleType()),
        ("fuel_hwy_l100km",  DoubleType()),
        ("fuel_comb_l100km", DoubleType()),
        ("fuel_comb_mpg",    IntegerType()),
        ("co2_emissions_g_km", IntegerType()),
    ]
    for col, dtype in numeric_cols:
        if col in df.columns:
            df = df.withColumn(col, F.col(col).cast(dtype))
    return df


def remove_duplicates(df):
    before = df.count()
    df = df.dropDuplicates()
    after = df.count()
    logger.info(f"Deduplication: {before} → {after} rows (removed {before - after})")
    return df


def handle_nulls(df):
    """Drop rows missing critical fields."""
    critical = ["make", "model", "co2_emissions_g_km", "engine_size_l"]
    critical_existing = [c for c in critical if c in df.columns]
    before = df.count()
    df = df.dropna(subset=critical_existing)
    after = df.count()
    logger.info(f"Null removal: {before} → {after} rows (removed {before - after})")
    return df


def add_derived_columns(df):
    """Add computed columns useful for analytics."""
    if "fuel_city_l100km" in df.columns and "fuel_hwy_l100km" in df.columns:
        df = df.withColumn(
            "avg_fuel_consumption_l100km",
            (F.col("fuel_city_l100km") + F.col("fuel_hwy_l100km")) / 2
        )
    if "co2_emissions_g_km" in df.columns:
        # Emission category buckets
        df = df.withColumn(
            "emission_category",
            F.when(F.col("co2_emissions_g_km") < 120, "Low")
             .when(F.col("co2_emissions_g_km") < 200, "Medium")
             .when(F.col("co2_emissions_g_km") < 280, "High")
             .otherwise("Very High")
        )
    return df


def transform(spark: SparkSession, raw_path: str, output_path: str):
    df = read_raw_data(spark, raw_path)
    df = clean_column_names(df)
    df = cast_columns(df)
    df = remove_duplicates(df)
    df = handle_nulls(df)
    df = add_derived_columns(df)

    logger.info(f"Writing processed data to: {output_path}")
    df.write.mode("overwrite").parquet(output_path)
    logger.info(f"Done. Final row count: {df.count()}")
    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    spark = create_spark_session(local=args.local)

    if args.local:
        transform(spark, LOCAL_RAW_PATH, LOCAL_PROCESSED_PATH)
    else:
        transform(spark, RAW_PATH, PROCESSED_PATH)

    spark.stop()
