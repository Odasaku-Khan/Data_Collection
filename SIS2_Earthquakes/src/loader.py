import sqlite3
import pandas as pd

df = pd.read_csv("data/cleaned_data.csv")
print("CSV records:", len(df))
print(df.columns.tolist())

conn = sqlite3.connect("data/earthquakes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS earthquakes (
    id TEXT PRIMARY KEY,
    magnitude REAL,
    place TEXT,
    time_ms INTEGER,
    status TEXT,
    event_type TEXT,
    longitude REAL,
    latitude REAL,
    depth_km REAL,
    event_time TEXT,
    magnitude_group TEXT
)
""")

columns = list(df.columns)
print("Number of columns:", len(columns))

column_names = ", ".join(columns)
placeholders = ", ".join(["?"] * len(columns))

insert_sql = (
    "INSERT INTO earthquakes (" + column_names + ") "
    "VALUES (" + placeholders + ") "
    "ON CONFLICT(id) DO NOTHING"
)
print(insert_sql)

rows = list(df.itertuples(index=False, name=None))
print("Rows ready:", len(rows))

cursor.executemany(insert_sql, rows)
conn.commit()

cursor.execute("SELECT * FROM earthquakes ORDER BY id")
before = cursor.fetchall()
print("Before second load:", len(before))

cursor.execute("SELECT COUNT(*) FROM earthquakes")
print("Stored records:", cursor.fetchone()[0])

cursor.executemany(insert_sql, rows)
conn.commit()

cursor.execute("""
SELECT id, COUNT(*)
FROM earthquakes
GROUP BY id
HAVING COUNT(*) > 1
""")
duplicates = cursor.fetchall()
print("Duplicate IDs:", duplicates)

cursor.execute("SELECT * FROM earthquakes ORDER BY id")
after = cursor.fetchall()

print("After second load:", len(after))
print("Data unchanged:", before == after)

conn.close()