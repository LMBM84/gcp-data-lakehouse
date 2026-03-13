-- ============================================================
-- BigQuery ML: Predict CO2 Emissions
-- Trains a linear regression model to predict CO2 g/km
-- from engine features, then evaluates and predicts.
-- ============================================================

-- ── Step 1: Create ML feature table ─────────────────────────
CREATE OR REPLACE TABLE `your-project-id.co2_emissions.vehicles_ml_features` AS
SELECT
  engine_size_l,
  cylinders,
  fuel_comb_l100km,
  fuel_city_l100km,
  fuel_hwy_l100km,
  -- One-hot encode fuel type
  IF(fuel_type = 'X', 1, 0)  AS fuel_regular,
  IF(fuel_type = 'Z', 1, 0)  AS fuel_premium,
  IF(fuel_type = 'D', 1, 0)  AS fuel_diesel,
  IF(fuel_type = 'E', 1, 0)  AS fuel_ethanol,
  -- Transmission type
  IF(transmission LIKE 'A%', 1, 0) AS is_automatic,
  co2_emissions_g_km            AS label
FROM `your-project-id.co2_emissions.vehicles_processed`
WHERE co2_emissions_g_km IS NOT NULL
  AND engine_size_l IS NOT NULL
  AND fuel_comb_l100km IS NOT NULL;


-- ── Step 2: Train linear regression model ───────────────────
CREATE OR REPLACE MODEL `your-project-id.co2_emissions.co2_predictor`
OPTIONS (
  model_type = 'LINEAR_REG',
  input_label_cols = ['label'],
  data_split_method = 'AUTO_SPLIT',
  enable_global_explain = TRUE
) AS
SELECT * FROM `your-project-id.co2_emissions.vehicles_ml_features`;


-- ── Step 3: Evaluate model performance ──────────────────────
SELECT
  mean_absolute_error,
  mean_squared_error,
  mean_squared_log_error,
  median_absolute_error,
  r2_score,
  explained_variance
FROM ML.EVALUATE(
  MODEL `your-project-id.co2_emissions.co2_predictor`,
  (SELECT * FROM `your-project-id.co2_emissions.vehicles_ml_features`)
);


-- ── Step 4: Predict on new/unseen vehicles ───────────────────
SELECT
  make,
  model,
  co2_emissions_g_km          AS actual_co2,
  ROUND(predicted_label, 1)   AS predicted_co2,
  ROUND(ABS(co2_emissions_g_km - predicted_label), 1) AS abs_error
FROM ML.PREDICT(
  MODEL `your-project-id.co2_emissions.co2_predictor`,
  (
    SELECT
      v.engine_size_l,
      v.cylinders,
      v.fuel_comb_l100km,
      v.fuel_city_l100km,
      v.fuel_hwy_l100km,
      IF(v.fuel_type = 'X', 1, 0)  AS fuel_regular,
      IF(v.fuel_type = 'Z', 1, 0)  AS fuel_premium,
      IF(v.fuel_type = 'D', 1, 0)  AS fuel_diesel,
      IF(v.fuel_type = 'E', 1, 0)  AS fuel_ethanol,
      IF(v.transmission LIKE 'A%', 1, 0) AS is_automatic,
      v.make,
      v.model,
      v.co2_emissions_g_km
    FROM `your-project-id.co2_emissions.vehicles_processed` v
    LIMIT 100
  )
)
ORDER BY abs_error DESC;


-- ── Step 5: Feature importance ───────────────────────────────
SELECT *
FROM ML.GLOBAL_EXPLAIN(MODEL `your-project-id.co2_emissions.co2_predictor`)
ORDER BY attribution DESC;
