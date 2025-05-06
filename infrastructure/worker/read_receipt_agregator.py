import json, collections, time
from kafka import KafkaConsumer, KafkaProducer
from uuid import UUID

consumer = KafkaConsumer(
    "message_reads",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda b: json.loads(b.decode()),
    group_id="read-agg",
)
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda d: json.dumps(d).encode(),
)

# In‑memory buckets  -> {message_id: {user_ids}}
bucket: dict[UUID, set[UUID]] = collections.defaultdict(set)
FLUSH_INTERVAL = 5  # seconds

last_flush = time.time()
for msg in consumer:
    data = msg.value
    bucket[UUID(data["message_id"])].add(UUID(data["reader_id"]))

    if time.time() - last_flush > FLUSH_INTERVAL:
        for mid, readers in bucket.items():
            producer.send(
                "aggregated_reads",
                {"message_id": str(mid), "readers": [str(u) for u in readers]},
            )
        bucket.clear()
        producer.flush()
        last_flush = time.time()
