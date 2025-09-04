import os

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
CORS_ORIGINS = "http://localhost:3000,http://localhost:3010,https://*.pythonanywhere.com"

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
