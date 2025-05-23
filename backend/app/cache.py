# backend/app/cache.py
import redis
import json
import os

# --- Get Redis Connection Details ONLY from Environment ---
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT_STR = os.getenv('REDIS_PORT')
REDIS_DB_STR = os.getenv('REDIS_DB')

# --- Fail Fast if Not Set ---
if not all([REDIS_HOST, REDIS_PORT_STR, REDIS_DB_STR]):
    raise ValueError("FATAL ERROR: REDIS_HOST, REDIS_PORT, or REDIS_DB "
                     "environment variables are not set. "
                     "Ensure they are set in your Kubernetes manifests "
                     "or system environment.")

try:
    REDIS_PORT = int(REDIS_PORT_STR)
    REDIS_DB = int(REDIS_DB_STR)
except ValueError:
    raise ValueError("FATAL ERROR: REDIS_PORT and REDIS_DB must be integers.")

print(f"Attempting to connect to Redis at {REDIS_HOST}:{REDIS_PORT}...")

# Create a Redis connection pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_redis_connection():
    """Provides a Redis connection from the pool."""
    try:
        r = redis.Redis(connection_pool=redis_pool)
        r.ping()
        print(f"Redis connection successful to {REDIS_HOST}:{REDIS_PORT}!")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}: {e}")
        return None

def get_cache(r: redis.Redis, key: str):
    """Gets a value from Redis cache."""
    if not r: return None
    value = r.get(key)
    return json.loads(value) if value else None

def set_cache(r: redis.Redis, key: str, value, ttl_seconds: int = 3600):
    """Sets a value in Redis cache with a TTL."""
    if not r: return
    r.setex(key, ttl_seconds, json.dumps(value))