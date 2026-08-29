import logging
import sys
import time
import threading
from collections import defaultdict
from typing import Dict, List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("edumanage.access")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging once at startup."""
    if logging.getLogger().handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logging.basicConfig(level=level, handlers=[handler])


class RateLimiter:
    """
    Sliding-window token rate limiter per client IP address.
    Thread-safe, high-performance, with memory leak protection via periodic cleanup.
    """

    def __init__(self, requests_per_second: int = 100, window_seconds: float = 1.0):
        self.limit = requests_per_second
        self.window = window_seconds
        self._history: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.RLock()
        self._last_cleanup = time.time()

    def is_allowed(self, client_ip: str) -> Tuple[bool, int, int]:
        now = time.time()
        with self._lock:
            # Clean up stale IP records every 60 seconds
            if now - self._last_cleanup > 60:
                self._cleanup_stale_ips(now)

            window_start = now - self.window
            timestamps = [t for t in self._history[client_ip] if t > window_start]
            self._history[client_ip] = timestamps

            count = len(timestamps)
            if count >= self.limit:
                remaining = 0
                reset_after = max(1, int(self.window - (now - timestamps[0])))
                return False, remaining, reset_after

            timestamps.append(now)
            remaining = self.limit - len(timestamps)
            return True, remaining, 1

    def _cleanup_stale_ips(self, now: float) -> None:
        window_start = now - self.window
        stale_ips = [
            ip for ip, timestamps in self._history.items()
            if not timestamps or timestamps[-1] < window_start
        ]
        for ip in stale_ips:
            del self._history[ip]
        self._last_cleanup = now


GLOBAL_RATE_LIMITER = RateLimiter(requests_per_second=100, window_seconds=1.0)


class APIRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Production-oriented rate limiting middleware protecting financial & auth endpoints
    from flooding, brute force, and automated DDoS attacks.
    Enforces a global 100 req/sec limit per IP.
    """

    EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.EXEMPT_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        # Extract client IP supporting reverse proxies
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.headers.get("x-real-ip") or (
                request.client.host if request.client else "127.0.0.1"
            )

        allowed, remaining, retry_after = GLOBAL_RATE_LIMITER.is_allowed(client_ip)

        if not allowed:
            logger.warning("Rate limit exceeded for IP %s on path %s", client_ip, request.url.path)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Maximum 100 requests per second allowed per IP.",
                    "error": "rate_limit_exceeded",
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": "100",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = "100"
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request with method, path, status, duration, and client IP."""

    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        client = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s%s | status=%s | %.2fms | client=%s",
                method,
                path,
                f"?{query}" if query else "",
                response.status_code,
                duration_ms,
                client,
            )
            return response
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "%s %s%s | failed | %.2fms | client=%s",
                method,
                path,
                f"?{query}" if query else "",
                duration_ms,
                client,
            )
            raise


def setup_middleware(app: FastAPI) -> None:
    """Register all application middleware (order: last added runs first)."""
    configure_logging()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(APIRateLimitMiddleware)
