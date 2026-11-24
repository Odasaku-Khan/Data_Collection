import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import pandas as pd

stages = [
    "src.producer",
    "src.consumer",
    "src.validator",
    "src.cleaner",
    "src.loader",
    "src.analysis"
]

Path("data").mkdir(exist_ok=True)
Path("figures").mkdir(exist_ok=True)

reset_database = True

if reset_database and os.path.exists("data/earthquakes.db"):
    os.remove("data/earthquakes.db")

for old_figure in Path("figures").glob("*.png"):
    old_figure.unlink()

for stage in stages:
    print("=" * 50)
    print("Running:", stage)
    print("=" * 50)

    result = subprocess.run([sys.executable, "-m", stage])

    if result.returncode != 0:
        print("Stage failed:", stage, "with exit code", result.returncode)
        sys.exit(1)

    print("Finished:", stage)

    
with open("data/producer_stats.json", "r") as file:
    producer_stats = json.load(file)

with open("data/consumed_data.json", "r") as file:
    consumed = json.load(file)

with open("data/validated_data.json", "r") as file:
    validated = json.load(file)

with open("data/invalid_data.json", "r") as file:
    invalid = json.load(file)

cleaned = pd.read_csv("data/cleaned_data.csv")

conn = sqlite3.connect("data/earthquakes.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM earthquakes")
stored_total = cursor.fetchone()[0]

cursor.execute("SELECT id FROM earthquakes")
stored_ids = [row[0] for row in cursor.fetchall()]
conn.close()

current_stored = cleaned["id"].isin(stored_ids).sum()
figures = list(Path("figures").glob("*.png"))

print("=" * 50)
print("PIPELINE VERIFICATION")
print("=" * 50)
print("Batch ID:", producer_stats["batch_id"])
print("Collected records:", producer_stats["collected"])
print("Kafka messages delivered:", producer_stats["delivered"])
print("Kafka messages consumed (matching batch):", len(consumed))
print("Valid records:", len(validated))
print("Invalid records:", len(invalid))
print("Cleaned records:", len(cleaned))
print("Current-batch records in SQLite:", current_stored)
print("Total rows in SQLite:", stored_total)
print("Visualizations:", len(figures))

print("-" * 50)

if producer_stats["collected"] == producer_stats["delivered"] == len(consumed):
    print("Collection and Kafka counts match")
else:
    print("WARNING: collection and Kafka counts differ")

if len(validated) + len(invalid) == len(consumed):
    print("Valid + invalid records equal consumed records")
else:
    print("WARNING: some consumed records are unaccounted for")

if current_stored == len(cleaned):
    print("All cleaned records are stored in SQLite")
else:
    print("WARNING: some cleaned records are missing from SQLite")