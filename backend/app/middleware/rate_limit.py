import time

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SimpleRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 120, per_seconds: int = 60):
        super().__init__(app)
        self.calls = calls
        self.per = per_seconds
        self.state: dict[str, tuple[float, int]] = {}

    async def dispatch(self, request: Request, call_next):
        identifier = request.client.host if request.client else "unknown"
        now = time.time()
        reset, count = self.state.get(identifier, (now + self.per, 0))
        if now > reset:
            reset = now + self.per
            count = 0
        count += 1
        self.state[identifier] = (reset, count)
        if count > self.calls:
            return Response("Too Many Requests", status_code=429)
        return await call_next(request)
