"""Simple per-IP token-bucket rate limiter (in-memory; fine for MVP / single instance).

Replace with Redis-backed `redis-cell` or sliding window in prod.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


@dataclass
class _Bucket:
    tokens: float
    updated: float


class TokenBucketMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, capacity: int = 60, refill_per_second: float = 1.0) -> None:
        super().__init__(app)
        self.capacity = capacity
        self.refill = refill_per_second
        self.buckets: dict[str, _Bucket] = defaultdict(lambda: _Bucket(capacity, time.time()))

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self.buckets[ip]
        elapsed = now - bucket.updated
        bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.refill)
        bucket.updated = now
        if bucket.tokens < 1:
            return Response("rate limit exceeded", status_code=429)
        bucket.tokens -= 1
        return await call_next(request)
