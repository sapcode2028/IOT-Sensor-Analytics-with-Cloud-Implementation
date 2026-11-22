import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)
sensors = ["SENS_01", "SENS_02", "SENS_03", "SENS_04"]
start_time = datetime(2026, 11, 1, 0, 0, 0)
rows = []

for i in range(1500):
    ts = start_time + timedelta(minutes=10 * i)
    sensor_id = sensors[i % len(sensors)]
    hour_factor = -3.0 * ((ts.hour - 14) / 12.0) ** 2 + 3.0
    base_temp = 24.0 + hour_factor + (sensors.index(sensor_id) * 1.2)
    temp = round(base_temp + random.uniform(-1.5, 1.5), 2)
    humidity = round(max(25.0, min(95.0, 72.0 - (temp - 20.0) * 1.8 + random.uniform(-4.0, 4.0))), 2)

    if i in (25, 140, 610):
        temp = None
    if i in (88, 420):
        humidity = 150.0

    rows.append({
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "sensor_id": sensor_id,
        "temperature_c": temp,
        "humidity_pct": humidity,
        "battery_pct": random.randint(45, 100)
    })

pd.DataFrame(rows).to_csv("iot_sensor_data.csv", index=False)
print("Generated iot_sensor_data.csv")