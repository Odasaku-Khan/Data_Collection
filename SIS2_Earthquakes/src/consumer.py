import json
from confluent_kafka import Consumer, KafkaError

with open("data/batch_id.txt", "r") as file:
    expected_batch_id = file.read().strip()

print("Expected batch:", expected_batch_id)

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "sis2-consumer-test-1",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
})

consumer.subscribe(["earthquakes"])

records = []
received = 0
skipped = 0
empty_polls = 0
max_empty_polls = 30

while received < 300:
    message = consumer.poll(1.0)

    if message is None:
        empty_polls = empty_polls + 1
        if empty_polls >= max_empty_polls:
            print("Timeout: no new messages")
            break
        continue

    if message.error():
        if message.error().code() == KafkaError._PARTITION_EOF:
            continue
        print("Kafka error:", message.error())
        break

    try:
        record = json.loads(message.value().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        print("Invalid message:", error)
        continue

    if record.get("batch_id") != expected_batch_id:
        skipped = skipped + 1
        empty_polls = 0
        continue

    del record["batch_id"]

    records.append(record)
    received = received + 1
    empty_polls = 0

consumer.close()
print("Skipped messages from other batches:", skipped)
print("Received records:", len(records))

with open("data/consumed_data.json", "w") as file:
    json.dump(records, file, indent=2)

print("Consumer data saved")