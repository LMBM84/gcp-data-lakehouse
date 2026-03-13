# Dataset: CO2 Emissions by Vehicles — Canada

## Source
- **Provider:** Government of Canada / Kaggle
- **Kaggle URL:** https://www.kaggle.com/datasets/debajyotipodder/co2-emission-by-vehicles
- **License:** Open — free for educational and portfolio use
- **Records:** ~7,385 vehicles
- **Coverage:** Multiple model years, all major manufacturers

## Schema

| Column | Type | Description |
|---|---|---|
| `make` | STRING | Vehicle manufacturer (e.g. Toyota, Ford) |
| `model` | STRING | Vehicle model name |
| `vehicle_class` | STRING | Category (SUV, Compact, Mid-size, etc.) |
| `engine_size_l` | FLOAT | Engine displacement in litres |
| `cylinders` | INTEGER | Number of cylinders |
| `transmission` | STRING | Transmission code (A6 = 6-speed auto, M5 = 5-speed manual) |
| `fuel_type` | STRING | Fuel type code (X=Regular, Z=Premium, D=Diesel, E=Ethanol, N=Natural Gas) |
| `fuel_city_l100km` | FLOAT | City fuel consumption (L/100km) |
| `fuel_hwy_l100km` | FLOAT | Highway fuel consumption (L/100km) |
| `fuel_comb_l100km` | FLOAT | Combined fuel consumption (L/100km) |
| `fuel_comb_mpg` | INTEGER | Combined fuel consumption (mpg) |
| `co2_emissions_g_km` | INTEGER | CO2 tailpipe emissions (g/km) — **target variable** |

## Derived Columns (added during processing)

| Column | Description |
|---|---|
| `avg_fuel_consumption_l100km` | Average of city and highway fuel consumption |
| `emission_category` | Bucketed: Low (<120), Medium (<200), High (<280), Very High (≥280) |
| `ingested_at` | Timestamp when the record was loaded into BigQuery |

## Sample Rows

| make | model | engine_size_l | cylinders | fuel_type | co2_emissions_g_km |
|---|---|---|---|---|---|
| ACURA | ILX | 2.0 | 4 | Z | 221 |
| BMW | 325i | 2.5 | 6 | Z | 221 |
| FORD | F-150 | 5.0 | 8 | X | 346 |
| TOYOTA | Prius | 1.8 | 4 | X | 96 |
| HONDA | Civic | 1.5 | 4 | Z | 136 |

## Fuel Type Codes

| Code | Fuel |
|---|---|
| X | Regular gasoline |
| Z | Premium gasoline |
| D | Diesel |
| E | Ethanol (E85) |
| N | Natural gas |
