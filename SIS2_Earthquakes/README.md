# SIS 2: Earthquake Data Pipeline

A Python data collection and preparation project that retrieves earthquake records from the **USGS Earthquake API**, publishes them to **Apache Kafka**, validates them with **Pandera**, cleans and transforms them with **pandas** and **NumPy**, stores them in **SQLite3**, and creates three **Matplotlib** charts.

## Pipeline

```text
USGS Earthquake API
        |
        v
Kafka Producer -> Kafka topic: earthquakes -> Kafka Consumer
                                               |
                                               v
                                       Pandera Validation
                                               |
                                               v
                                    pandas / NumPy Cleaning
                                               |
                                               v
                                           SQLite3
                                               |
                                               v
                                     EDA + Matplotlib Charts
```

Each run processes **300 earthquake records**. Because the USGS feed updates continuously, the results can change between runs.

## Data source

- Provider: [United States Geological Survey (USGS)](https://earthquake.usgs.gov/)
- API endpoint: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson`
- Format: GeoJSON, retrieved with an HTTP GET request
- Sample selection: the first 300 features of the response
- Fields: event ID, magnitude, location description, time, status, event type, longitude, latitude, and depth
- Data preservation: the original API response is saved to `data/raw_data.json`

## Project structure

```text
SIS2_Earthquakes/
├── main.py                    # Runs and checks the entire pipeline
├── requirements.txt           # Python dependencies
├── README.md
├── src/
│   ├── __init__.py
│   ├── api_client.py           # Collects USGS earthquake data
│   ├── producer.py             # Publishes records to Kafka with a batch ID
│   ├── consumer.py             # Reads records from the matching Kafka batch
│   ├── validator.py            # Pandera validation and invalid-record tests
│   ├── cleaner.py              # Cleaning, NumPy, filtering, GroupBy, pivot
│   ├── loader.py               # SQLite3 loading and idempotency check
│   └── analysis.py             # EDA and three figures
├── data/                       # Generated JSON, CSV, database, and run statistics
├── figures/                    # Generated PNG charts
├── docs/
│   └── data_dictionary.md
└── report/                     # Project report
```

## Requirements

- Python **3.14** (version used for development)
- Docker Desktop with Docker engine running
- Internet access to reach the USGS API
- Available local port **9092** for Kafka

Python dependencies are listed in `requirements.txt`.

## 1. Install Python dependencies

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## 2. Start Apache Kafka

**First-time setup:** start Docker Desktop, then create the Kafka container:

```bash
docker run -d \
  --name sis2-kafka \
  -p 9092:9092 \
  apache/kafka:4.2.2
```

Create the Kafka topic after the broker has started:

```bash
docker exec sis2-kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --create \
  --topic earthquakes \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

**Later runs:** if the container already exists but is stopped, restart it instead of creating another one:

```bash
docker start sis2-kafka
```

Check that the broker and topic are available:

```bash
docker ps
docker exec sis2-kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
```

The topic list should include `earthquakes`. Create the topic **only once**; running the creation command again on an existing topic will return an error.

## 3. Run the complete pipeline

```bash
python3 main.py
```

`main.py` executes these modules in order:

1. `src.producer`
2. `src.consumer`
3. `src.validator`
4. `src.cleaner`
5. `src.loader`
6. `src.analysis`

Execution stops if a stage exits with an error. The final verification displays the record counts for collection, Kafka delivery and consumption, validation, cleaning, SQLite3 storage, and generated figures.

The tested workflow resets the database for a fresh pipeline run; the loader also verifies duplicate prevention by attempting to insert the same records twice. When the database is preserved between runs instead, its total row count may exceed the number of records in the current batch.

## 4. Run stages individually

Run these commands **in order**, after starting Kafka:

```bash
python3 -m src.producer
python3 -m src.consumer
python3 -m src.validator
python3 -m src.cleaner
python3 -m src.loader
python3 -m src.analysis
```

The consumer uses the producer's batch ID, so the producer should be run before the consumer.

## Validation

Pandera checks the dataset **before** the main cleaning and transformation stage. Checks include required fields, uniqueness, numeric bounds, permitted status values, and timestamp restrictions.

The validator also tests deliberately invalid records to demonstrate error detection. These test records do **not** enter the final processed dataset.

## Cleaning and transformation

The pipeline checks missing values and duplicate event IDs, converts timestamps to UTC datetimes, normalizes text, and performs NumPy calculations. It also demonstrates multi-condition filtering, `groupby()` aggregation, and `pivot_table()` reshaping.

`magnitude_group` is derived as either `Below M3` or `M3+`.

## SQLite3 and idempotency

The database is `data/earthquakes.db`, with an `earthquakes` table containing 11 columns. The `id` column is the primary key.

The loader uses `INSERT ... ON CONFLICT(id) DO NOTHING` and inserts the same dataset twice. It checks that the number of rows stays unchanged, the stored records are identical before and after the second insertion, and no duplicate IDs exist.

## Analysis and figures

The analysis reads the stored records from SQLite3, reports descriptive and grouped statistics, and creates:

| File | Purpose |
|---|---|
| `figures/magnitude_distribution.png` | Histogram of earthquake magnitudes |
| `figures/status_distribution.png` | Counts of automatic versus reviewed events |
| `figures/depth_vs_magnitude.png` | Scatter plot of earthquake depth and magnitude |

Open the figures on macOS with:

```bash
open figures/
```

## Generated outputs

| File | Created by |
|---|---|
| `data/raw_data.json` | API client |
| `data/batch_id.txt`, `data/producer_stats.json` | Producer |
| `data/consumed_data.json` | Consumer |
| `data/validated_data.json`, `data/invalid_data.json` | Validator |
| `data/cleaned_data.csv` | Cleaner |
| `data/earthquakes.db` | Loader |
| `figures/*.png` | Analysis |

A description of each database field is available in `docs/data_dictionary.md`.

## Pipeline verification

Example results from a successful run on **24 November 2026**:

```text
Collected records: 300
Kafka messages delivered: 300
Kafka messages consumed (matching batch): 300
Valid records: 300
Invalid records: 0
Cleaned records: 300
Current-batch records in SQLite: 300
Total rows in SQLite: 300
Visualizations: 3
Collection and Kafka counts match
Valid + invalid records equal consumed records
All cleaned records are stored in SQLite
```

The consumer may skip retained messages from older runs. A unique `batch_id` identifies each producer run, allowing the consumer to count only the corresponding messages. The ID is removed before validation and storage.

Since USGS data is live, the exact earthquake data, statistics, and counts of valid records can differ on later runs. The final checks should be interpreted using the reported counts from the same batch.

## References

- [USGS GeoJSON feeds](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [Confluent Kafka Python client](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html)
- [Pandera documentation](https://pandera.readthedocs.io/)
- [pandas documentation](https://pandas.pydata.org/docs/)
- [NumPy documentation](https://numpy.org/doc/)
- [SQLite documentation](https://www.sqlite.org/docs.html)
- [Matplotlib documentation](https://matplotlib.org/stable/)
