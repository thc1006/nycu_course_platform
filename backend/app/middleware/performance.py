"""
Performance Middleware for FastAPI.

Provides:
- Response compression (gzip)
- Request rate limiting
- Query timeout handling
- Performance monitoring
"""

import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware

# Configure logging
logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Implements token bucket algorithm for request rate limiting.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            burst_size: Maximum burst requests allowed
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size

        # Storage for rate limit data per IP
        # Format: {ip: {"tokens": float, "last_update": float}}
        self.rate_data = defaultdict(lambda: {
            "tokens": burst_size,
            "last_update": time.time()
        })

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response object
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Update token bucket
        current_time = time.time()
        data = self.rate_data[client_ip]

        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - data["last_update"]
        tokens_to_add = time_elapsed * (self.requests_per_minute / 60.0)

        # Update tokens (capped at burst_size)
        data["tokens"] = min(
            self.burst_size,
            data["tokens"] + tokens_to_add
        )
        data["last_update"] = current_time

        # Check if request is allowed
        if data["tokens"] >= 1:
            # Consume one token
            data["tokens"] -= 1

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(int(data["tokens"]))
            response.headers["X-RateLimit-Reset"] = str(
                int(current_time + (60 - (data["tokens"] / self.requests_per_minute * 60)))
            )

            return response
        else:
            # Rate limit exceeded
            retry_after = int((1 - data["tokens"]) / (self.requests_per_minute / 60.0))

            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}"
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                }
            )


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring middleware.

    Tracks request duration and logs slow queries.
    """

    def __init__(
        self,
        app,
        slow_request_threshold_ms: float = 1000.0,
    ):
        """
        Initialize performance monitor.

        Args:
            app: FastAPI application
            slow_request_threshold_ms: Threshold for logging slow requests (ms)
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold_ms / 1000.0

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process request with performance monitoring.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response object with performance headers
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Add performance headers
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration_ms:.2f}ms"
            )

        # Log all requests
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {duration_ms:.2f}ms"
        )

        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Cache control middleware.

    Adds appropriate cache headers to responses.
    """

    def __init__(
        self,
        app,
        default_max_age: int = 300,  # 5 minutes
    ):
        """
        Initialize cache control.

        Args:
            app: FastAPI application
            default_max_age: Default cache max-age in seconds
        """
        super().__init__(app)
        self.default_max_age = default_max_age

        # Define cache policies for different endpoints
        self.cache_policies = {
            "/api/semesters": 3600,  # 1 hour - semesters rarely change
            "/api/courses": 300,  # 5 minutes
            "/api/courses/search": 300,  # 5 minutes
            "/api/advanced": 300,  # 5 minutes
        }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Add cache control headers to responses.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with cache headers
        """
        response = await call_next(request)

        # Only add cache headers to GET requests
        if request.method == "GET":
            # Find matching cache policy
            max_age = self.default_max_age
            for path_prefix, age in self.cache_policies.items():
                if request.url.path.startswith(path_prefix):
                    max_age = age
                    break

            # Add cache control headers
            response.headers["Cache-Control"] = f"public, max-age={max_age}"
            response.headers["Vary"] = "Accept-Encoding"

        return response


def setup_performance_middleware(app):
    """
    Setup all performance middleware on the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Add gzip compression (should be first to compress other middleware responses)
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # Only compress responses > 1KB
        compresslevel=6,  # Compression level (1-9)
    )

    # Add cache control
    app.add_middleware(
        CacheControlMiddleware,
        default_max_age=300,
    )

    # Add performance monitoring
    app.add_middleware(
        PerformanceMonitoringMiddleware,
        slow_request_threshold_ms=1000.0,
    )

    # Add rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=120,  # Increased for search-heavy workload
        burst_size=20,
    )

    logger.info("Performance middleware configured")
