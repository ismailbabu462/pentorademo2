#!/bin/bash

# Google Cloud Deployment Script for Pentest Suite
# This script deploys the application to Google Cloud Run

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
PROJECT_ID="pentora-security"
REGION="us-central1"
SERVICE_NAME="pentest-suite"
DOMAIN="pentorasecbeta.mywire.org"

print_status "Starting Google Cloud deployment for Pentest Suite..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set project
print_status "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create Cloud SQL instance if it doesn't exist
print_status "Creating Cloud SQL instance..."
if ! gcloud sql instances describe pentest-mysql --project=$PROJECT_ID &> /dev/null; then
    gcloud sql instances create pentest-mysql \
        --database-version=MYSQL_8_0 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=rootpassword123 \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase
    print_success "Cloud SQL instance created"
else
    print_status "Cloud SQL instance already exists"
fi

# Create database
print_status "Creating database..."
gcloud sql databases create pentest_suite --instance=pentest-mysql || true

# Create database user
print_status "Creating database user..."
gcloud sql users create pentest_user \
    --instance=pentest-mysql \
    --password=pentest_password || true

# Build and push Docker images
print_status "Building and pushing Docker images..."

# Build backend image
print_status "Building backend image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/pentest-backend ./backend

# Build frontend image
print_status "Building frontend image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/pentest-frontend ./frontend

# Build nginx image
print_status "Building nginx image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/pentest-nginx ./nginx

# Deploy to Cloud Run
print_status "Deploying backend to Cloud Run..."
gcloud run deploy pentest-backend \
    --image gcr.io/$PROJECT_ID/pentest-backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8001 \
    --set-env-vars="DATABASE_URL=mysql+pymysql://pentest_user:pentest_password@/pentest_suite?unix_socket=/cloudsql/$PROJECT_ID:$REGION:pentest-mysql" \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:pentest-mysql

print_status "Deploying frontend to Cloud Run..."
gcloud run deploy pentest-frontend \
    --image gcr.io/$PROJECT_ID/pentest-frontend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 3010 \
    --set-env-vars="REACT_APP_API_URL=https://pentest-backend-$(gcloud run services describe pentest-backend --region=$REGION --format='value(status.url)' | sed 's|https://||')" \
    --set-env-vars="REACT_APP_BACKEND_URL=https://pentest-backend-$(gcloud run services describe pentest-backend --region=$REGION --format='value(status.url)' | sed 's|https://||')"

print_status "Deploying nginx to Cloud Run..."
gcloud run deploy pentest-nginx \
    --image gcr.io/$PROJECT_ID/pentest-nginx \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 80 \
    --port 443

# Get service URLs
BACKEND_URL=$(gcloud run services describe pentest-backend --region=$REGION --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe pentest-frontend --region=$REGION --format='value(status.url)')
NGINX_URL=$(gcloud run services describe pentest-nginx --region=$REGION --format='value(status.url)')

print_success "Deployment completed successfully!"
print_status "Service URLs:"
print_status "Backend: $BACKEND_URL"
print_status "Frontend: $FRONTEND_URL"
print_status "Nginx: $NGINX_URL"

# Setup custom domain
print_status "Setting up custom domain mapping..."
gcloud run domain-mappings create \
    --service pentest-nginx \
    --domain $DOMAIN \
    --region $REGION

print_success "Custom domain mapping created for $DOMAIN"

print_status "Deployment completed! Your application is now available at:"
print_success "https://$DOMAIN"
