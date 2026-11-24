import json
from uuid import uuid4
from confluent_kafka import Producer
from src.api_client import collect_earthquakes

producer = Producer({
    "bootstrap.servers": "localhost:9092"
})

df = collect_earthquakes()

records = json.loads(
    df.to_json(orient="records", date_format="iso")
)

print("Records ready:", len(records))

batch_id = str(uuid4())

with open("data/batch_id.txt", "w") as file:
    file.write(batch_id)

print("Batch ID:", batch_id)

for record in records:
    record["batch_id"] = batch_id

print(records[0])

delivery_stats = {"success": 0, "failed": 0}

def delivery_report(err, msg):
    if err is not None:
        delivery_stats["failed"] += 1
        print("Delivery failed:", err)
    else:
        delivery_stats["success"] += 1


for record in records:
    producer.produce(
        topic="earthquakes",
        key=record["id"],
        value=json.dumps(record).encode("utf-8"),
        on_delivery=delivery_report
    )
    producer.poll(0)

remaining = producer.flush()
print("Successfully delivered:", delivery_stats["success"])
print("Failed deliveries:", delivery_stats["failed"])

print("Records queued:", len(records))
print("Undelivered messages:", remaining)

producer_stats = {
    "batch_id": batch_id,
    "collected": len(df),
    "queued": len(records),
    "delivered": delivery_stats["success"],
    "failed": delivery_stats["failed"],
    "undelivered": remaining
}

with open("data/producer_stats.json", "w") as file:
    json.dump(producer_stats, file, indent=2)

print("Producer stats saved")