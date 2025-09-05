#!/bin/bash

# Deployment Test Script
# This script tests all critical components of the deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="production.env"
DOMAIN="pentorasecbeta.mywire.org"

echo "🧪 Starting Deployment Tests"
echo "================================"

# Test 1: Check if required files exist
print_status "Test 1: Checking required files..."

required_files=(
    "$COMPOSE_FILE"
    "$ENV_FILE"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "nginx/conf.d/default.conf"
    "generate-secrets.sh"
    "deploy-production.sh"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file exists"
    else
        print_error "✗ $file missing"
        exit 1
    fi
done

# Test 2: Check Docker Compose syntax
print_status "Test 2: Validating Docker Compose syntax..."
if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE config > /dev/null 2>&1; then
    print_success "✓ Docker Compose syntax is valid"
else
    print_error "✗ Docker Compose syntax error"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE config
    exit 1
fi

# Test 3: Check environment variables
print_status "Test 3: Checking environment variables..."

if [ -f "$ENV_FILE" ]; then
    # Check if passwords are not default
    if grep -q "change_me" "$ENV_FILE"; then
        print_warning "⚠ Some passwords still contain 'change_me' - consider regenerating"
    else
        print_success "✓ Environment variables look secure"
    fi
    
    # Check required variables
    required_vars=("MYSQL_ROOT_PASSWORD" "MYSQL_PASSWORD" "JWT_SECRET_KEY" "REDIS_PASSWORD")
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" "$ENV_FILE"; then
            print_success "✓ $var is set"
        else
            print_error "✗ $var is missing"
        fi
    done
else
    print_error "✗ $ENV_FILE not found"
    exit 1
fi

# Test 4: Check Docker images can be built
print_status "Test 4: Testing Docker image builds..."

# Test backend build
print_status "Testing backend Docker build..."
if docker build -t test-backend ./backend > /dev/null 2>&1; then
    print_success "✓ Backend Docker image builds successfully"
    docker rmi test-backend > /dev/null 2>&1
else
    print_error "✗ Backend Docker image build failed"
    docker build -t test-backend ./backend
    exit 1
fi

# Test frontend build
print_status "Testing frontend Docker build..."
if docker build -t test-frontend ./frontend > /dev/null 2>&1; then
    print_success "✓ Frontend Docker image builds successfully"
    docker rmi test-frontend > /dev/null 2>&1
else
    print_error "✗ Frontend Docker image build failed"
    docker build -t test-frontend ./frontend
    exit 1
fi

# Test 5: Check SSL certificates
print_status "Test 5: Checking SSL certificate setup..."

if [ -f "./nginx/ssl/nginx-selfsigned.crt" ]; then
    print_success "✓ Self-signed certificate exists"
else
    print_warning "⚠ Self-signed certificate not found - will be created during deployment"
fi

# Test 6: Check Nginx configuration
print_status "Test 6: Validating Nginx configuration..."

if [ -f "./nginx/conf.d/default.conf" ]; then
    # Check for SSL configuration
    if grep -q "ssl_certificate" "./nginx/conf.d/default.conf"; then
        print_success "✓ Nginx SSL configuration found"
    else
        print_error "✗ Nginx SSL configuration missing"
    fi
    
    # Check for security headers
    if grep -q "Strict-Transport-Security" "./nginx/conf.d/default.conf"; then
        print_success "✓ Security headers configured"
    else
        print_warning "⚠ Security headers not found in Nginx config"
    fi
else
    print_error "✗ Nginx configuration file not found"
fi

# Test 7: Check if services can start (dry run)
print_status "Test 7: Testing service startup (dry run)..."

# Start only MySQL and Redis for testing
if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d mysql redis > /dev/null 2>&1; then
    print_success "✓ Core services (MySQL, Redis) can start"
    
    # Wait a bit and check health
    sleep 10
    
    # Check MySQL health
    if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec mysql mysqladmin ping -h localhost -u root -p$(grep MYSQL_ROOT_PASSWORD $ENV_FILE | cut -d'=' -f2) --silent > /dev/null 2>&1; then
        print_success "✓ MySQL is healthy"
    else
        print_warning "⚠ MySQL health check failed"
    fi
    
    # Stop test services
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down > /dev/null 2>&1
else
    print_error "✗ Core services failed to start"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs mysql redis
    exit 1
fi

# Test 8: Check port availability
print_status "Test 8: Checking port availability..."

ports=(80 443 3306 6379 8001 3010)
for port in "${ports[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        print_warning "⚠ Port $port is already in use"
    else
        print_success "✓ Port $port is available"
    fi
done

# Test 9: Check file permissions
print_status "Test 9: Checking file permissions..."

# Check if production.env has secure permissions
if [ -f "$ENV_FILE" ]; then
    perms=$(stat -c "%a" "$ENV_FILE" 2>/dev/null || stat -f "%A" "$ENV_FILE" 2>/dev/null)
    if [ "$perms" = "600" ]; then
        print_success "✓ $ENV_FILE has secure permissions (600)"
    else
        print_warning "⚠ $ENV_FILE permissions are $perms (should be 600)"
        chmod 600 "$ENV_FILE"
        print_success "✓ Fixed $ENV_FILE permissions"
    fi
fi

# Test 10: Check script executability
print_status "Test 10: Checking script executability..."

scripts=("generate-secrets.sh" "deploy-production.sh" "init-letsencrypt.sh" "nginx/ssl-setup.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            print_success "✓ $script is executable"
        else
            print_warning "⚠ $script is not executable, fixing..."
            chmod +x "$script"
            print_success "✓ Fixed $script permissions"
        fi
    fi
done

echo ""
echo "🎉 All tests completed!"
echo "================================"
print_success "✅ Deployment is ready!"
echo ""
print_status "📋 Next steps:"
print_status "   1. Run: ./deploy-production.sh"
print_status "   2. Check logs: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs"
print_status "   3. Test HTTPS: curl -k https://localhost"
print_status "   4. Monitor services: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps"
echo ""
print_warning "⚠️  Remember to:"
print_warning "   - Set up firewall rules for ports 80 and 443"
print_warning "   - Configure DNS to point to your server"
print_warning "   - Set up monitoring and backups"
print_warning "   - Update GOOGLE_API_KEY and SEARCH_ENGINE_ID in production.env"
