import time
from cache import redis_client

BUCKET_CAPACITY = 3
REFILL_RATE = 1/12

TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

local bucket = redis.call("HMGET", key, "tokens", "last_refill")

local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_refill = current_time
end

local elapsed = math.max(0, current_time - last_refill)

tokens = math.min(
    capacity,
    tokens + elapsed * refill_rate
)

local allowed = 0

if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

redis.call(
    "HSET",
    key,
    "tokens", tokens,
    "last_refill", current_time
)

local ttl = math.ceil(capacity / refill_rate) + 1
redis.call("EXPIRE", key, ttl)

return {allowed, math.floor(tokens)}
"""

token_bucket = redis_client.register_script(TOKEN_BUCKET_SCRIPT)
def check_rate_limiter(client_id:str):
    key = f"rate_limit:{client_id}"
    result = token_bucket(
        keys=[key],
        args=[
            BUCKET_CAPACITY,
            REFILL_RATE,
            time.time()
        ]
    )

    return {
        "allowed": bool(result[0]),
        "remaining_tokens": result[1]
    }
