#!/bin/bash

# Production Deployment Script for Google Cloud VM
# This script deploys the Pentest Suite application with all security fixes

set -e

# Colors for output
RED='\033[0;31m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
DOMAIN="pentorasecbeta.mywire.org"
EMAIL="admin@pentorasecbeta.mywire.org"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="production.env"

echo "🚀 Starting Production Deployment for Pentest Suite"
echo "🌐 Domain: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "docker-compose.prod.yml not found. Please run this script from the project root directory."
    exit 1
fi

print_status "Step 1: Generating secure secrets..."

# Generate secure secrets if production.env doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    print_status "Creating secure production environment file..."
    ./generate-secrets.sh
else
    print_warning "production.env already exists. Using existing configuration."
fi

print_status "Step 2: Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

print_status "Step 3: Stopping existing containers..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down --remove-orphans || true

print_status "Step 4: Cleaning Docker cache..."
docker system prune -a --volumes -f
docker volume prune -f
docker network prune -f

print_status "Step 5: Setting up SSL certificates..."

# Create necessary directories
mkdir -p ./nginx/conf.d
mkdir -p ./nginx/ssl
mkdir -p ./certbot/conf
mkdir -p ./certbot/www
mkdir -p ./certbot/logs

# Generate self-signed certificate for initial setup
if [ ! -f "./nginx/ssl/nginx-selfsigned.crt" ]; then
    print_status "Generating self-signed certificate for initial setup..."
    ./nginx/ssl-setup.sh
fi

print_status "Step 6: Starting core services..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d mysql redis ollama

print_status "Waiting for core services to be ready..."
sleep 30

# Check if MySQL is healthy
print_status "Checking MySQL health..."
for i in {1..30}; do
    if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec mysql mysqladmin ping -h localhost -u root -p$(grep MYSQL_ROOT_PASSWORD $ENV_FILE | cut -d'=' -f2) --silent; then
        print_success "MySQL is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "MySQL failed to start properly"
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs mysql
        exit 1
    fi
    sleep 2
done

print_status "Step 7: Starting backend services..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d backend celery-worker

print_status "Waiting for backend to be ready..."
sleep 20

print_status "Step 8: Starting frontend..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d frontend

print_status "Step 9: Starting Nginx reverse proxy..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d nginx

print_status "Waiting for all services to be ready..."
sleep 30

print_status "Step 10: Obtaining Let's Encrypt SSL certificate..."

# Try to get Let's Encrypt certificate
if ./init-letsencrypt.sh -d $DOMAIN -e $EMAIL; then
    print_success "Let's Encrypt certificate obtained successfully!"
else
    print_warning "Let's Encrypt certificate failed, continuing with self-signed certificate"
    print_warning "You can manually run: ./init-letsencrypt.sh -d $DOMAIN -e $EMAIL"
fi

print_status "Step 11: Final health check..."

# Check all services
print_status "Checking service status..."
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps

# Test HTTP connection
print_status "Testing HTTP connection..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost" | grep -q "200\|301\|302"; then
    print_success "HTTP connection successful!"
else
    print_warning "HTTP connection test failed"
fi

# Test HTTPS connection
print_status "Testing HTTPS connection..."
if curl -s -k -o /dev/null -w "%{http_code}" "https://localhost" | grep -q "200\|301\|302"; then
    print_success "HTTPS connection successful!"
else
    print_warning "HTTPS connection test failed"
fi

print_status "Step 12: Setting up automatic renewal..."

# Create renewal script
cat > ./renew-certs.sh << 'EOF'
#!/bin/bash
echo "🔄 Renewing SSL certificates..."
docker-compose -f docker-compose.prod.yml --env-file production.env run --rm certbot renew --webroot --webroot-path=/var/www/certbot

echo "🔄 Reloading Nginx configuration..."
docker-compose -f docker-compose.prod.yml --env-file production.env exec nginx nginx -s reload

echo "✅ Certificate renewal completed"
EOF

chmod +x ./renew-certs.sh

print_success "🎉 Production deployment completed successfully!"
echo ""
print_status "📋 Service URLs:"
print_status "   🌐 Frontend: https://$DOMAIN"
print_status "   🔧 API: https://$DOMAIN/api"
print_status "   ❤️  Health: https://$DOMAIN/health"
print_status "   🗄️  phpMyAdmin: https://$DOMAIN/phpmyadmin"
echo ""
print_status "📊 Service Status:"
docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps
echo ""
print_status "🔧 Useful Commands:"
print_status "   View logs: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs"
print_status "   Restart services: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE restart"
print_status "   Renew certificates: ./renew-certs.sh"
print_status "   Stop all services: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down"
echo ""
print_warning "⚠️  Important Security Notes:"
print_warning "   1. Change all default passwords in production.env"
print_warning "   2. Set up firewall rules for ports 80 and 443"
print_warning "   3. Monitor logs regularly"
print_warning "   4. Set up automated backups"
print_warning "   5. Keep Docker images updated"
echo ""
print_success "🚀 Your Pentest Suite is now running at: https://$DOMAIN"
