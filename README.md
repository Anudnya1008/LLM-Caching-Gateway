
# LLM Cache Gateway

A distributed backend API built using Python, FastAPI, Redis, and Apache Kafka to reduce redundant LLM requests, improve response times, and handle concurrent API traffic efficiently.

## Tech Stack
Python, FastAPI, Redis, Apache Kafka, Sentence Transformers, Gemini API, Docker, Locust

## Features
- **Exact Caching:** Uses SHA-256 keys to cache identical requests.
- **Semantic Caching:** Uses Sentence Transformers to identify and reuse responses for similar queries.
- **Cache Expiration:** Redis TTL-based cache management.
- **Rate Limiting:** IP-based request throttling using Redis.
- **Cache Stampede Prevention:** Distributed locking to prevent concurrent requests from triggering redundant LLM calls.
- **Kafka Integration:** Asynchronous event streaming for API usage tracking, cache events, and analytics.
- **Fault Tolerance:** Exponential backoff and retries for temporary LLM API failures.
- **Monitoring:** Cache hit, miss, and semantic hit metrics.
- **Performance Testing:** Locust-based load testing to measure latency, throughput, and concurrency.

## Running Locally
1. Clone the repository.
2. Install Python dependencies.
3. Start Redis and Kafka using Docker.
4. Configure the Gemini API key.
5. Start the FastAPI application.
6. Open `/docs` to test API endpoints.

## Future Improvements
- Cloud deployment on AWS or GCP
- Advanced monitoring and observability
- Redis caching performance optimization
