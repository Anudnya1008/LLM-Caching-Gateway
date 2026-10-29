from fastapi import FastAPI, Query
from cache import gete_cached_response, set_cached_response
from llm_service import generate_llm_response
from cache import increment_metric, get_cache_metrics
import time
from rate_limiter import check_rate_limiter
from fastapi import Request, HTTPException
from semantic_cache import (
    find_semantic_match,
    store_semantic_response
)
from kafka_producer import publish_event
app = FastAPI(title="LLM Cache Gateway")

@app.get("/")
def home():
    return {"message":"LLM Cache Gateway is running"}

@app.get("/ask")
def ask_llm(request: Request, question:str = Query(min_length=1)):
    start_time = time.perf_counter()

    client_id = request.client.host if request.client else "unknown"

    rate_limit = check_rate_limiter(client_id)

    if not rate_limit["allowed"]:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    
    cached_response = gete_cached_response(question)
    if cached_response is not None:
        increment_metric("cache_hits")
        response_time = (time.perf_counter() - start_time) * 1000
        publish_event("exact_cache_hit", response_time)
        return {
            "question": question,
            "answer": cached_response,
            "source": "cache"
        }
    increment_metric("cache_misses")
    semantic_response = find_semantic_match(question)

    if semantic_response is not None:

        increment_metric("semantic_hits")

        # Save as exact match for future requests
        set_cached_response(question, semantic_response)

        response_time = (time.perf_counter() - start_time) * 1000
        publish_event("semantic_cache_hit", response_time)
        return {
            "question": question,
            "answer": semantic_response,
            "source": "semantic_cache",
            "response_time_ms": round(response_time, 2)
        }

    response = generate_llm_response(question)

    set_cached_response(question, response)

    store_semantic_response(question, response)

    response_time = (time.perf_counter() - start_time) * 1000
    publish_event("llm_call", response_time)
    return {
        "question": question,
        "answer": response,
        "source": "llm",
        "response_time_ms": round(response_time, 2)
    }