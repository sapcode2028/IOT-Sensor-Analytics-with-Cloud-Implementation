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

queries = {
    "1. Preview (top 10)": "SELECT * FROM sensor_readings LIMIT 10;",
    "2. Overall summary": """
        SELECT
            COUNT(*) AS total_clean_rows,
            ROUND(MIN(temperature_c)::numeric, 2) AS min_temp_c,
            ROUND(MAX(temperature_c)::numeric, 2) AS max_temp_c,
            ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp_c,
            ROUND(MIN(humidity_pct)::numeric, 2) AS min_humidity_pct,
            ROUND(MAX(humidity_pct)::numeric, 2) AS max_humidity_pct,
            ROUND(AVG(humidity_pct)::numeric, 2) AS avg_humidity_pct
        FROM sensor_readings;
    """,
    "3. By sensor": """
        SELECT
            sensor_id,
            COUNT(*) AS reading_count,
            ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp_c,
            ROUND(AVG(humidity_pct)::numeric, 2) AS avg_humidity_pct
        FROM sensor_readings
        GROUP BY sensor_id
        ORDER BY sensor_id;
    """,
    "4. Daily trend": """
        SELECT
            date,
            ROUND(AVG(temperature_c)::numeric, 2) AS daily_avg_temp_c,
            ROUND(AVG(humidity_pct)::numeric, 2) AS daily_avg_humidity_pct
        FROM sensor_readings
        GROUP BY date
        ORDER BY date;
    """,
}

for title, sql in queries.items():
    print(f"\n=== {title} ===")
    print(pd.read_sql(sql, engine).to_string(index=False))