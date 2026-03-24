import pandas as pd
import pymysql

conn = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,charset="utf8"
)

ENTITY = "sensor.bhpzem_main_energy"
YEAR = 2025

query = f"""
SELECT
    hour,
    HOUR(hour) + 1 AS hour_number,
    MONTH(hour) AS month,
    DAY(hour) AS day,
    hourly_kwh
FROM (
    SELECT
        FROM_UNIXTIME(s.start_ts) AS hour,
        s.sum - LAG(s.sum) OVER (ORDER BY s.start_ts) AS hourly_kwh
    FROM statistics s
    JOIN statistics_meta m ON s.metadata_id = m.id
    WHERE m.statistic_id = '{ENTITY}'
      AND s.start_ts >= UNIX_TIMESTAMP('{YEAR}-01-01 00:00:00')
      AND s.start_ts <  UNIX_TIMESTAMP('{YEAR+1}-01-01 00:00:00')
) x
WHERE hourly_kwh IS NOT NULL
ORDER BY hour
"""

df = pd.read_sql(query, conn)
conn.close()

df.to_csv(f"energy_hourly_{YEAR}.csv", index=False)

print("rows:", len(df))
print(df.head())