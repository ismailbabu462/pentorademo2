import os
from typing import List

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = 7  # Reduced from 30 days for better security

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pentest_suite.db")

# MySQL Configuration for local development
MYSQL_DATABASE_URL = os.getenv(
    "MYSQL_DATABASE_URL", 
    "mysql+pymysql://root:rootpassword123@localhost:3306/pentest_suite"
)

# CORS Configuration
CORS_ORIGINS = "https://pentorasecbeta.mywire.org,http://localhost:3000,http://localhost:3010,https://*.pythonanywhere.com"

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Security Configuration
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB
MAX_JSON_SIZE = int(os.getenv("MAX_JSON_SIZE", "10240"))  # 10KB
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

# Payment Configuration
LEMONSQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")  # Production için WARNING
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Application Configuration
APP_NAME = "Emergent Pentest Suite API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A comprehensive penetration testing management platform"

# Security Headers Configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    "default_limit": RATE_LIMIT_PER_MINUTE,
    "window_seconds": 60,
    "per_user_limit": 50,  # Per user per window
    "per_ip_limit": 200    # Per IP per window
}

# Database Connection Pool Configuration
DATABASE_POOL_CONFIG = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "max_overflow": 10,
    "pool_size": 10
}

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_FILE_TYPES = [".txt", ".json", ".csv", ".xml", ".log"]

# Validation Configuration
VALIDATION_CONFIG = {
    "max_title_length": 200,
    "max_description_length": 10000,
    "max_payload_length": 5000,
    "max_username_length": 100,
    "max_email_length": 255,
    "min_password_length": 8
}

# Tool Configuration
TOOL_CONFIG = {
    "max_output_size": 100000,  # 100KB
    "max_target_length": 500,
    "max_tool_name_length": 100,
    "duplicate_check_minutes": 5
}

# AI Configuration
AI_CONFIG = {
    "max_context_length": 50000,
    "max_response_length": 10000,
    "timeout_seconds": 120,
    "max_retries": 3
}
