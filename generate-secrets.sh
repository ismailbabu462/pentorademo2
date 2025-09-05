#!/bin/bash

# Generate secure secrets for production deployment
# This script creates a secure production.env file with random passwords

set -e

echo "🔐 Generating secure production secrets..."

# Create production.env with secure passwords
cat > production.env << EOF
# Production Environment Configuration for Google Cloud
# Generated on: $(date)
# IMPORTANT: Keep this file secure and never commit to version control!

# Database Configuration
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
MYSQL_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
DATABASE_URL=mysql+pymysql://pentest_user:\${MYSQL_PASSWORD}@mysql:3306/pentest_suite

# Redis Configuration
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# CORS Configuration
CORS_ORIGINS=https://pentorasecbeta.mywire.org,https://www.pentorasecbeta.mywire.org

# Security Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
LEMONSQUEEZY_WEBHOOK_SECRET=pentora_webhook_$(openssl rand -hex 16)

# AI Configuration
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1
GOOGLE_API_KEY=${GOOGLE_API_KEY:-your_google_api_key_here}
SEARCH_ENGINE_ID=${SEARCH_ENGINE_ID:-your_search_engine_id_here}

# Logging Configuration
LOG_LEVEL=WARNING
DEBUG=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# File Upload
MAX_FILE_SIZE=10485760
MAX_REQUEST_SIZE=1048576
MAX_JSON_SIZE=10240

# Application
APP_NAME=Emergent Pentest Suite API
APP_VERSION=1.0.0
EOF

echo "✅ Secure production.env file generated!"
echo "🔒 File permissions set to 600 (owner read/write only)"
chmod 600 production.env

echo ""
echo "📋 Generated secrets:"
echo "   - MySQL Root Password: $(grep MYSQL_ROOT_PASSWORD production.env | cut -d'=' -f2)"
echo "   - MySQL User Password: $(grep MYSQL_PASSWORD production.env | cut -d'=' -f2)"
echo "   - Redis Password: $(grep REDIS_PASSWORD production.env | cut -d'=' -f2)"
echo "   - JWT Secret: $(grep JWT_SECRET_KEY production.env | cut -d'=' -f2 | cut -c1-20)..."
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Save these passwords securely"
echo "   2. Never commit production.env to version control"
echo "   3. Update GOOGLE_API_KEY and SEARCH_ENGINE_ID if needed"
echo "   4. Test the deployment before going live"
