"""
Security Headers Middleware for FastAPI

This middleware adds essential security headers to all HTTP responses,
following enterprise-grade security practices used by major companies.

Security Headers Implemented:
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- Content-Security-Policy (CSP)
- Referrer-Policy
- Permissions-Policy
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.
    
    This middleware implements the security headers recommended by OWASP
    and used by major enterprise applications to protect against:
    - Clickjacking attacks
    - XSS attacks
    - MIME type sniffing attacks
    - Protocol downgrade attacks
    - Information leakage
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Define security headers with their values
        self.security_headers = {
            # HTTP Strict Transport Security (HSTS)
            # Forces browsers to use HTTPS for 1 year, including subdomains
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Prevents MIME type sniffing attacks
            # Browsers won't try to guess content types
            "X-Content-Type-Options": "nosniff",
            
            # Prevents clickjacking attacks
            # Prevents the page from being embedded in frames/iframes
            "X-Frame-Options": "DENY",
            
            # Content Security Policy (CSP)
            # Comprehensive XSS protection by controlling resource loading
            "Content-Security-Policy": (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "script-src 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            
            # Controls referrer information leakage
            # Only sends referrer for same-origin requests
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Disables sensitive browser features by default
            # Prevents unauthorized access to camera, microphone, etc.
            "Permissions-Policy": (
                "geolocation=(), "
                "midi=(), "
                "camera=(), "
                "microphone=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=(self), "
                "payment=()"
            ),
            
            # Additional security headers for enhanced protection
            "X-XSS-Protection": "1; mode=block",
            "X-Download-Options": "noopen",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add security headers to the response.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware/handler in the chain
            
        Returns:
            Response with security headers added
        """
        # Record start time for performance monitoring
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers to the response
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        # Add performance header (optional)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add server identification (optional - can be customized)
        response.headers["Server"] = "PentoraSec-API/1.0"
        
        return response


def create_security_headers_middleware(app):
    """
    Factory function to create and configure the security headers middleware.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Configured SecurityHeadersMiddleware instance
    """
    return SecurityHeadersMiddleware(app)


# Alternative implementation for more granular control
class ConfigurableSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Configurable version of the security headers middleware.
    Allows customization of security headers based on environment or requirements.
    """
    
    def __init__(self, app, custom_headers: dict = None, exclude_paths: list = None):
        super().__init__(app)
        
        # Default security headers
        self.default_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "script-src 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), "
                "midi=(), "
                "camera=(), "
                "microphone=()"
            )
        }
        
        # Merge with custom headers if provided
        self.security_headers = {**self.default_headers}
        if custom_headers:
            self.security_headers.update(custom_headers)
        
        # Paths to exclude from security headers (e.g., health checks)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with configurable security headers."""
        
        # Check if path should be excluded
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        return response
