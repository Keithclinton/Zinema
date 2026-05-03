import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os

from shared.redis_utils import cache_get, cache_incr, cache_set

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        key = f"ratelimit:{client_ip}"
        reqs = cache_get(key)
        if reqs is None:
            cache_set(key, "1", ttl=self.window_seconds)
        else:
            reqs = int(reqs)
            if reqs >= self.max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            cache_incr(key)
        response = await call_next(request)
        return response
