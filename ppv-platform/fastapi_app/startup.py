from fastapi import FastAPI
from rate_limit import RateLimitMiddleware

def setup_middlewares(app: FastAPI):
    app.add_middleware(RateLimitMiddleware, max_requests=20, window_seconds=60)
