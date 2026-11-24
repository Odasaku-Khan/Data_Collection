def collect_earthquakes():
    import requests
    import json
    from pathlib import Path
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
    
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    
    api_json = response.json()
    records = api_json["features"]
    
    print("Status:", response.status_code)
    print("Total records:", len(records))
    print("First ID:", records[0]["id"])
    print("First magnitude:", records[0]["properties"]["mag"])
    Path("data").mkdir(exist_ok=True)
    
    with open("data/raw_data.json", "w") as file:
        json.dump(api_json, file, indent=2)
    
    selected_records = records[:300]
    
    print("Selected records:", len(selected_records))
    print("Raw JSON saved")
    earthquake = selected_records[0]
    
    print("ID:", earthquake["id"])
    print("Properties:", earthquake["properties"])
    print("Coordinates:", earthquake["geometry"]["coordinates"])
    
    import pandas as pd
    
    rows = []
    
    for earthquake in selected_records:
        properties = earthquake["properties"]
        coordinates = earthquake["geometry"]["coordinates"]
    
        rows.append({
        "id": earthquake["id"],
        "magnitude": properties.get("mag"),
        "place": properties.get("place"),
        "time_ms": properties.get("time"),
        "status": properties.get("status"),
        "event_type": properties.get("type"),
        "longitude": coordinates[0],
        "latitude": coordinates[1],
        "depth_km": coordinates[2]
    })
    
    df = pd.DataFrame(rows)
    
    print(df.head())
    print(df.shape)
    
    df["event_time"] = pd.to_datetime(
        df["time_ms"],
        unit="ms",
        utc=True
    )
    print(df.head())
    print("Shape:", df.shape)
    print("\nData types:")
    print(df.dtypes)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nDuplicate IDs:", df["id"].duplicated().sum())

    return df