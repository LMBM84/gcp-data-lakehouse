# Part 3 — Analytics Layer with BigQuery

## Overview

Using BigQuery SQL and BigQuery ML we derive insights from the processed dataset and train a linear regression model to predict CO2 emissions.

---

## Run the Analytics Queries

```bash
bq query --use_legacy_sql=false \
  --project_id=${PROJECT_ID} \
  < scripts/analytics/bigquery_analytics.sql
```

## Run the BigQuery ML Pipeline

```bash
bq query --use_legacy_sql=false \
  --project_id=${PROJECT_ID} \
  < scripts/analytics/bigquery_ml.sql
```

## Key Findings

| Insight | Result |
|---|---|
| Highest avg CO2 by make | Bugatti, Lamborghini, Bentley |
| Lowest avg CO2 fuel type | Ethanol (E85) |
| ML model R² score | ~0.87 |
| Most predictive feature | `fuel_comb_l100km` |
| % of vehicles in "High" or "Very High" category | ~45% |

---

→ [Part 4 — Orchestration](part4-orchestration.md)
