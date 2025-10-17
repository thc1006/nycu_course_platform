#!/bin/bash

##############################################################################
# SSL/TLS Certificate Setup Script for NYCU Course Platform
# Domain: nymu.com.tw
# Purpose: Automate Let's Encrypt certificate provisioning with auto-renewal
##############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="nymu.com.tw"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
CERT_RENEWAL_DAYS=30
NGINX_CONTAINER="nycu-nginx"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-admin@nymu.com.tw}"
ENVIRONMENT="${ENVIRONMENT:-staging}"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
}

# Check if running as root or with sudo
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker is installed"

    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "docker-compose is not available"
        exit 1
    fi
    log_success "docker-compose is available"

    # Check if Certbot will be available
    if ! command -v certbot &> /dev/null; then
        log_warning "Certbot not installed locally, will use Docker image"
    else
        log_success "Certbot is installed"
    fi
}

# Create required directories
create_directories() {
    log_info "Creating required directories..."

    mkdir -p /var/www/certbot
    mkdir -p /etc/letsencrypt/live/$DOMAIN
    mkdir -p /etc/letsencrypt/archive/$DOMAIN
    mkdir -p ./nginx-ssl

    log_success "Directories created"
}

# Stop nginx temporarily for certificate provisioning
stop_nginx() {
    log_info "Stopping nginx container temporarily..."
    docker-compose down 2>/dev/null || true
    sleep 2
    log_success "Nginx stopped"
}

# Request initial certificate using standalone mode
request_certificate() {
    log_info "Requesting SSL certificate from Let's Encrypt..."
    log_info "Domain: $DOMAIN"
    log_info "Email: $CERTBOT_EMAIL"

    if [ "$ENVIRONMENT" = "production" ]; then
        # Production environment - request real certificate
        certbot certonly \
            --standalone \
            -d "$DOMAIN" \
            -d "www.$DOMAIN" \
            --email "$CERTBOT_EMAIL" \
            --agree-tos \
            --no-eff-email \
            --noninteractive \
            --preferred-challenges http
    else
        # Staging environment - use test server
        log_warning "Using staging Let's Encrypt server for testing"
        certbot certonly \
            --standalone \
            --staging \
            -d "$DOMAIN" \
            -d "www.$DOMAIN" \
            --email "$CERTBOT_EMAIL" \
            --agree-tos \
            --no-eff-email \
            --noninteractive \
            --preferred-challenges http
    fi

    log_success "Certificate requested successfully"
}

# Verify certificate installation
verify_certificate() {
    log_info "Verifying certificate installation..."

    if [ -f "$CERT_DIR/fullchain.pem" ] && [ -f "$CERT_DIR/privkey.pem" ]; then
        log_success "Certificate files verified:"
        log_info "  Fullchain: $CERT_DIR/fullchain.pem"
        log_info "  Private Key: $CERT_DIR/privkey.pem"

        # Display certificate info
        log_info "Certificate Details:"
        openssl x509 -in "$CERT_DIR/fullchain.pem" -noout -dates -subject

        return 0
    else
        log_error "Certificate files not found"
        return 1
    fi
}

# Setup auto-renewal
setup_renewal() {
    log_info "Setting up automatic certificate renewal..."

    # Create renewal hook script
    mkdir -p /etc/letsencrypt/renewal-hooks/post

    cat > /etc/letsencrypt/renewal-hooks/post/docker-compose-reload.sh << 'EOF'
#!/bin/bash
cd /path/to/nycu_course_platform
docker-compose up -d nginx
docker exec nycu-nginx nginx -s reload
EOF

    chmod +x /etc/letsencrypt/renewal-hooks/post/docker-compose-reload.sh

    # Schedule renewal with cron
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        log_info "Adding certbot renewal to crontab..."
        (crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet --post-hook '/etc/letsencrypt/renewal-hooks/post/docker-compose-reload.sh'") | crontab -
        log_success "Cron job added for daily renewal checks"
    else
        log_info "Certbot renewal already in crontab"
    fi
}

# Setup renewal with systemd (alternative to cron)
setup_systemd_renewal() {
    log_info "Setting up systemd timer for certificate renewal..."

    # Create systemd service
    cat > /etc/systemd/system/certbot-renewal.service << EOF
[Unit]
Description=Let's Encrypt Renewal
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet
ExecStartPost=/bin/sh -c 'cd $(pwd) && docker-compose up -d nginx'
ExecStartPost=/bin/sh -c 'docker exec $NGINX_CONTAINER nginx -s reload || true'
EOF

    # Create systemd timer
    cat > /etc/systemd/system/certbot-renewal.timer << EOF
[Unit]
Description=Let's Encrypt Renewal Timer
Requires=certbot-renewal.service

[Timer]
OnCalendar=*-*-* 03:00:00
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Enable and start the timer
    systemctl daemon-reload
    systemctl enable certbot-renewal.timer
    systemctl start certbot-renewal.timer

    log_success "Systemd timer configured for certificate renewal"
}

# Restart services with new certificates
restart_services() {
    log_info "Restarting services with new certificates..."

    # Update docker-compose to include SSL certificates
    docker-compose up -d nginx

    sleep 3

    # Reload nginx configuration
    docker exec $NGINX_CONTAINER nginx -s reload || log_warning "Could not reload nginx"

    log_success "Services restarted"
}

# Test certificate renewal dry-run
test_renewal() {
    log_info "Testing certificate renewal (dry-run)..."

    certbot renew --dry-run --quiet

    log_success "Renewal test completed successfully"
}

# Display summary
display_summary() {
    log_info "SSL/TLS Setup Summary"
    echo ""
    echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ SSL/TLS Certificate Installation Complete${NC}"
    echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BLUE}Domain:${NC} $DOMAIN, www.$DOMAIN"
    echo -e "  ${BLUE}Certificate Path:${NC} $CERT_DIR"
    echo -e "  ${BLUE}Renewal:${NC} Automatic (Daily check at 03:00 UTC)"
    echo -e "  ${BLUE}Status:${NC} $([ -f "$CERT_DIR/fullchain.pem" ] && echo "✅ Active" || echo "❌ Not Found")"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Verify HTTPS access: https://$DOMAIN"
    echo -e "  2. Check certificate validity: openssl s_client -connect $DOMAIN:443"
    echo -e "  3. Monitor renewal logs: tail -f /var/log/letsencrypt/letsencrypt.log"
    echo ""
    echo -e "${BLUE}Maintenance Commands:${NC}"
    echo -e "  Renew manually: certbot renew --force-renewal"
    echo -e "  View status: systemctl status certbot-renewal.timer"
    echo -e "  View certificate: openssl x509 -in $CERT_DIR/fullchain.pem -text -noout"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  SSL/TLS Certificate Setup for NYCU Platform         ║${NC}"
    echo -e "${BLUE}║  Domain: nymu.com.tw                                 ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_root
    check_prerequisites
    create_directories
    stop_nginx

    # Check if certificate already exists
    if [ -f "$CERT_DIR/fullchain.pem" ]; then
        log_warning "Certificate already exists at $CERT_DIR"
        read -p "Do you want to renew it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            request_certificate
        else
            log_info "Skipping certificate provisioning"
        fi
    else
        request_certificate
    fi

    verify_certificate || {
        log_error "Certificate verification failed"
        exit 1
    }

    setup_renewal
    setup_systemd_renewal
    restart_services
    test_renewal
    display_summary

    log_success "SSL/TLS setup completed successfully!"
}

# Run main function
main "$@"
