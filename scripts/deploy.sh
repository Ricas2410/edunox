#!/bin/bash

# EduBridge Ghana Production Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="edubridge"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if required files exist
check_requirements() {
    log "Checking deployment requirements..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
    fi
    
    if [ ! -f ".env" ]; then
        error "Environment file not found: .env"
    fi
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running or not accessible"
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose > /dev/null 2>&1; then
        error "Docker Compose is not installed"
    fi
    
    success "All requirements met"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./logs"
    mkdir -p "./nginx/logs"
    mkdir -p "./nginx/ssl"
    mkdir -p "./monitoring"
    
    success "Directories created"
}

# Load environment variables
load_environment() {
    log "Loading environment variables..."
    
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
        success "Environment variables loaded"
    else
        error "Environment file not found"
    fi
}

# Backup database
backup_database() {
    log "Creating database backup..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps db | grep -q "Up"; then
        BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
        
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_dump \
            -U "${POSTGRES_USER:-edubridge}" \
            -d "${POSTGRES_DB:-edubridge}" > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            success "Database backup created: $BACKUP_FILE"
        else
            warning "Database backup failed, but continuing deployment"
        fi
    else
        warning "Database container not running, skipping backup"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    success "Images pulled successfully"
}

# Build application image
build_application() {
    log "Building application image..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build web
    
    success "Application image built successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm web python manage.py migrate
    
    success "Database migrations completed"
}

# Collect static files
collect_static() {
    log "Collecting static files..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm web python manage.py collectstatic --noinput
    
    success "Static files collected"
}

# Start services
start_services() {
    log "Starting services..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "Services started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for services to start
    sleep 30
    
    # Check if web service is healthy
    for i in {1..10}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps web | grep -q "healthy"; then
            success "Web service is healthy"
            return 0
        fi
        
        log "Waiting for web service to become healthy... (attempt $i/10)"
        sleep 10
    done
    
    error "Web service failed health check"
}

# Clean up old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
    
    success "Cleanup completed"
}

# Main deployment function
deploy() {
    log "Starting deployment of $PROJECT_NAME..."
    
    check_requirements
    create_directories
    load_environment
    backup_database
    pull_images
    build_application
    run_migrations
    collect_static
    start_services
    health_check
    cleanup
    
    success "Deployment completed successfully!"
    log "Application is now running at: ${SITE_URL:-https://edubridge.com}"
}

# Rollback function
rollback() {
    log "Starting rollback..."
    
    # Stop current services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Restore from latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | head -n1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring database from: $LATEST_BACKUP"
        
        # Start only database
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d db
        sleep 10
        
        # Restore database
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql \
            -U "${POSTGRES_USER:-edubridge}" \
            -d "${POSTGRES_DB:-edubridge}" < "$LATEST_BACKUP"
        
        success "Database restored"
    else
        warning "No backup found for rollback"
    fi
    
    # Start services with previous image
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "Rollback completed"
}

# Show logs
show_logs() {
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f "$1"
}

# Show status
show_status() {
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

# Main script logic
case "$1" in
    "deploy")
        deploy
        ;;
    "rollback")
        rollback
        ;;
    "logs")
        show_logs "$2"
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_database
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|logs [service]|status|backup|health}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application"
        echo "  rollback - Rollback to previous version"
        echo "  logs     - Show logs for all services or specific service"
        echo "  status   - Show status of all services"
        echo "  backup   - Create database backup"
        echo "  health   - Check application health"
        exit 1
        ;;
esac
