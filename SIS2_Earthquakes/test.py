from src.api_client import collect_earthquakes

df = collect_earthquakes()

print("Shape:", df.shape)
print(df.head())