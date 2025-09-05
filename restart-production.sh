#!/bin/bash

# Restart Production Services with Proper Frontend Build
# This script ensures frontend runs in production mode

echo "🔄 Restarting Production Services"
echo "================================="

# Stop all services
echo "🛑 Stopping all services..."
docker compose -f docker-compose.prod.yml --env-file production.env down --remove-orphans

# Remove frontend container and image to force rebuild
echo "🗑️ Removing frontend container and image..."
docker rm -f pentest_frontend 2>/dev/null || true
docker rmi pentest_frontend 2>/dev/null || true

# Clean up Docker
echo "🧹 Cleaning up Docker..."
docker system prune -f

# Generate self-signed SSL certificate if not exists
echo "🔒 Ensuring SSL certificate exists..."
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

# Start services
echo "🚀 Starting production services..."
docker compose -f docker-compose.prod.yml --env-file production.env up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "📊 Service Status:"
docker compose -f docker-compose.prod.yml --env-file production.env ps

# Get external IP and domain
EXTERNAL_IP=$(curl -s https://api.ipify.org || echo "YOUR_VM_IP")
DOMAIN="pentorasecbeta.mywire.org"

echo ""
echo "🎉 Production Services Restarted!"
echo "================================"
echo ""
echo "📋 Access URLs:"
echo "  🌐 Frontend: https://$DOMAIN"
echo "  🔧 API: https://$DOMAIN/api"
echo "  ❤️ Health: https://$DOMAIN/health"
echo "  🗄️ phpMyAdmin: https://$DOMAIN/phpmyadmin"
echo "  🖥️ Backend Direct: http://$EXTERNAL_IP:8001"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs: docker compose -f docker-compose.prod.yml --env-file production.env logs"
echo "  Stop all: docker compose -f docker-compose.prod.yml --env-file production.env down"
echo "  Restart: ./restart-production.sh"
echo ""
echo "⚠️ Important:"
echo "  - Frontend is now running in PRODUCTION mode"
echo "  - Make sure ports 80, 443 are open in your firewall"
echo "  - Check DNS is pointing to your server IP"
