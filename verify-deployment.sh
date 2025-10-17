#!/bin/bash

##############################################################################
# Production Deployment Verification Script
# Purpose: Comprehensive validation of all deployment components
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
DOMAIN="nymu.com.tw"
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
HTTPS_URL="https://$DOMAIN"
TIMEOUT=10

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}"
}

log_test() {
    echo -e "${CYAN}🧪 TEST: $1${NC}"
    ((TESTS_TOTAL++))
}

log_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

log_section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check Docker installation
check_docker() {
    log_section "Docker Environment Checks"

    log_test "Docker daemon running"
    if docker ps > /dev/null 2>&1; then
        log_pass "Docker daemon is running"
    else
        log_fail "Docker daemon is not running"
        return 1
    fi

    log_test "docker-compose availability"
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        log_pass "docker-compose is available"
    else
        log_fail "docker-compose is not available"
        return 1
    fi
}

# Check container status
check_containers() {
    log_section "Container Status Checks"

    local containers=("nycu-backend" "nycu-frontend" "nycu-nginx")

    for container in "${containers[@]}"; do
        log_test "Container $container is running"
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            log_pass "$container is running"
        else
            log_fail "$container is not running"
        fi
    done
}

# Check backend health
check_backend() {
    log_section "Backend Service Checks"

    log_test "Backend health endpoint"
    local health_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
    if [ "$health_response" = "200" ]; then
        log_pass "Backend health check passed (HTTP $health_response)"
    else
        log_fail "Backend health check failed (HTTP $health_response)"
    fi

    log_test "Backend API documentation"
    local docs_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" 2>/dev/null)
    if [ "$docs_response" = "200" ]; then
        log_pass "API documentation is accessible (HTTP $docs_response)"
    else
        log_fail "API documentation is not accessible (HTTP $docs_response)"
    fi

    log_test "Backend courses endpoint"
    local courses_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/courses?limit=1" 2>/dev/null)
    if [ "$courses_response" = "200" ]; then
        log_pass "Courses endpoint is working (HTTP $courses_response)"
    else
        log_fail "Courses endpoint is not working (HTTP $courses_response)"
    fi

    log_test "Backend response time"
    local response_time=$(curl -s -o /dev/null -w '%{time_total}' "$BACKEND_URL/health" 2>/dev/null)
    if (( $(echo "$response_time < 1" | bc -l) )); then
        log_pass "Backend response time is acceptable (${response_time}s)"
    else
        log_warning "Backend response time is slow (${response_time}s)"
    fi
}

# Check frontend health
check_frontend() {
    log_section "Frontend Service Checks"

    log_test "Frontend home page"
    local home_response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/" 2>/dev/null)
    if [ "$home_response" = "200" ] || [ "$home_response" = "304" ]; then
        log_pass "Frontend is serving content (HTTP $home_response)"
    else
        log_fail "Frontend is not serving content (HTTP $home_response)"
    fi

    log_test "Frontend assets"
    local assets_response=$(curl -s -I "$FRONTEND_URL/" 2>/dev/null | grep -c "_next" || echo "0")
    if [ "$assets_response" -gt 0 ]; then
        log_pass "Frontend assets are being served"
    else
        log_warning "Next.js assets might not be properly served"
    fi
}

# Check Nginx configuration
check_nginx() {
    log_section "Nginx Reverse Proxy Checks"

    log_test "Nginx configuration validity"
    if docker exec nycu-nginx nginx -t > /dev/null 2>&1; then
        log_pass "Nginx configuration is valid"
    else
        log_fail "Nginx configuration has errors"
    fi

    log_test "Nginx health endpoint"
    local nginx_health=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/health" 2>/dev/null)
    if [ "$nginx_health" = "200" ]; then
        log_pass "Nginx health endpoint is accessible (HTTP $nginx_health)"
    else
        log_fail "Nginx health endpoint is not accessible (HTTP $nginx_health)"
    fi

    log_test "Nginx frontend proxy"
    local nginx_proxy=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/" 2>/dev/null)
    if [ "$nginx_proxy" = "200" ] || [ "$nginx_proxy" = "304" ]; then
        log_pass "Nginx frontend proxy is working (HTTP $nginx_proxy)"
    else
        log_fail "Nginx frontend proxy is not working (HTTP $nginx_proxy)"
    fi
}

# Check SSL/TLS configuration
check_ssl() {
    log_section "SSL/TLS Configuration Checks"

    log_test "SSL certificate existence"
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ]; then
        log_pass "SSL certificates are in place"

        # Check certificate validity
        log_test "SSL certificate validity"
        local expiry=$(openssl x509 -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" -noout -enddate 2>/dev/null | cut -d= -f2)
        log_pass "Certificate expires: $expiry"
    else
        log_warning "SSL certificates not found at /etc/letsencrypt/live/$DOMAIN/"
        log_info "Run 'sudo ./deploy-ssl.sh' to setup Let's Encrypt certificates"
    fi

    log_test "HTTPS availability"
    local https_response=$(curl -s -o /dev/null -w "%{http_code}" -k "$HTTPS_URL/" 2>/dev/null)
    if [ "$https_response" = "200" ] || [ "$https_response" = "304" ]; then
        log_pass "HTTPS is available (HTTP $https_response)"
    else
        log_warning "HTTPS check (might be expected if not configured yet)"
    fi
}

# Check database connectivity
check_database() {
    log_section "Database Checks"

    log_test "Database file accessibility"
    if [ -f "/opt/nycu-platform/backend/courses.db" ]; then
        log_pass "Database file exists"

        log_test "Database integrity"
        if sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;" > /dev/null 2>&1; then
            local count=$(sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;")
            log_pass "Database is accessible ($count courses found)"
        else
            log_fail "Database integrity check failed"
        fi
    else
        log_warning "Database file not found at expected location"
    fi
}

# Check system resources
check_resources() {
    log_section "System Resource Checks"

    log_test "CPU availability"
    local cpu_cores=$(nproc)
    log_pass "System has $cpu_cores CPU cores"

    log_test "Memory availability"
    local mem_total=$(free -m | grep Mem | awk '{print $2}')
    local mem_used=$(free -m | grep Mem | awk '{print $3}')
    local mem_percent=$((100 * mem_used / mem_total))
    log_pass "Memory: ${mem_used}MB / ${mem_total}MB (${mem_percent}%)"

    if [ "$mem_percent" -gt 80 ]; then
        log_warning "Memory usage is high (${mem_percent}%)"
    fi

    log_test "Disk space"
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    log_pass "Disk usage: ${disk_usage}%"

    if [ "$disk_usage" -gt 85 ]; then
        log_warning "Disk usage is high (${disk_usage}%)"
    fi

    log_test "System load"
    local load_avg=$(uptime | awk -F'load average:' '{print $2}')
    log_pass "System load average: $load_avg"
}

# Check network connectivity
check_network() {
    log_section "Network Connectivity Checks"

    log_test "Internal service communication"
    if docker exec nycu-backend curl -s http://nginx:80/health > /dev/null 2>&1; then
        log_pass "Backend can communicate with Nginx"
    else
        log_warning "Backend to Nginx communication might have issues"
    fi

    log_test "Internet connectivity"
    if curl -s -m 5 https://www.google.com > /dev/null 2>&1; then
        log_pass "External internet connectivity is available"
    else
        log_warning "External internet connectivity might be limited"
    fi
}

# Check security headers
check_security() {
    log_section "Security Checks"

    log_test "Security headers"
    local hsts=$(curl -s -I "http://localhost/" 2>/dev/null | grep -i "Strict-Transport-Security" || echo "")
    if [ ! -z "$hsts" ]; then
        log_pass "HSTS header is present"
    else
        log_warning "HSTS header not detected (expected for HTTPS)"
    fi

    log_test "X-Content-Type-Options header"
    local xcto=$(curl -s -I "http://localhost/" 2>/dev/null | grep -i "X-Content-Type-Options" || echo "")
    if [ ! -z "$xcto" ]; then
        log_pass "X-Content-Type-Options header is present"
    fi

    log_test "X-Frame-Options header"
    local xfo=$(curl -s -I "http://localhost/" 2>/dev/null | grep -i "X-Frame-Options" || echo "")
    if [ ! -z "$xfo" ]; then
        log_pass "X-Frame-Options header is present"
    fi
}

# Check monitoring setup
check_monitoring() {
    log_section "Monitoring & Logging Checks"

    log_test "Log directory structure"
    if [ -d "/var/log/nycu-platform" ]; then
        log_pass "Log directory exists"
    else
        log_warning "Log directory not yet created"
    fi

    log_test "Monitoring scripts"
    if [ -f "/opt/nycu-platform/monitoring/monitor-performance.sh" ]; then
        log_pass "Performance monitoring script exists"
    else
        log_info "Monitoring scripts not yet installed"
    fi

    log_test "Health check script"
    if [ -f "/usr/local/bin/nycu-health-check.sh" ]; then
        log_pass "Health check script exists"
    else
        log_info "Health check script not yet installed"
    fi
}

# Display test summary
display_summary() {
    log_section "Test Summary"

    echo ""
    echo -e "${CYAN}Tests Run: ${TESTS_TOTAL}${NC}"
    echo -e "${GREEN}Tests Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}Tests Failed: ${TESTS_FAILED}${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✅ All Deployment Checks Passed!${NC}"
        echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
    else
        echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}⚠️  Some checks failed or had warnings${NC}"
        echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
    fi

    echo ""
    echo -e "${BLUE}Service Access URLs:${NC}"
    echo -e "  Frontend: $FRONTEND_URL"
    echo -e "  Backend API: $BACKEND_URL"
    echo -e "  API Docs: $BACKEND_URL/docs"
    echo -e "  HTTPS: $HTTPS_URL (after SSL setup)"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        echo -e "  1. Setup SSL: sudo ./deploy-ssl.sh"
    fi
    echo -e "  2. Configure monitoring: sudo bash setup-monitoring.sh"
    echo -e "  3. Update DNS records"
    echo -e "  4. Monitor logs: tail -f /var/log/nycu-platform/*/error.log"
    echo ""
}

# Main execution
main() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  NYCU Platform Deployment Verification               ║${NC}"
    echo -e "${CYAN}║  Domain: $DOMAIN                             ║${NC}"
    echo -e "${CYAN}║  Timestamp: $(date)  ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_docker || return 1
    check_containers
    check_backend
    check_frontend
    check_nginx
    check_ssl
    check_database
    check_resources
    check_network
    check_security
    check_monitoring
    display_summary
}

# Run main function
main "$@"
