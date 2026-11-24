import json
import numpy as np
import pandas as pd

with open("data/validated_data.json", "r") as file:
    records = json.load(file)

df = pd.DataFrame(records)

print(df.shape)
print(df.isnull().sum())
print("Duplicate IDs:", df.duplicated(subset=["id"]).sum())

print("Before:", df["event_time"].dtype)

df["event_time"] = pd.to_datetime(
    df["event_time"],
    utc=True,
    errors="coerce"
)

df = df.drop_duplicates(subset=["id"]).copy()

df["place"] = df["place"].str.strip()
df["status"] = df["status"].str.strip().str.lower()

print("Records after cleaning:", len(df))
print("Average magnitude:", np.mean(df["magnitude"]))
print("Median magnitude:", np.median(df["magnitude"]))
print("Maximum depth:", np.max(df["depth_km"]))
print("After:", df["event_time"].dtype)
print("NaT values:", df["event_time"].isna().sum())
print(df["event_time"].head())

df["magnitude_group"] = np.where(
    df["magnitude"] >= 3,
    "M3+",
    "Below M3"
)

print(df["magnitude_group"].value_counts())

filtered = df[
    (df["magnitude"] >= 2) &
    (df["depth_km"] > 10)
]

print("Filtered earthquakes:", len(filtered))

grouped = df.groupby("status")["magnitude"].agg(["count", "mean"])

print("\nEarthquakes by status:")
print(grouped)


pivot = df.pivot_table(
    index="status",
    columns="magnitude_group",
    values="id",
    aggfunc="count",
    fill_value=0
)

print("\nMagnitude distribution by status:")
print(pivot)

df.to_csv("data/cleaned_data.csv", index=False)

print("\nCleaned dataset saved")
print("Final records:", len(df))



