#!/bin/bash

##############################################################################
# Production Deployment Script for NYCU Course Platform
# Purpose: Automated deployment to production with all services
# Domain: nymu.com.tw
##############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DEPLOYMENT_DIR="/opt/nycu-platform"
DOMAIN="nymu.com.tw"
ENVIRONMENT="${ENVIRONMENT:-production}"
BACKUP_DIR="/backup/nycu-platform"
LOG_FILE="/var/log/nycu-deployment.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_section() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_section "Checking Prerequisites"

    local missing_tools=0

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        missing_tools=1
    else
        log_success "Docker is installed: $(docker --version)"
    fi

    # Check docker-compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "docker-compose is not available"
        missing_tools=1
    else
        log_success "docker-compose is available"
    fi

    # Check git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        missing_tools=1
    else
        log_success "Git is installed: $(git --version)"
    fi

    # Check curl
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed"
        missing_tools=1
    else
        log_success "curl is installed"
    fi

    if [ $missing_tools -eq 1 ]; then
        log_error "Please install missing tools and try again"
        exit 1
    fi
}

# Setup deployment directory
setup_directories() {
    log_section "Setting Up Directories"

    mkdir -p "$DEPLOYMENT_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "/var/log/nycu-platform"
    mkdir -p "/var/www/certbot"
    mkdir -p "/etc/letsencrypt/live/$DOMAIN"

    log_success "Directories created"
}

# Clone or update repository
setup_repository() {
    log_section "Setting Up Repository"

    local repo_url="${REPO_URL:-https://github.com/anthropics/nycu-course-platform.git}"

    if [ -d "$DEPLOYMENT_DIR/.git" ]; then
        log_info "Repository already exists, updating..."
        cd "$DEPLOYMENT_DIR"
        git pull origin main
    else
        log_info "Cloning repository from $repo_url..."
        git clone "$repo_url" "$DEPLOYMENT_DIR"
        cd "$DEPLOYMENT_DIR"
    fi

    log_success "Repository ready at $DEPLOYMENT_DIR"
}

# Backup existing data
backup_data() {
    log_section "Backing Up Existing Data"

    if [ -f "$DEPLOYMENT_DIR/backend/courses.db" ]; then
        log_info "Backing up database..."
        cp "$DEPLOYMENT_DIR/backend/courses.db" "$BACKUP_DIR/courses.db.$TIMESTAMP"
        log_success "Database backed up"
    fi

    if [ -d "$DEPLOYMENT_DIR/backend/logs" ]; then
        log_info "Backing up logs..."
        cp -r "$DEPLOYMENT_DIR/backend/logs" "$BACKUP_DIR/logs.$TIMESTAMP"
        log_success "Logs backed up"
    fi
}

# Load environment variables
load_environment() {
    log_section "Loading Environment Configuration"

    cd "$DEPLOYMENT_DIR"

    # Create or use existing .env file
    if [ ! -f ".env" ]; then
        log_info "Creating .env file..."
        cat > .env << EOF
ENVIRONMENT=$ENVIRONMENT
DOMAIN=$DOMAIN
CERTBOT_EMAIL=${CERTBOT_EMAIL:-admin@$DOMAIN}
POSTGRES_USER=nycu_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
BACKEND_WORKERS=4
FRONTEND_MEMORY=1536
NODE_ENV=production
EOF
        log_success ".env file created"
    else
        log_info ".env file already exists"
    fi

    # Source the environment file
    set -a
    source .env
    set +a

    log_success "Environment loaded"
}

# Build Docker images
build_images() {
    log_section "Building Docker Images"

    cd "$DEPLOYMENT_DIR"

    log_info "Building backend image..."
    docker build -f Dockerfile.backend -t nycu-platform/backend:latest .
    log_success "Backend image built"

    log_info "Building frontend image..."
    docker build -f Dockerfile.frontend -t nycu-platform/frontend:latest .
    log_success "Frontend image built"

    log_success "All images built successfully"
}

# Start services with docker-compose
start_services() {
    log_section "Starting Services"

    cd "$DEPLOYMENT_DIR"

    log_info "Pulling latest base images..."
    docker-compose pull

    log_info "Starting services..."
    docker-compose up -d

    # Wait for services to start
    sleep 5

    log_success "Services started"
}

# Verify services are running
verify_services() {
    log_section "Verifying Services"

    cd "$DEPLOYMENT_DIR"

    local services_ok=0

    # Check backend
    log_info "Checking backend service..."
    if docker-compose exec -T backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend service is healthy"
    else
        log_error "Backend service health check failed"
        services_ok=1
    fi

    # Check frontend
    log_info "Checking frontend service..."
    if docker-compose exec -T frontend curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend service is healthy"
    else
        log_error "Frontend service health check failed"
        services_ok=1
    fi

    # Check nginx
    log_info "Checking nginx service..."
    if docker exec nycu-nginx nginx -t > /dev/null 2>&1; then
        log_success "Nginx configuration is valid"
    else
        log_error "Nginx configuration validation failed"
        services_ok=1
    fi

    return $services_ok
}

# Setup SSL certificates
setup_ssl() {
    log_section "Setting Up SSL Certificates"

    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        log_info "SSL certificate already exists"
        return 0
    fi

    log_warning "SSL certificate not found"
    log_info "Run 'sudo ./deploy-ssl.sh' to setup Let's Encrypt certificates"
    log_info "For now, continuing with HTTP..."
}

# Configure monitoring
setup_monitoring() {
    log_section "Setting Up Monitoring"

    cd "$DEPLOYMENT_DIR"

    # Create monitoring script
    cat > /usr/local/bin/nycu-health-check.sh << 'EOF'
#!/bin/bash

DOMAIN="nymu.com.tw"
BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

check_health() {
    local service=$1
    local url=$2

    if curl -sf "$url" > /dev/null; then
        echo "✅ $service is healthy"
        return 0
    else
        echo "❌ $service is DOWN"
        return 1
    fi
}

echo "🔍 Health Check - $(date)"
check_health "Backend" "$BACKEND_URL"
check_health "Frontend" "$FRONTEND_URL"
EOF

    chmod +x /usr/local/bin/nycu-health-check.sh
    log_success "Health check script installed"

    # Add to crontab
    if ! crontab -l 2>/dev/null | grep -q "nycu-health-check"; then
        (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/nycu-health-check.sh >> /var/log/nycu-health.log 2>&1") | crontab -
        log_success "Health check added to crontab (every 5 minutes)"
    fi
}

# Setup log rotation
setup_log_rotation() {
    log_section "Setting Up Log Rotation"

    cat > /etc/logrotate.d/nycu-platform << EOF
/var/log/nycu-platform/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}

/var/log/nycu-deployment.log {
    daily
    rotate 7
    compress
}
EOF

    log_success "Log rotation configured"
}

# Create systemd service file
create_systemd_service() {
    log_section "Creating Systemd Service"

    cat > /etc/systemd/system/nycu-platform.service << EOF
[Unit]
Description=NYCU Course Platform Docker Compose Service
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$DEPLOYMENT_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml up
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml down
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable nycu-platform.service

    log_success "Systemd service created and enabled"
}

# Display deployment summary
display_summary() {
    log_section "DEPLOYMENT SUMMARY"

    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ NYCU Platform Deployment Complete${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Service Information:${NC}"
    echo -e "  Frontend: http://localhost:3000"
    echo -e "  Backend API: http://localhost:8000"
    echo -e "  API Docs: http://localhost:8000/docs"
    echo -e "  Domain: https://$DOMAIN (after SSL setup)"
    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose ps 2>/dev/null || docker ps
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "  View logs: docker-compose logs -f"
    echo -e "  Health check: /usr/local/bin/nycu-health-check.sh"
    echo -e "  Service status: systemctl status nycu-platform"
    echo -e "  Restart service: systemctl restart nycu-platform"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Setup SSL: sudo ./deploy-ssl.sh"
    echo -e "  2. Update DNS records to point $DOMAIN to this server"
    echo -e "  3. Verify HTTPS: https://$DOMAIN"
    echo -e "  4. Configure monitoring and alerts"
    echo ""
    echo -e "${YELLOW}Deployment Log:${NC}"
    echo -e "  $LOG_FILE"
    echo ""
}

# Rollback on failure
rollback() {
    log_error "Deployment failed, attempting rollback..."

    cd "$DEPLOYMENT_DIR"
    docker-compose down 2>/dev/null || true

    if [ -f "$BACKUP_DIR/courses.db.$TIMESTAMP" ]; then
        log_info "Restoring database from backup..."
        cp "$BACKUP_DIR/courses.db.$TIMESTAMP" "$DEPLOYMENT_DIR/backend/courses.db"
    fi

    log_error "Rollback completed. Check logs for details."
    exit 1
}

# Main execution
main() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  NYCU Platform Production Deployment                 ║${NC}"
    echo -e "${CYAN}║  Domain: nymu.com.tw                                 ║${NC}"
    echo -e "${CYAN}║  Time: $(date)                   ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Setup log file
    mkdir -p $(dirname "$LOG_FILE")
    touch "$LOG_FILE"

    # Error handling
    trap 'rollback' ERR

    check_root
    check_prerequisites
    setup_directories
    setup_repository
    backup_data
    load_environment
    build_images
    start_services

    if verify_services; then
        log_success "All services verified"
    else
        log_error "Service verification failed"
        exit 1
    fi

    setup_ssl
    setup_monitoring
    setup_log_rotation
    create_systemd_service
    display_summary

    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
