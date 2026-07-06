from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.rate_limiter import check_rate_limit
from app.core.config import settings


RATE_LIMITS = {
    "POST:/api/v1/auth/login": (20, 60),
    "POST:/api/v1/auth/signup": (10, 60),
    "POST:/api/v1/auth/forgot-password": (5, 60),
    "POST:/api/v1/resumes/upload": (10, 60),
    "ai": (20, 60),
    "POST:/api/v1/applications": (10, 60),
    "default": (100, 60),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        route_key = f"{request.method}:{request.url.path}"
        limit_config = RATE_LIMITS.get(route_key)

        if route_key.startswith("POST:/api/v1/ai") or route_key.startswith("POST:/ai"):
            limit_config = RATE_LIMITS["ai"]

        if limit_config is None:
            limit_config = RATE_LIMITS["default"]

        max_requests, window = limit_config
        user_key = f"ratelimit:{request.client.host}:{route_key}"

        allowed, remaining, reset_time = await check_rate_limit(
            user_key, max_requests, window
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT",
                        "message": "Too many requests. Please try again later.",
                    },
                },
                headers={
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(window),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        return response
