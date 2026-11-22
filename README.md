# IoT Sensor Telemetry Analytics Pipeline (AWS S3 → Aurora PostgreSQL → Tableau Public)

An end-to-end IoT sensor analytics project that ingests telemetry data into Amazon S3, loads and queries cleaned records in Amazon Aurora PostgreSQL (`database-2` in `eu-north-1`), exports curated CSV extracts, and visualizes trends and sensor comparisons in Tableau Public.

## Architecture & Workflow

1. **Data Source & Storage (AWS S3):** Raw/source IoT sensor telemetry (`iot_sensor_data.csv`, covering `2026-11-01` to `2026-11-10` across `SENS_01`–`SENS_04`) stored in AWS S3.
2. **Relational Warehouse (Amazon Aurora PostgreSQL):** Cleaned telemetry (`1,495` clean rows in `sensor_readings`) queried on `database-2` (`eu-north-1`) via Python and SQL (`run_analytics.py`).
3. **Tableau Public Exports:** CSV extracts generated for visualization:
   - `sensor_readings_tableau.csv`
   - `sensor_summary_tableau.csv`[cite: 1]
   - `daily_sensor_trends_tableau.csv`[cite: 1]
4. **Interactive Visualization (Tableau Public):** Dashboard featuring KPI summary cards, daily trend lines, sensor comparison charts, a pie chart showing reading share by sensor, and interactive filters, published to Tableau Public[cite: 1].

## Project Structure

```text
iot-aws-analytics/
├── run_analytics.py               # Runs SQL/Python analytics queries against PostgreSQL[cite: 1]
├── sensor_readings_tableau.csv    # Full cleaned readings export for Tableau Public[cite: 1]
├── sensor_summary_tableau.csv     # Sensor-level summary export for Tableau Public[cite: 1]
├── daily_sensor_trends_tableau.csv# Daily sensor trend export for Tableau Public[cite: 1]
└── README.md

PUBBISHED LINK: https://public.tableau.com:9443/views/IoTSensorAnalytics/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link
