import json

from shared.redis_utils import cache_get, cache_set

def cache_token(token, data, ttl):
    cache_set(f"ppv:token:{token}", json.dumps(data), ttl=ttl)

def get_token(token):
    val = cache_get(f"ppv:token:{token}")
    if val:
        return json.loads(val)
    return None
