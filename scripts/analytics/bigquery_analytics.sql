-- ============================================================
-- Part 3: BigQuery Analytics Queries
-- Analytical SQL for CO2 emissions insights
-- ============================================================

-- ── 1. Average CO2 emissions by make ────────────────────────
SELECT
  make,
  COUNT(*)                                  AS vehicle_count,
  ROUND(AVG(co2_emissions_g_km), 1)         AS avg_co2_g_km,
  ROUND(MIN(co2_emissions_g_km), 1)         AS min_co2_g_km,
  ROUND(MAX(co2_emissions_g_km), 1)         AS max_co2_g_km
FROM `your-project-id.co2_emissions.vehicles_processed`
GROUP BY make
ORDER BY avg_co2_g_km DESC
LIMIT 20;


-- ── 2. Emissions by fuel type ────────────────────────────────
SELECT
  fuel_type,
  COUNT(*)                                  AS vehicle_count,
  ROUND(AVG(co2_emissions_g_km), 1)         AS avg_co2_g_km,
  ROUND(AVG(fuel_comb_l100km), 2)           AS avg_fuel_comb_l100km
FROM `your-project-id.co2_emissions.vehicles_processed`
GROUP BY fuel_type
ORDER BY avg_co2_g_km DESC;


-- ── 3. Emission category distribution ───────────────────────
SELECT
  emission_category,
  COUNT(*)                                  AS count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM `your-project-id.co2_emissions.vehicles_processed`
GROUP BY emission_category
ORDER BY count DESC;


-- ── 4. Engine size vs CO2 correlation buckets ────────────────
SELECT
  ROUND(engine_size_l, 1)                   AS engine_size_rounded,
  COUNT(*)                                  AS count,
  ROUND(AVG(co2_emissions_g_km), 1)         AS avg_co2_g_km
FROM `your-project-id.co2_emissions.vehicles_processed`
GROUP BY engine_size_rounded
ORDER BY engine_size_rounded;


-- ── 5. Top 10 lowest emission vehicles ───────────────────────
SELECT
  make,
  model,
  vehicle_class,
  fuel_type,
  engine_size_l,
  co2_emissions_g_km
FROM `your-project-id.co2_emissions.vehicles_processed`
ORDER BY co2_emissions_g_km ASC
LIMIT 10;


-- ── 6. Transmission type impact on emissions ─────────────────
SELECT
  CASE
    WHEN transmission LIKE 'A%' THEN 'Automatic'
    WHEN transmission LIKE 'M%' THEN 'Manual'
    WHEN transmission LIKE 'AM%' THEN 'Automated Manual'
    WHEN transmission LIKE 'AV%' THEN 'CVT'
    ELSE 'Other'
  END                                       AS transmission_type,
  COUNT(*)                                  AS count,
  ROUND(AVG(co2_emissions_g_km), 1)         AS avg_co2_g_km
FROM `your-project-id.co2_emissions.vehicles_processed`
GROUP BY transmission_type
ORDER BY avg_co2_g_km;
