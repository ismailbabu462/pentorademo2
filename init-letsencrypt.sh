#!/bin/bash

# SSL Certificate initialization script for Pentest Suite
# This script sets up Let's Encrypt SSL certificates using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=""
EMAIL=""
STAGING=0

# Function to print colored output
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

# Function to show usage
show_usage() {
    echo "Usage: $0 -d <domain> -e <email> [--staging]"
    echo ""
    echo "Options:"
    echo "  -d, --domain    Domain name for SSL certificate"
    echo "  -e, --email     Email address for Let's Encrypt notifications"
    echo "  --staging       Use Let's Encrypt staging environment (for testing)"
    echo ""
    echo "Example:"
    echo "  $0 -d pentorasecbeta.mywire.org -e admin@pentorasecbeta.mywire.org"
    echo "  $0 -d pentorasecbeta.mywire.org -e admin@pentorasecbeta.mywire.org --staging"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        --staging)
            STAGING=1
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    print_error "Domain and email are required"
    show_usage
    exit 1
fi

# Validate domain format
if ! [[ $DOMAIN =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
    print_error "Invalid domain format: $DOMAIN"
    exit 1
fi

# Validate email format
if ! [[ $EMAIL =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    print_error "Invalid email format: $EMAIL"
    exit 1
fi

print_status "Starting SSL certificate setup for domain: $DOMAIN"
print_status "Email: $EMAIL"

if [ $STAGING -eq 1 ]; then
    print_warning "Using Let's Encrypt STAGING environment"
    CERTBOT_SERVER="--staging"
else
    print_status "Using Let's Encrypt PRODUCTION environment"
    CERTBOT_SERVER=""
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p ./nginx/conf.d
mkdir -p ./certbot/conf
mkdir -p ./certbot/www
mkdir -p ./certbot/logs

# Update nginx configuration with domain
print_status "Updating Nginx configuration with domain: $DOMAIN"
sed -i "s/your-domain.com/$DOMAIN/g" ./nginx/conf.d/default.conf

# Start Nginx container for initial certificate request
print_status "Starting Nginx container for initial certificate request..."
docker-compose up -d nginx

# Wait for Nginx to be ready
print_status "Waiting for Nginx to be ready..."
sleep 10

# Check if Nginx is running
if ! docker-compose ps nginx | grep -q "Up"; then
    print_error "Nginx failed to start"
    docker-compose logs nginx
    exit 1
fi

print_success "Nginx is running"

# Request SSL certificate
print_status "Requesting SSL certificate from Let's Encrypt..."

# Create certbot command
CERTBOT_CMD="docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email $CERTBOT_SERVER -d $DOMAIN"

print_status "Running: $CERTBOT_CMD"

# Execute certbot command
if eval $CERTBOT_CMD; then
    print_success "SSL certificate obtained successfully!"
else
    print_error "Failed to obtain SSL certificate"
    print_status "Checking certbot logs..."
    docker-compose logs certbot
    exit 1
fi

# Verify certificate files exist
if [ ! -f "./certbot/conf/live/$DOMAIN/fullchain.pem" ] || [ ! -f "./certbot/conf/live/$DOMAIN/privkey.pem" ]; then
    print_error "Certificate files not found after successful request"
    print_status "Available files in certbot/conf/live/$DOMAIN/:"
    ls -la "./certbot/conf/live/$DOMAIN/" || true
    exit 1
fi

print_success "Certificate files verified"

# Restart Nginx with SSL configuration
print_status "Restarting Nginx with SSL configuration..."
docker-compose restart nginx

# Wait for Nginx to restart
print_status "Waiting for Nginx to restart..."
sleep 10

# Test HTTPS connection
print_status "Testing HTTPS connection..."
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" | grep -q "200\|301\|302"; then
    print_success "HTTPS connection successful!"
else
    print_warning "HTTPS connection test failed, but certificate was obtained"
    print_status "You may need to check your DNS settings or firewall configuration"
fi

# Set up automatic renewal
print_status "Setting up automatic certificate renewal..."

# Create renewal script
cat > ./renew-certs.sh << 'EOF'
#!/bin/bash
# Certificate renewal script

echo "Renewing SSL certificates..."
docker-compose run --rm certbot renew --webroot --webroot-path=/var/www/certbot

echo "Reloading Nginx configuration..."
docker-compose exec nginx nginx -s reload

echo "Certificate renewal completed"
EOF

chmod +x ./renew-certs.sh

print_success "Automatic renewal script created: ./renew-certs.sh"

# Add cron job suggestion
print_status "To set up automatic renewal, add this to your crontab:"
print_status "0 12 * * * /path/to/your/project/renew-certs.sh >> /var/log/certbot-renewal.log 2>&1"

# Final status
print_success "SSL certificate setup completed!"
print_status "Domain: $DOMAIN"
print_status "Certificate location: ./certbot/conf/live/$DOMAIN/"
print_status "Nginx configuration: ./nginx/conf.d/default.conf"
print_status "Renewal script: ./renew-certs.sh"

if [ $STAGING -eq 1 ]; then
    print_warning "Remember to run this script again without --staging for production certificates"
fi

print_status "You can now access your application at: https://$DOMAIN"
