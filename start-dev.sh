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

echo ""
echo "🎉 Development environment started!"
echo ""
echo "📋 Access URLs:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔧 API: http://localhost:8001"
echo "  ❤️ Health: http://localhost:8001/health"
echo "  🗄️ phpMyAdmin: http://localhost:8080"
echo "  🤖 Ollama: http://localhost:11434"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs: docker-compose -f docker-compose.dev.yml logs"
echo "  Stop all: docker-compose -f docker-compose.dev.yml down"
echo "  Restart: ./start-dev.sh"
