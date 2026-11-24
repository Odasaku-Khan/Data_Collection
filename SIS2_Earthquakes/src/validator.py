import json
import pandas as pd
import pandera.pandas as pa

with open("data/consumed_data.json", "r") as file:
    records = json.load(file)

df = pd.DataFrame(records)

print("Records:", len(df))
print(df.dtypes)

schema = pa.DataFrameSchema({
    "id": pa.Column(str, nullable=False, unique=True),
    "magnitude": pa.Column(float, pa.Check.between(-2, 10)),
    "place": pa.Column(str, nullable=False),
    "time_ms": pa.Column(int, pa.Check.gt(0)),
    "status": pa.Column(str, pa.Check.isin(["automatic", "reviewed"])),
    "event_type": pa.Column(str, nullable=False),
    "latitude": pa.Column(float, pa.Check.between(-90, 90)),
    "longitude": pa.Column(float, pa.Check.between(-180, 180)),
    "depth_km": pa.Column(float, pa.Check.between(-10, 800))
})

try:
    schema.validate(df, lazy=True)
    invalid_index = []
    print("Validation passed")

except pa.errors.SchemaErrors as error:
    print("Validation errors:")
    print(error.failure_cases)

    no_index = error.failure_cases["index"].isna().sum()
    if no_index > 0:
        raise SystemExit("Column-level failure (type or missing column)")

    invalid_index = error.failure_cases["index"].astype(int).unique().tolist()

invalid_df = df.loc[invalid_index]
validated_df = df.drop(index=invalid_index)

print("Valid records:", len(validated_df))
print("Invalid real records:", len(invalid_df))

validated_df.to_json(
    "data/validated_data.json",
    orient="records",
    date_format="iso"
)

invalid_df.to_json(
    "data/invalid_data.json",
    orient="records",
    date_format="iso"
)

test_df = df.head(5).copy()

test_df.loc[0, "latitude"] = 150
test_df.loc[1, "longitude"] = 250
test_df.loc[2, "id"] = None
test_df.loc[3, "magnitude"] = 15
test_df.loc[4, "status"] = "unknown"

try:
    schema.validate(test_df, lazy=True)
    print("All test records passed")

except pa.errors.SchemaErrors as error:
    print("Invalid test records detected:")
    print(error.failure_cases)