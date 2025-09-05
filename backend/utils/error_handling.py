"""
Error handling utilities for the backend application
"""

import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)

class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, details)

class ConflictError(APIError):
    """Resource conflict error"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 409, details)

class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 429, details)

class DatabaseError(APIError):
    """Database operation error"""
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

def handle_database_error(error: SQLAlchemyError, operation: str = "database operation") -> None:
    """Handle database errors and convert to appropriate API errors"""
    logger.error(f"Database error during {operation}: {str(error)}")
    
    if "UNIQUE constraint failed" in str(error) or "Duplicate entry" in str(error):
        raise ConflictError(f"Resource already exists", {"operation": operation})
    elif "FOREIGN KEY constraint failed" in str(error):
        raise ValidationError("Invalid reference to related resource", {"operation": operation})
    elif "NOT NULL constraint failed" in str(error):
        raise ValidationError("Required field is missing", {"operation": operation})
    else:
        raise DatabaseError(f"Database {operation} failed")

def safe_db_operation(operation_func, *args, **kwargs):
    """Safely execute database operations with error handling"""
    try:
        return operation_func(*args, **kwargs)
    except SQLAlchemyError as e:
        handle_database_error(e, "operation")
    except Exception as e:
        logger.error(f"Unexpected error during database operation: {str(e)}")
        raise DatabaseError("Unexpected database error occurred")

def rollback_on_error(db: Session) -> None:
    """Safely rollback database transaction on error"""
    try:
        db.rollback()
    except Exception as e:
        logger.error(f"Failed to rollback database transaction: {str(e)}")

def log_and_raise(error: Exception, message: str, status_code: int = 500) -> None:
    """Log error and raise HTTPException"""
    logger.error(f"{message}: {str(error)}")
    raise HTTPException(status_code=status_code, detail=message)

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that all required fields are present and not empty"""
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields or empty_fields:
        error_details = {}
        if missing_fields:
            error_details["missing_fields"] = missing_fields
        if empty_fields:
            error_details["empty_fields"] = empty_fields
        
        raise ValidationError("Required fields are missing or empty", error_details)

def sanitize_error_message(message: str) -> str:
    """Sanitize error messages to prevent information leakage"""
    # Remove potential sensitive information
    sensitive_patterns = [
        r'password[^"]*"[^"]*"',
        r'token[^"]*"[^"]*"',
        r'key[^"]*"[^"]*"',
        r'secret[^"]*"[^"]*"',
    ]
    
    import re
    for pattern in sensitive_patterns:
        message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
    
    return message

def create_error_response(error: Exception, include_details: bool = False) -> Dict[str, Any]:
    """Create standardized error response"""
    if isinstance(error, APIError):
        response = {
            "error": error.message,
            "status_code": error.status_code
        }
        if include_details and error.details:
            response["details"] = error.details
    elif isinstance(error, HTTPException):
        response = {
            "error": error.detail,
            "status_code": error.status_code
        }
    else:
        response = {
            "error": "Internal server error",
            "status_code": 500
        }
        if include_details:
            response["details"] = {"type": type(error).__name__}
    
    return response
