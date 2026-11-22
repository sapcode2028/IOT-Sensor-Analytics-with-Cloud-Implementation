
import io
import os
import urllib.parse
import boto3
import pandas as pd
from sqlalchemy import create_engine

S3_BUCKET = os.getenv("S3_BUCKET", "iot-sensor-data-sapta-2026")
S3_KEY = os.getenv("S3_KEY", "iot_sensor_data.csv")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")

DB_HOST = os.getenv("DB_HOST", "database-2.cluster-cluqo4es6g2p.eu-north-1.rds.amazonaws.com")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")

# 1. Extract from S3
s3 = boto3.client("s3", region_name=AWS_REGION)
obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
df = pd.read_csv(io.BytesIO(obj["Body"].read()))

# 2. Transform
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="coerce")
df["humidity_pct"] = pd.to_numeric(df["humidity_pct"], errors="coerce")
df = df.dropna(subset=["timestamp", "temperature_c", "humidity_pct"])
df = df[(df["humidity_pct"].between(0, 100)) & (df["temperature_c"].between(-40, 85))]
df["date"] = df["timestamp"].dt.date
df["hour"] = df["timestamp"].dt.hour

# 3. Generate IAM auth token & load into PostgreSQL
rds = boto3.client("rds", region_name=AWS_REGION)
auth_token = rds.generate_db_auth_token(
    DBHostname=DB_HOST,
    Port=DB_PORT,
    DBUsername=DB_USER,
    Region=AWS_REGION,
)
encoded_token = urllib.parse.quote_plus(auth_token)

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{encoded_token}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"sslmode": "require"},
)
df.to_sql("sensor_readings", con=engine, if_exists="replace", index=False, chunksize=500)
print(f"Loaded {len(df)} clean rows into {DB_NAME}.sensor_readings")