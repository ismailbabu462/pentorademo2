#!/bin/bash

# Self-signed SSL certificate setup for Nginx
# This creates a temporary self-signed certificate for initial setup

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create SSL directory
mkdir -p ./nginx/ssl

print_status "Generating self-signed SSL certificate for initial setup..."

# Generate private key
openssl genrsa -out ./nginx/ssl/nginx-selfsigned.key 2048

# Generate certificate
openssl req -new -x509 -key ./nginx/ssl/nginx-selfsigned.key -out ./nginx/ssl/nginx-selfsigned.crt -days 365 -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Pentora Security/OU=IT Department/CN=pentorasecbeta.mywire.org"

print_success "Self-signed certificate generated successfully!"

print_warning "This is a temporary certificate for initial setup."
print_warning "Please run ./init-letsencrypt.sh to get a proper Let's Encrypt certificate."

# Update nginx configuration to use self-signed certificate
print_status "Updating Nginx configuration to use self-signed certificate..."

# Backup original config
if [ -f "./nginx/conf.d/default.conf" ]; then
    cp ./nginx/conf.d/default.conf ./nginx/conf.d/default.conf.backup
fi

# Create a temporary nginx config with self-signed certificate
cat > ./nginx/conf.d/default-selfsigned.conf << 'EOF'
# Nginx configuration with self-signed certificate
# This is a temporary configuration for initial setup

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# Upstream definitions
upstream backend {
    server pentest_backend:8001;
    keepalive 32;
}

upstream frontend {
    server pentest_frontend:3010;
    keepalive 32;
}

# HTTP server - redirects to HTTPS
server {
    listen 80;
    server_name _;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server with self-signed certificate
server {
    listen 443 ssl http2;
    server_name _;
    
    # Self-signed SSL configuration
    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Client settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # API routes - Backend
    location /api/ {
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        # Proxy settings
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # No caching for health checks
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # Static files and frontend
    location / {
        # Rate limiting for frontend
        limit_req zone=api burst=50 nodelay;
        
        # Proxy to frontend
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security: Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

print_success "Self-signed certificate setup completed!"
print_warning "Remember to run ./init-letsencrypt.sh for production SSL certificates."
