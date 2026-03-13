-- ============================================================
-- Part 2b: BigQuery SQL Transformation
-- Loads processed Parquet from GCS into BigQuery and applies
-- further SQL-based transformations.
-- ============================================================

-- ── Step 1: Create the dataset ──────────────────────────────
CREATE SCHEMA IF NOT EXISTS `your-project-id.co2_emissions`
OPTIONS (
  description = "CO2 emissions by vehicles — Canada",
  location = "US"
);


-- ── Step 2: Create external table over GCS Parquet files ────
CREATE OR REPLACE EXTERNAL TABLE `your-project-id.co2_emissions.vehicles_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://your-project-processed/processed/co2_emissions/*.parquet']
);


-- ── Step 3: Load into native BigQuery table ─────────────────
CREATE OR REPLACE TABLE `your-project-id.co2_emissions.vehicles_processed`
PARTITION BY RANGE_BUCKET(co2_emissions_g_km, GENERATE_ARRAY(0, 600, 50))
CLUSTER BY make, fuel_type
AS
SELECT
  make,
  model,
  vehicle_class,
  engine_size_l,
  cylinders,
  transmission,
  fuel_type,
  fuel_city_l100km,
  fuel_hwy_l100km,
  fuel_comb_l100km,
  fuel_comb_mpg,
  co2_emissions_g_km,
  avg_fuel_consumption_l100km,
  emission_category,
  CURRENT_TIMESTAMP() AS ingested_at
FROM `your-project-id.co2_emissions.vehicles_external`;


-- ── Step 4: Data quality check ──────────────────────────────
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(co2_emissions_g_km IS NULL) AS null_emissions,
  COUNTIF(engine_size_l IS NULL)      AS null_engine_size,
  COUNTIF(make IS NULL)               AS null_make,
  MIN(co2_emissions_g_km)             AS min_co2,
  MAX(co2_emissions_g_km)             AS max_co2,
  ROUND(AVG(co2_emissions_g_km), 2)   AS avg_co2
FROM `your-project-id.co2_emissions.vehicles_processed`;
