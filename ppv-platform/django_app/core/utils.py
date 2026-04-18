from django_redis import get_redis_connection
import json

def cache_token(token, data, ttl):
    redis_conn = get_redis_connection()
    redis_conn.set(f"ppv:token:{token}", json.dumps(data), ex=ttl)

def get_token(token):
    redis_conn = get_redis_connection()
    val = redis_conn.get(f"ppv:token:{token}")
    if val:
        return json.loads(val)
    return None
