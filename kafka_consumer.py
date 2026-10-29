import json
from confluent_kafka import Consumer, KafkaException

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "llm-analytics-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
})

consumer.subscribe(["llm-gateway-events"])

analytics = {
    "total_requests": 0,
    "exact_cache_hits": 0,
    "semantic_cache_hits": 0,
    "llm_calls": 0,
    "total_response_time": 0.0
}

print("Kafka consumer started. Waiting for events...", flush=True)

try:
    while True:
        message = consumer.poll(1.0)

        if message is None:
            continue

        if message.error():
            raise KafkaException(message.error())

        event = json.loads(message.value().decode("utf-8"))

        event_type = event["event_type"]
        response_time = event["response_time_ms"]

        analytics["total_requests"] += 1
        analytics["total_response_time"] += response_time

        if event_type == "exact_cache_hit":
            analytics["exact_cache_hits"] += 1

        elif event_type == "semantic_cache_hit":
            analytics["semantic_cache_hits"] += 1

        elif event_type == "llm_call":
            analytics["llm_calls"] += 1

        total = analytics["total_requests"]

        cache_hits = (
            analytics["exact_cache_hits"]
            + analytics["semantic_cache_hits"]
        )

        cache_hit_rate = (cache_hits / total) * 100
        avg_response_time = analytics["total_response_time"] / total

        print("\n------ LLM Gateway Analytics ------")
        print(f"Total Requests: {total}")
        print(f"Exact Cache Hits: {analytics['exact_cache_hits']}")
        print(f"Semantic Cache Hits: {analytics['semantic_cache_hits']}")
        print(f"Gemini API Calls: {analytics['llm_calls']}")
        print(f"Cache Hit Rate: {cache_hit_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.2f} ms")
        print("-----------------------------------")

        # Commit only after successfully processing the event.
        consumer.commit(message=message, asynchronous=False)

except KeyboardInterrupt:
    print("\nStopping Kafka consumer...")

finally:
    consumer.close()