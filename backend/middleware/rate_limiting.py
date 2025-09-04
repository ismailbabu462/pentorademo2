"""
Rate Limiting Middleware for FastAPI

This middleware implements rate limiting to prevent API abuse and DoS attacks.
It uses a simple in-memory store for demonstration purposes.
In production, use Redis or similar distributed cache.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
import time
from typing import Dict, Deque
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse.
    
    Features:
    - Per-IP rate limiting
    - Different limits for different endpoints
    - Sliding window algorithm
    - Configurable limits
    """
    
    def __init__(self, app, default_limit: int = 500, window_seconds: int = 60):
        super().__init__(app)
        
        # Rate limiting configuration
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        
        # Endpoint-specific limits (increased for development)
        self.endpoint_limits = {
            "/api/auth/login": 10,      # 10 login attempts per minute
            "/api/auth/register": 5,    # 5 registration attempts per minute
            "/api/ai/chat": 50,         # 50 AI requests per minute
            "/api/tools/": 100,         # 100 tool requests per minute
            "/api/projects": 200,       # 200 project requests per minute
        }
        
        # In-memory store for rate limiting (use Redis in production)
        self.requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request headers."""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def get_rate_limit(self, path: str) -> int:
        """Get rate limit for specific endpoint."""
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit
        return self.default_limit
    
    def is_rate_limited(self, client_ip: str, path: str) -> bool:
        """Check if client is rate limited."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests outside the window
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        # Check if limit exceeded
        limit = self.get_rate_limit(path)
        if len(client_requests) >= limit:
            return True
        
        # Add current request
        client_requests.append(now)
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        client_ip = self.get_client_ip(request)
        path = request.url.path
        
        # Skip rate limiting for health checks and static files
        if path in ["/health", "/metrics"] or path.startswith("/static/"):
            return await call_next(request)
        
        # Check rate limit
        if self.is_rate_limited(client_ip, path):
            logger.warning(f"Rate limit exceeded for IP {client_ip} on path {path}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": self.window_seconds
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        limit = self.get_rate_limit(path)
        remaining = limit - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_seconds))
        
        return response


def create_rate_limit_middleware(app, default_limit: int = 100, window_seconds: int = 60):
    """
    Create and configure rate limiting middleware.
    
    Args:
        app: FastAPI application instance
        default_limit: Default requests per window
        window_seconds: Time window in seconds
    
    Returns:
        Configured RateLimitMiddleware instance
    """
    return RateLimitMiddleware(app, default_limit, window_seconds)
