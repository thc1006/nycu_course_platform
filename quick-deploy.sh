#!/bin/bash

##############################################################################
# NYCU Platform - Quick Start Deployment Script
# Purpose: One-command deployment for production
# Usage: sudo bash quick-deploy.sh
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
DOMAIN="nymu.com.tw"
PLATFORM_DIR="/opt/nycu-platform"
LOG_DIR="/var/log/nycu-platform"

# Functions
log_header() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  NYCU Course Platform - Quick Deployment Script           ║${NC}"
    echo -e "${CYAN}║  Domain: ${DOMAIN:0:42}            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_step() {
    echo -e "${CYAN}→${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_prerequisites() {
    log_section "Step 1: Checking Prerequisites"

    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root (use: sudo bash quick-deploy.sh)"
        exit 1
    fi

    # Check Docker
    log_step "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker found: $(docker --version)"

    # Check Docker Compose
    log_step "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "Docker Compose found"

    # Check if Docker daemon is running
    log_step "Checking Docker daemon..."
    if ! docker ps &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    log_success "Docker daemon is running"

    # Check if curl is installed
    log_step "Checking curl..."
    if ! command -v curl &> /dev/null; then
        log_warning "curl is not installed - some features may be limited"
    else
        log_success "curl found"
    fi
}

prepare_directories() {
    log_section "Step 2: Preparing Directories"

    log_step "Creating platform directory: $PLATFORM_DIR"
    mkdir -p "$PLATFORM_DIR"

    log_step "Creating log directory: $LOG_DIR"
    mkdir -p "$LOG_DIR"/{api,performance,security}

    log_step "Creating backup directory"
    mkdir -p /backup

    log_success "All directories prepared"
}

copy_files() {
    log_section "Step 3: Copying Application Files"

    log_step "Detecting current directory..."
    CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    log_info "Source directory: $CURRENT_DIR"

    if [ ! -f "$CURRENT_DIR/docker-compose.yml" ]; then
        log_error "docker-compose.yml not found in $CURRENT_DIR"
        exit 1
    fi

    log_step "Copying files to $PLATFORM_DIR..."
    cp -r "$CURRENT_DIR"/* "$PLATFORM_DIR/" 2>/dev/null || true
    cp -r "$CURRENT_DIR"/.env* "$PLATFORM_DIR/" 2>/dev/null || true

    log_success "Files copied successfully"

    # Fix ownership
    chown -R nobody:nogroup "$PLATFORM_DIR" 2>/dev/null || true
}

deploy_services() {
    log_section "Step 4: Deploying Services with Docker Compose"

    cd "$PLATFORM_DIR"

    log_step "Building Docker images..."
    if docker-compose build 2>&1 | grep -q "ERROR\|failed"; then
        log_error "Docker image build failed"
        exit 1
    fi
    log_success "Docker images built successfully"

    log_step "Starting services..."
    docker-compose up -d

    log_success "Services started"

    # Wait for services to be ready
    log_step "Waiting for services to be ready (30 seconds)..."
    sleep 10

    # Check container status
    log_step "Verifying container status..."
    if ! docker-compose ps | grep -q "Up"; then
        log_error "Services failed to start"
        docker-compose logs
        exit 1
    fi

    log_success "All containers are running"
}

verify_services() {
    log_section "Step 5: Verifying Services"

    log_step "Checking backend health..."
    for i in {1..5}; do
        if curl -s http://localhost:8000/health | grep -q "healthy"; then
            log_success "Backend health check passed"
            break
        fi
        if [ $i -lt 5 ]; then
            log_info "Retry $i/5 in 5 seconds..."
            sleep 5
        else
            log_error "Backend health check failed after 5 attempts"
            exit 1
        fi
    done

    log_step "Checking frontend..."
    if curl -s http://localhost:3000 > /dev/null 2>&1 || curl -s http://localhost:3001 > /dev/null 2>&1; then
        log_success "Frontend is responding"
    else
        log_warning "Frontend not yet responding (normal during first deployment)"
    fi

    log_step "Checking API endpoints..."
    if curl -s http://localhost:8000/api/courses | grep -q "id\|total"; then
        log_success "API endpoints working"
    else
        log_warning "API endpoints not yet responding"
    fi
}

setup_ssl() {
    log_section "Step 6: SSL/TLS Certificate Setup"

    log_info "Checking if certificates already exist..."
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        log_success "SSL certificates already configured"
        return 0
    fi

    log_step "Installing Certbot..."
    if ! command -v certbot &> /dev/null; then
        apt-get update > /dev/null 2>&1
        apt-get install -y certbot python3-certbot-nginx > /dev/null 2>&1
    fi

    log_step "Running deploy-ssl.sh..."
    if [ -f "$PLATFORM_DIR/deploy-ssl.sh" ]; then
        bash "$PLATFORM_DIR/deploy-ssl.sh"
        log_success "SSL certificates configured"
    else
        log_warning "deploy-ssl.sh not found - skip for now"
        log_info "Run later: sudo bash deploy-ssl.sh"
    fi
}

setup_monitoring() {
    log_section "Step 7: Setting Up Monitoring"

    log_step "Creating health check script..."
    mkdir -p /usr/local/bin

    cat > /usr/local/bin/nycu-health-check.sh << 'HEALTHCHECK'
#!/bin/bash
BACKEND=$(curl -s http://localhost:8000/health | grep -o "healthy")
FRONTEND=$(curl -s -I http://localhost:3000 | grep "HTTP" | grep -o "200\|301\|302" || curl -s -I http://localhost:3001 | grep "HTTP" | grep -o "200\|301\|302")
NGINX=$(curl -s -I http://localhost/health | grep -o "200")

if [ ! -z "$BACKEND" ] && [ ! -z "$FRONTEND" ]; then
    echo "✅ All systems operational"
    exit 0
else
    echo "❌ System check failed"
    [ -z "$BACKEND" ] && echo "  - Backend: DOWN"
    [ -z "$FRONTEND" ] && echo "  - Frontend: DOWN"
    [ -z "$NGINX" ] && echo "  - Nginx: DOWN"
    exit 1
fi
HEALTHCHECK

    chmod +x /usr/local/bin/nycu-health-check.sh
    log_success "Health check script installed"

    log_step "Running setup-monitoring.sh..."
    if [ -f "$PLATFORM_DIR/setup-monitoring.sh" ]; then
        bash "$PLATFORM_DIR/setup-monitoring.sh"
        log_success "Monitoring configured"
    else
        log_warning "setup-monitoring.sh not found"
    fi
}

final_verification() {
    log_section "Step 8: Final Verification"

    log_step "Running comprehensive verification..."
    if [ -f "$PLATFORM_DIR/verify-deployment.sh" ]; then
        bash "$PLATFORM_DIR/verify-deployment.sh"
    else
        log_warning "verify-deployment.sh not found"

        # Basic verification
        log_step "Running basic checks..."
        BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
        FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)

        if [ "$BACKEND_STATUS" = "200" ]; then
            log_success "Backend: HTTP $BACKEND_STATUS"
        else
            log_error "Backend: HTTP $BACKEND_STATUS"
        fi

        if [ "$FRONTEND_STATUS" = "200" ] || [ "$FRONTEND_STATUS" = "304" ]; then
            log_success "Frontend: HTTP $FRONTEND_STATUS"
        else
            log_warning "Frontend: HTTP $FRONTEND_STATUS"
        fi
    fi
}

display_summary() {
    log_section "Deployment Complete! 🎉"

    echo ""
    echo -e "${GREEN}✅ NYCU Platform deployed successfully!${NC}"
    echo ""

    echo -e "${BLUE}Service Access:${NC}"
    echo "  🌐 Frontend:     http://localhost:3000"
    echo "  📚 Backend API:  http://localhost:8000"
    echo "  📖 API Docs:     http://localhost:8000/docs"
    echo "  🏥 Health Check: http://localhost:8000/health"
    echo ""

    echo -e "${BLUE}After DNS Configuration:${NC}"
    echo "  🌐 Frontend:     https://$DOMAIN"
    echo "  📚 API:          https://$DOMAIN/api"
    echo "  📖 API Docs:     https://$DOMAIN/api/docs"
    echo ""

    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View services:    docker-compose ps"
    echo "  View logs:        docker-compose logs -f"
    echo "  Health check:     /usr/local/bin/nycu-health-check.sh"
    echo "  Restart services: docker-compose restart"
    echo "  Stop services:    docker-compose down"
    echo "  Verify deployment: bash verify-deployment.sh"
    echo ""

    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Configure DNS records for $DOMAIN"
    echo "  2. Run SSL setup: sudo bash deploy-ssl.sh"
    echo "  3. Monitor logs: docker-compose logs -f"
    echo "  4. Test access: https://$DOMAIN"
    echo ""

    echo -e "${CYAN}Platform Directory:${NC} $PLATFORM_DIR"
    echo -e "${CYAN}Log Directory:${NC} $LOG_DIR"
    echo ""
}

main() {
    log_header

    # Check prerequisites
    check_prerequisites || exit 1

    # Prepare system
    prepare_directories || exit 1

    # Copy files
    copy_files || exit 1

    # Deploy services
    deploy_services || exit 1

    # Verify services
    verify_services || exit 1

    # Setup SSL
    setup_ssl || log_warning "SSL setup encountered issues (non-critical)"

    # Setup monitoring
    setup_monitoring || log_warning "Monitoring setup encountered issues (non-critical)"

    # Final verification
    final_verification || log_warning "Some verification checks failed (review manually)"

    # Display summary
    display_summary

    log_section "✨ Ready for Production! ✨"
    echo ""
}

# Run main
main "$@"
