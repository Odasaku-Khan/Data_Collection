Table `earthquakes` in `data/earthquakes.db` (11 columns).

| Column | SQLite type | Description | Source / rule |
|---|---|---|---|
| id | TEXT (primary key) | Unique USGS event identifier | feature `id`; not null, unique |
| magnitude | REAL | Earthquake magnitude | `properties.mag`; between -2 and 10 |
| place | TEXT | Text description of the location | `properties.place`; not null |
| time_ms | INTEGER | Event time, Unix milliseconds (UTC) | `properties.time`; greater than 0 |
| status | TEXT | Review status of the event | `properties.status`; `automatic` or `reviewed` |
| event_type | TEXT | Type of seismic event | `properties.type`; not null |
| longitude | REAL | Longitude in degrees | `coordinates[0]`; between -180 and 180 |
| latitude | REAL | Latitude in degrees | `coordinates[1]`; between -90 and 90 |
| depth_km | REAL | Depth of the event in kilometers | `coordinates[2]`; between -10 and 800 |
| event_time | TEXT | Event time as an ISO datetime (UTC) | derived from `time_ms` |
| magnitude_group | TEXT | `Below M3` or `M3+` | derived: magnitude below 3 or 3 and above |

Notes:
- The Kafka messages also contain `batch_id`. It is used only to match
  consumer messages to the producer run and is removed before validation.
- Negative magnitudes and slightly negative depths occur in real data, so they
  are allowed by the validation rules.