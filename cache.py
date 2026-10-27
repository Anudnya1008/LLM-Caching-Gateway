import redis
import hashlib

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


def increment_metric(metric_name: str):
    redis_client.incr(f"metrics:{metric_name}")


def get_cache_metrics():
    hits = int(redis_client.get("metrics:cache_hits") or 0)
    misses = int(redis_client.get("metrics:cache_misses") or 0)

    total = hits + misses

    hit_rate = (hits / total * 100) if total > 0 else 0

    return {
        "total_requests": total,
        "cache_hits": hits,
        "cache_misses": misses,
        "cache_hit_rate": round(hit_rate, 2)
    }

def generated_cache_key(question:str):
    normalized_question = question.strip().lower()
    return hashlib.sha256(
        normalized_question.encode()

    ).hexdigest()

def gete_cached_response(question: str):
    key = generated_cache_key(question)
    return redis_client.get(key)

def set_cached_response(question:str, response:str):
    key = generated_cache_key(question)
    redis_client.setex(     #It stores a value with an expiration time.
        key,
        3600,
        response
    )