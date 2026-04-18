import os
import redis
import json

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def cache_token(token, data, ttl):
    redis_client.set(f"ppv:token:{token}", json.dumps(data), ex=ttl)

def get_token(token):
    val = redis_client.get(f"ppv:token:{token}")
    if val:
        return json.loads(val)
    return None

def atomic_increment_usage(token):
    key = f"ppv:token:{token}:used_count"
    return redis_client.incr(key)
