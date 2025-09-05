#!/bin/bash

# Quick Fix Start Script
# Fixes common issues and starts the application

echo "🔧 Quick Fix Start Script"
echo "========================="

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Generate self-signed SSL certificate
echo "🔒 Generating self-signed SSL certificate..."
mkdir -p nginx/ssl
if [ ! -f "nginx/ssl/nginx-selfsigned.crt" ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/nginx-selfsigned.key \
        -out nginx/ssl/nginx-selfsigned.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=pentorasecbeta.mywire.org"
    echo "✅ Self-signed certificate generated"
else
    echo "✅ Self-signed certificate already exists"
fi

# Generate production environment if not exists
if [ ! -f "production.env" ]; then
    echo "🔐 Generating production environment..."
    ./generate-secrets.sh
fi

# Start services without certbot
echo "🚀 Starting services (without certbot)..."
docker-compose up -d mysql redis ollama backend frontend nginx

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Quick fix complete!"
echo ""
echo "📋 Access URLs:"
echo "  🌐 Frontend: http://localhost (or your VM IP)"
echo "  🔧 API: http://localhost:8001"
echo "  ❤️ Health: http://localhost:8001/health"
echo "  🗄️ phpMyAdmin: http://localhost:8080"
echo ""
echo "⚠️ Note: Using self-signed certificates. For production, run:"
echo "  ./init-letsencrypt.sh -d your-domain.com -e your-email@domain.com"
