import logging
import sys
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

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
