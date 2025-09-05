"""
Validation utilities for the backend application
"""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from config import TOOL_CONFIG, VALIDATION_CONFIG


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format"""
    if not uuid_string or not isinstance(uuid_string, str):
        return False

    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False

    # Username should be 3-50 characters, alphanumeric and underscores only
    if len(username) < 3 or len(username) > VALIDATION_CONFIG["max_username_length"]:
        return False

    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, username))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return {"valid": False, "errors": ["Password is required"]}

    errors = []

    if len(password) < VALIDATION_CONFIG["min_password_length"]:
        errors.append(
            f"Password must be at least {VALIDATION_CONFIG['min_password_length']} characters long"
        )

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    return {"valid": len(errors) == 0, "errors": errors}


def sanitize_input(text: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""

    # Remove leading/trailing whitespace
    sanitized = text.strip()

    if not allow_html:
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', "", sanitized)

        # Check for XSS patterns
        dangerous_patterns = [
            r"<script[^>]*>",  # Script tags
            r"javascript:",  # JavaScript protocol
            r"on\w+\s*=",  # Event handlers
            r"data:text/html",  # Data URLs
            r"vbscript:",  # VBScript
            r"expression\s*\(",  # CSS expressions
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def validate_tool_name(tool_name: str) -> bool:
    """Validate tool name format"""
    if not tool_name or not isinstance(tool_name, str):
        return False

    if len(tool_name) > TOOL_CONFIG["max_tool_name_length"]:
        return False

    # Only allow alphanumeric characters, underscores, and hyphens
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, tool_name))


def validate_target(target: str) -> bool:
    """Validate target input for tools"""
    if not target or not isinstance(target, str):
        return False

    if len(target) > TOOL_CONFIG["max_target_length"]:
        return False

    # Check for potentially dangerous content
    dangerous_patterns = [r"<script", r"javascript:", r"data:", r"vbscript:"]
    for pattern in dangerous_patterns:
        if re.search(pattern, target, re.IGNORECASE):
            return False

    return True


def validate_severity(severity: str) -> bool:
    """Validate vulnerability severity level"""
    if not severity or not isinstance(severity, str):
        return False

    valid_severities = ["critical", "high", "medium", "low", "info"]
    return severity.lower() in valid_severities


def validate_json_size(json_data: Union[str, Dict, List], max_size: int = None) -> bool:
    """Validate JSON data size"""
    if max_size is None:
        from config import MAX_JSON_SIZE

        max_size = MAX_JSON_SIZE

    if isinstance(json_data, str):
        return len(json_data) <= max_size
    elif isinstance(json_data, (dict, list)):
        import json

        try:
            json_str = json.dumps(json_data)
            return len(json_str) <= max_size
        except (TypeError, ValueError):
            return False

    return False


def validate_file_upload(filename: str, file_size: int) -> Dict[str, Any]:
    """Validate file upload"""
    from config import ALLOWED_FILE_TYPES, MAX_FILE_SIZE

    errors = []

    # Check file size
    if file_size > MAX_FILE_SIZE:
        errors.append(
            f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
        )

    # Check file extension
    if filename:
        file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if file_ext not in ALLOWED_FILE_TYPES:
            errors.append(
                f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
            )

    return {"valid": len(errors) == 0, "errors": errors}


def validate_pagination(
    page: int, page_size: int, max_page_size: int = 100
) -> Dict[str, Any]:
    """Validate pagination parameters"""
    errors = []

    if page < 1:
        errors.append("Page number must be greater than 0")

    if page_size < 1:
        errors.append("Page size must be greater than 0")
    elif page_size > max_page_size:
        errors.append(f"Page size cannot exceed {max_page_size}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "page": max(1, page),
        "page_size": min(max(1, page_size), max_page_size),
    }


def validate_date_range(
    start_date: Optional[str], end_date: Optional[str]
) -> Dict[str, Any]:
    """Validate date range parameters"""
    errors = []
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            errors.append(
                "Invalid start date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            errors.append(
                "Invalid end date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )

    if start_dt and end_dt and start_dt > end_dt:
        errors.append("Start date must be before end date")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "start_date": start_dt,
        "end_date": end_dt,
    }


def validate_search_query(query: str, max_length: int = 100) -> str:
    """Validate and sanitize search query"""
    if not query or not isinstance(query, str):
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", query.strip())

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_sort_field(sort_field: str, allowed_fields: List[str]) -> bool:
    """Validate sort field against allowed fields"""
    if not sort_field or not isinstance(sort_field, str):
        return False

    return sort_field in allowed_fields


def validate_sort_order(sort_order: str) -> bool:
    """Validate sort order (asc/desc)"""
    if not sort_order or not isinstance(sort_order, str):
        return False

    return sort_order.lower() in ["asc", "desc"]
