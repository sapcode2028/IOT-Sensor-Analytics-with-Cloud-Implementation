import os
import urllib.parse
import boto3
import pandas as pd
from sqlalchemy import create_engine

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")
DB_HOST = os.getenv("DB_HOST", "database-2.cluster-cluqo4es6g2p.eu-north-1.rds.amazonaws.com")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")

rds = boto3.client("rds", region_name=AWS_REGION)
token = rds.generate_db_auth_token(
    DBHostname=DB_HOST,
    Port=DB_PORT,
    DBUsername=DB_USER,
    Region=AWS_REGION,
)
encoded_token = urllib.parse.quote_plus(token)

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{encoded_token}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"sslmode": "require"},
)

# 1. Full cleaned readings (great for interactive charts & filters)
df_full = pd.read_sql("SELECT * FROM sensor_readings ORDER BY timestamp;", engine)
df_full.to_csv("sensor_readings_tableau.csv", index=False)

# 2. Sensor-level summary (optional extra CSV for quick comparison)
df_sensor = pd.read_sql(
    """
    SELECT
        sensor_id,
        COUNT(*) AS reading_count,
        ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp_c,
        ROUND(AVG(humidity_pct)::numeric, 2) AS avg_humidity_pct,
        ROUND(AVG(battery_pct)::numeric, 2) AS avg_battery_pct
    FROM sensor_readings
    GROUP BY sensor_id
    ORDER BY sensor_id;
    """,
    engine,
)
df_sensor.to_csv("sensor_summary_tableau.csv", index=False)

# 3. Daily summary (optional extra CSV)
df_daily = pd.read_sql(
    """
    SELECT
        date,
        sensor_id,
        COUNT(*) AS reading_count,
        ROUND(AVG(temperature_c)::numeric, 2) AS daily_avg_temp_c,
        ROUND(AVG(humidity_pct)::numeric, 2) AS daily_avg_humidity_pct,
        ROUND(AVG(battery_pct)::numeric, 2) AS daily_avg_battery_pct
    FROM sensor_readings
    GROUP BY date, sensor_id
    ORDER BY date, sensor_id;
    """,
    engine,
)
df_daily.to_csv("daily_sensor_trends_tableau.csv", index=False)

print("Exported CSV files successfully.")