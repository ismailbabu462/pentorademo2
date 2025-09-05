#!/bin/bash

# Development Start Script
# Starts the application in development mode

echo "🚀 Starting Development Environment"
echo "=================================="

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true

# Start development services
echo "🚀 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "📊 Service Status:"
docker-compose -f docker-compose.dev.yml ps

# Get external IP and domain
EXTERNAL_IP=$(curl -s https://api.ipify.org || echo "YOUR_VM_IP")
DOMAIN="pentorasecbeta.mywire.org"

echo ""
echo "🎉 Development environment started!"
echo ""
echo "📋 Access URLs:"
echo "  🌐 Frontend: http://$EXTERNAL_IP:3000"
echo "  🔧 API: http://$EXTERNAL_IP:8001"
echo "  ❤️ Health: http://$EXTERNAL_IP:8001/health"
echo "  🗄️ phpMyAdmin: http://$EXTERNAL_IP:8080"
echo "  🤖 Ollama: http://$EXTERNAL_IP:11434"
echo ""
echo "🌍 Domain URLs (if DNS configured):"
echo "  🌐 Frontend: https://$DOMAIN"
echo "  🔧 API: https://$DOMAIN/api"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs: docker-compose -f docker-compose.dev.yml logs"
echo "  Stop all: docker-compose -f docker-compose.dev.yml down"
echo "  Restart: ./start-dev.sh"
