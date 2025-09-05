"""
Utility modules for the backend application
"""

from .error_handling import (
    APIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    DatabaseError,
    handle_database_error,
    safe_db_operation,
    rollback_on_error,
    log_and_raise,
    validate_required_fields,
    sanitize_error_message,
    create_error_response
)

from .validation import (
    validate_email,
    validate_uuid,
    validate_username,
    validate_password_strength,
    sanitize_input,
    validate_tool_name,
    validate_target,
    validate_severity,
    validate_json_size,
    validate_file_upload,
    validate_pagination,
    validate_date_range,
    validate_search_query,
    validate_sort_field,
    validate_sort_order
)

__all__ = [
    # Error handling
    "APIError",
    "ValidationError", 
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "DatabaseError",
    "handle_database_error",
    "safe_db_operation",
    "rollback_on_error",
    "log_and_raise",
    "validate_required_fields",
    "sanitize_error_message",
    "create_error_response",
    
    # Validation
    "validate_email",
    "validate_uuid",
    "validate_username",
    "validate_password_strength",
    "sanitize_input",
    "validate_tool_name",
    "validate_target",
    "validate_severity",
    "validate_json_size",
    "validate_file_upload",
    "validate_pagination",
    "validate_date_range",
    "validate_search_query",
    "validate_sort_field",
    "validate_sort_order"
]
