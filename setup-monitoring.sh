#!/bin/bash

##############################################################################
# Monitoring and Logging Setup for NYCU Course Platform
# Purpose: Configure comprehensive monitoring, logging, and alerting
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
LOG_DIR="/var/log/nycu-platform"
MONITORING_DIR="/opt/nycu-platform/monitoring"
DOMAIN="nymu.com.tw"

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

# Create log directories
setup_logging() {
    log_info "Setting up logging infrastructure..."

    mkdir -p "$LOG_DIR"/{backend,frontend,nginx,system}
    mkdir -p /var/log/nycu-platform/{api,errors,performance}

    # Setup log rotation
    cat > /etc/logrotate.d/nycu-platform << 'EOF'
/var/log/nycu-platform/**/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}

/var/log/nycu-platform/nginx/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        docker exec nycu-nginx nginx -s reload > /dev/null 2>&1 || true
    endscript
}
EOF

    log_success "Logging configured"
}

# Setup performance monitoring script
setup_performance_monitoring() {
    log_info "Setting up performance monitoring..."

    mkdir -p "$MONITORING_DIR"

    cat > "$MONITORING_DIR/monitor-performance.sh" << 'EOF'
#!/bin/bash

# Performance Monitoring Script
LOG_FILE="/var/log/nycu-platform/performance/metrics.log"
mkdir -p $(dirname "$LOG_FILE")

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# System metrics
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}' | cut -d'.' -f1)
MEM_TOTAL=$(free | grep Mem | awk '{print $2}')
MEM_USED=$(free | grep Mem | awk '{print $3}')
MEM_PERCENT=$((100 * MEM_USED / MEM_TOTAL))
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')

# Docker metrics
BACKEND_STATUS=$(docker inspect nycu-backend --format='{{.State.Status}}' 2>/dev/null || echo "unknown")
FRONTEND_STATUS=$(docker inspect nycu-frontend --format='{{.State.Status}}' 2>/dev/null || echo "unknown")
NGINX_STATUS=$(docker inspect nycu-nginx --format='{{.State.Status}}' 2>/dev/null || echo "unknown")

# API response time
API_RESPONSE_TIME=$(curl -s -o /dev/null -w '%{time_total}' http://localhost:8000/health 2>/dev/null || echo "unknown")

# Log metrics
echo "[$TIMESTAMP] CPU: ${CPU_USAGE}% | MEM: ${MEM_PERCENT}% (${MEM_USED}MB/${MEM_TOTAL}MB) | DISK: ${DISK_USAGE}% | LOAD: ${LOAD_AVG}" >> "$LOG_FILE"
echo "[$TIMESTAMP] Backend: $BACKEND_STATUS | Frontend: $FRONTEND_STATUS | Nginx: $NGINX_STATUS | API Response: ${API_RESPONSE_TIME}s" >> "$LOG_FILE"

# Alert thresholds
if [ "$CPU_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] ALERT: High CPU usage: ${CPU_USAGE}%" >> "$LOG_FILE"
fi

if [ "$MEM_PERCENT" -gt 80 ]; then
    echo "[$TIMESTAMP] ALERT: High memory usage: ${MEM_PERCENT}%" >> "$LOG_FILE"
fi

if [ "$DISK_USAGE" -gt 85 ]; then
    echo "[$TIMESTAMP] ALERT: High disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
fi

if [[ "$BACKEND_STATUS" != "running" ]]; then
    echo "[$TIMESTAMP] ALERT: Backend container not running" >> "$LOG_FILE"
fi

if [[ "$FRONTEND_STATUS" != "running" ]]; then
    echo "[$TIMESTAMP] ALERT: Frontend container not running" >> "$LOG_FILE"
fi
EOF

    chmod +x "$MONITORING_DIR/monitor-performance.sh"
    log_success "Performance monitoring script created"
}

# Setup API metrics collection
setup_api_monitoring() {
    log_info "Setting up API monitoring..."

    cat > "$MONITORING_DIR/monitor-api.sh" << 'EOF'
#!/bin/bash

# API Health Check and Metrics
LOG_FILE="/var/log/nycu-platform/api/health.log"
METRICS_FILE="/var/log/nycu-platform/api/metrics.log"
mkdir -p $(dirname "$LOG_FILE")

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DOMAIN="nymu.com.tw"
API_URL="http://localhost:8000"

# Health check endpoints
check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "$API_URL$endpoint" 2>/dev/null)

    if [ "$response" = "$expected_status" ]; then
        echo "✅ $endpoint: $response"
        return 0
    else
        echo "❌ $endpoint: Expected $expected_status, got $response"
        echo "[$TIMESTAMP] ALERT: $endpoint returned status $response" >> "$LOG_FILE"
        return 1
    fi
}

# Check key endpoints
echo "[$TIMESTAMP] API Health Check" >> "$LOG_FILE"
check_endpoint "/health" "200"
check_endpoint "/docs" "200"
check_endpoint "/api/v1/courses" "200"
check_endpoint "/api/v1/search" "405"  # POST only

# Database connectivity
DB_CHECK=$(sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;" 2>/dev/null || echo "error")
echo "[$TIMESTAMP] Database: $DB_CHECK records" >> "$METRICS_FILE"
EOF

    chmod +x "$MONITORING_DIR/monitor-api.sh"
    log_success "API monitoring script created"
}

# Setup log aggregation
setup_log_aggregation() {
    log_info "Setting up log aggregation..."

    cat > "$MONITORING_DIR/aggregate-logs.sh" << 'EOF'
#!/bin/bash

# Log Aggregation Script
SUMMARY_FILE="/var/log/nycu-platform/daily-summary.log"
TIMESTAMP=$(date '+%Y-%m-%d')

echo "" >> "$SUMMARY_FILE"
echo "═════════════════════════════════════════" >> "$SUMMARY_FILE"
echo "Daily Summary: $TIMESTAMP" >> "$SUMMARY_FILE"
echo "═════════════════════════════════════════" >> "$SUMMARY_FILE"

# Error count
ERROR_COUNT=$(grep -r "ERROR\|error\|Error" /var/log/nycu-platform/ 2>/dev/null | wc -l || echo "0")
echo "Errors: $ERROR_COUNT" >> "$SUMMARY_FILE"

# Warning count
WARN_COUNT=$(grep -r "WARNING\|warning\|Warning" /var/log/nycu-platform/ 2>/dev/null | wc -l || echo "0")
echo "Warnings: $WARN_COUNT" >> "$SUMMARY_FILE"

# Request count (if available)
REQ_COUNT=$(grep -r "GET\|POST\|PUT\|DELETE" /var/log/nycu-platform/nginx/ 2>/dev/null | wc -l || echo "0")
echo "Requests: $REQ_COUNT" >> "$SUMMARY_FILE"

# Service status
docker ps --format "{{.Names}}: {{.Status}}" | grep nycu >> "$SUMMARY_FILE" 2>/dev/null || echo "No containers running" >> "$SUMMARY_FILE"
EOF

    chmod +x "$MONITORING_DIR/aggregate-logs.sh"
    log_success "Log aggregation script created"
}

# Setup cron jobs for monitoring
setup_monitoring_crons() {
    log_info "Setting up monitoring cron jobs..."

    CRON_JOBS="
*/5 * * * * /opt/nycu-platform/monitoring/monitor-performance.sh
*/10 * * * * /opt/nycu-platform/monitoring/monitor-api.sh
0 0 * * * /opt/nycu-platform/monitoring/aggregate-logs.sh
"

    # Add to crontab if not present
    if ! crontab -l 2>/dev/null | grep -q "monitor-performance.sh"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -
        log_success "Monitoring cron jobs installed"
    else
        log_info "Monitoring cron jobs already present"
    fi
}

# Setup alerting
setup_alerting() {
    log_info "Setting up alerting system..."

    cat > "$MONITORING_DIR/check-alerts.sh" << 'EOF'
#!/bin/bash

# Alert Check Script
ALERT_LOG="/var/log/nycu-platform/alerts.log"
CRITICAL_ALERTS=$(grep -c "ALERT:" /var/log/nycu-platform/*/*.log 2>/dev/null || echo "0")

if [ "$CRITICAL_ALERTS" -gt 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $CRITICAL_ALERTS alerts detected" >> "$ALERT_LOG"

    # Email notification (if configured)
    if command -v mail &> /dev/null && [ ! -z "$ALERT_EMAIL" ]; then
        ALERTS=$(grep "ALERT:" /var/log/nycu-platform/*/*.log 2>/dev/null | tail -10)
        echo "Recent Alerts:
$ALERTS" | mail -s "NYCU Platform Alerts" "$ALERT_EMAIL"
    fi
fi
EOF

    chmod +x "$MONITORING_DIR/check-alerts.sh"
    log_success "Alerting system configured"
}

# Create monitoring dashboard generator
setup_dashboard() {
    log_info "Setting up monitoring dashboard..."

    cat > "$MONITORING_DIR/generate-dashboard.sh" << 'EOF'
#!/bin/bash

# Generate HTML Dashboard
DASHBOARD="/var/www/html/monitoring/dashboard.html"
mkdir -p $(dirname "$DASHBOARD")

cat > "$DASHBOARD" << 'DASHBOARD_EOF'
<!DOCTYPE html>
<html>
<head>
    <title>NYCU Platform - Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .header { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .metric { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status-ok { color: #28a745; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .status-error { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NYCU Platform Monitoring Dashboard</h1>
        <p>Last updated: <span id="timestamp"></span></p>
    </div>

    <div class="metric">
        <h3>System Status</h3>
        <p>CPU Usage: <span id="cpu-usage"></span></p>
        <p>Memory Usage: <span id="mem-usage"></span></p>
        <p>Disk Usage: <span id="disk-usage"></span></p>
    </div>

    <div class="metric">
        <h3>Service Status</h3>
        <p>Backend: <span id="backend-status"></span></p>
        <p>Frontend: <span id="frontend-status"></span></p>
        <p>Nginx: <span id="nginx-status"></span></p>
    </div>

    <div class="metric">
        <h3>Recent Logs</h3>
        <pre id="recent-logs"></pre>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(loadMetrics, 30000);
        loadMetrics();

        function loadMetrics() {
            fetch('/api/monitoring/metrics')
                .then(r => r.json())
                .then(data => updateDashboard(data));
        }

        function updateDashboard(data) {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
            document.getElementById('cpu-usage').textContent = data.cpu || 'N/A';
            document.getElementById('mem-usage').textContent = data.memory || 'N/A';
            document.getElementById('disk-usage').textContent = data.disk || 'N/A';
            document.getElementById('backend-status').textContent = data.backend || 'N/A';
            document.getElementById('frontend-status').textContent = data.frontend || 'N/A';
            document.getElementById('nginx-status').textContent = data.nginx || 'N/A';
        }
    </script>
</body>
</html>
DASHBOARD_EOF

    log_success "Monitoring dashboard created at $DASHBOARD"
}

# Display summary
display_summary() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Monitoring and Logging Setup Complete${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Configured Components:${NC}"
    echo -e "  ✅ Centralized logging at: $LOG_DIR"
    echo -e "  ✅ Performance monitoring (every 5 min)"
    echo -e "  ✅ API health checks (every 10 min)"
    echo -e "  ✅ Daily log aggregation"
    echo -e "  ✅ Alert system configured"
    echo -e "  ✅ Log rotation (30 days)"
    echo ""
    echo -e "${BLUE}Log Locations:${NC}"
    echo -e "  Backend: $LOG_DIR/backend/"
    echo -e "  Frontend: $LOG_DIR/frontend/"
    echo -e "  Nginx: $LOG_DIR/nginx/"
    echo -e "  Performance: $LOG_DIR/performance/metrics.log"
    echo -e "  API: $LOG_DIR/api/health.log"
    echo ""
    echo -e "${BLUE}Monitoring Scripts:${NC}"
    echo -e "  $MONITORING_DIR/monitor-performance.sh"
    echo -e "  $MONITORING_DIR/monitor-api.sh"
    echo -e "  $MONITORING_DIR/aggregate-logs.sh"
    echo -e "  $MONITORING_DIR/check-alerts.sh"
    echo ""
    echo -e "${BLUE}View Logs:${NC}"
    echo -e "  tail -f $LOG_DIR/system/system.log"
    echo -e "  tail -f $LOG_DIR/performance/metrics.log"
    echo ""
}

# Main execution
main() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Monitoring & Logging Setup                         ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""

    setup_logging
    setup_performance_monitoring
    setup_api_monitoring
    setup_log_aggregation
    setup_monitoring_crons
    setup_alerting
    setup_dashboard
    display_summary

    log_success "Monitoring setup completed successfully!"
}

main "$@"
