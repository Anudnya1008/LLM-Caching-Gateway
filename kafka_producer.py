import json
import logging
from datetime import datetime, timezone

from confluent_kafka import Producer

logger = logging.getLogger(__name__)

KAFKA_TOPIC = "llm-gateway-events"

producer = Producer({
    "bootstrap.servers": "localhost:9092",
    "client.id": "llm-cache-gateway",
    "message.timeout.ms": 5000
})


def delivery_report(err, msg):
    if err is not None:
        logger.error("Kafka delivery failed: %s", err)


def publish_event(event_type: str, response_time_ms: float):
    event = {
        "event_type": event_type,
        "response_time_ms": round(response_time_ms, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        producer.produce(
            topic=KAFKA_TOPIC,
            value=json.dumps(event).encode("utf-8"),
            callback=delivery_report
        )

        # Process delivery callbacks without waiting for Kafka.
        producer.poll(0)

    except Exception as error:
        logger.warning("Unable to publish Kafka event: %s", error)