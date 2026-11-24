import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("data/earthquakes.db")

df = pd.read_sql_query(
    "SELECT * FROM earthquakes",
    conn
)

conn.close()

print("Dataset shape:", df.shape)
print(df.dtypes)
print(df.describe())

print("\nEarthquakes by status:")
print(df["status"].value_counts())

print("\nMagnitude groups:")
print(df["magnitude_group"].value_counts())

small = (df["magnitude"] < 3).sum()
print("\nMagnitude below 3:", small, "of", len(df))
print("Share below 3 (%):", round(small / len(df) * 100, 1))

print("\nAverage magnitude by status:")
print(df.groupby("status")["magnitude"].mean())

Path("figures").mkdir(exist_ok=True)

# Chart 1: magnitude histogram
plt.figure(figsize=(8, 5))
plt.hist(df["magnitude"], bins=20, edgecolor="black")
plt.title("Earthquake Magnitude Distribution")
plt.xlabel("Magnitude")
plt.ylabel("Number of Earthquakes")
plt.tight_layout()
plt.savefig("figures/magnitude_distribution.png")
plt.close()

# Chart 2: status bar chart
status_counts = df["status"].value_counts()

plt.figure(figsize=(8, 5))
plt.bar(status_counts.index, status_counts.values, edgecolor="black")
plt.title("Earthquakes by Review Status")
plt.xlabel("Status")
plt.ylabel("Number of Earthquakes")
plt.tight_layout()
plt.savefig("figures/status_distribution.png")
plt.close()

# Chart 3: depth vs magnitude scatter plot
plt.figure(figsize=(8, 5))
plt.scatter(df["depth_km"], df["magnitude"], alpha=0.6)
plt.title("Depth vs Magnitude")
plt.xlabel("Depth (km)")
plt.ylabel("Magnitude")
plt.tight_layout()
plt.savefig("figures/depth_vs_magnitude.png")
plt.close()

print("\nFigures saved")