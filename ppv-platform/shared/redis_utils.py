import json
import os
import threading
import time

import redis

REDIS_URL = os.getenv('REDIS_URL')

_memory_store = {}
_memory_lock = threading.Lock()


def _create_redis_client():
    if not REDIS_URL:
        return None
    try:
        return redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    except Exception:
        return None


redis_client = _create_redis_client()


def _memory_set(key, value, ttl=None):
    expires_at = time.time() + ttl if ttl else None
    with _memory_lock:
        _memory_store[key] = (value, expires_at)


def _memory_get(key):
    with _memory_lock:
        item = _memory_store.get(key)
        if not item:
            return None
        value, expires_at = item
        if expires_at is not None and time.time() >= expires_at:
            _memory_store.pop(key, None)
            return None
        return value


def _memory_incr(key):
    with _memory_lock:
        value, expires_at = _memory_store.get(key, ("0", None))
        try:
            next_value = int(value) + 1
        except (TypeError, ValueError):
            next_value = 1
        _memory_store[key] = (str(next_value), expires_at)
        return next_value


def cache_set(key, value, ttl=None):
    if redis_client is not None:
        try:
            redis_client.set(key, value, ex=ttl)
            return
        except Exception:
            pass
    _memory_set(key, value, ttl=ttl)


def cache_get(key):
    if redis_client is not None:
        try:
            value = redis_client.get(key)
            if value is not None:
                return value
        except Exception:
            pass
    return _memory_get(key)


def cache_incr(key):
    if redis_client is not None:
        try:
            return redis_client.incr(key)
        except Exception:
            pass
    return _memory_incr(key)


def cache_token(token, data, ttl):
    cache_set(f"ppv:token:{token}", json.dumps(data), ttl=ttl)


def get_token(token):
    val = cache_get(f"ppv:token:{token}")
    if val:
        return json.loads(val)
    return None


def atomic_increment_usage(token):
    key = f"ppv:token:{token}:used_count"
    return cache_incr(key)
