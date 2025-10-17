#!/bin/bash

##############################################################################
# NYCU Platform - Comprehensive Health Check Script
# Monitors all critical components and sends alerts
##############################################################################

set -e

# Configuration
DOMAIN="nymu.com.tw"
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
DB_PATH="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"
ALERT_EMAIL="admin@nymu.com.tw"
SLACK_WEBHOOK=""  # Add your Slack webhook URL
LOG_FILE="/var/log/nycu-platform/health-check.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Health status
OVERALL_STATUS="healthy"
ISSUES=()

##############################################################################
# LOGGING FUNCTION
##############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a $LOG_FILE
}

##############################################################################
# ALERT FUNCTION
##############################################################################

send_alert() {
    local severity=$1
    local component=$2
    local message=$3

    log "ALERT" "$severity - $component: $message"

    # Email alert
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "[$severity] NYCU Platform Alert - $component" $ALERT_EMAIL 2>/dev/null || true
    fi

    # Slack alert
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\":warning: [$severity] $component: $message\"}" \
            $SLACK_WEBHOOK 2>/dev/null || true
    fi

    # Prometheus alert metric
    echo "nycu_alert{severity=\"$severity\",component=\"$component\"} 1" > /tmp/nycu_alerts.prom
}

##############################################################################
# SYSTEM HEALTH CHECKS
##############################################################################

check_system() {
    log "INFO" "Checking system resources..."

    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
        ISSUES+=("High CPU usage: ${CPU_USAGE}%")
        send_alert "WARNING" "System" "High CPU usage: ${CPU_USAGE}%"
    fi
    log "INFO" "CPU Usage: ${CPU_USAGE}%"

    # Memory usage
    MEM_TOTAL=$(free -m | awk 'NR==2{print $2}')
    MEM_USED=$(free -m | awk 'NR==2{print $3}')
    MEM_PERCENT=$(echo "scale=2; $MEM_USED * 100 / $MEM_TOTAL" | bc)
    if (( $(echo "$MEM_PERCENT > 85" | bc -l) )); then
        ISSUES+=("High memory usage: ${MEM_PERCENT}%")
        send_alert "WARNING" "System" "High memory usage: ${MEM_PERCENT}%"
    fi
    log "INFO" "Memory Usage: ${MEM_PERCENT}% ($MEM_USED MB / $MEM_TOTAL MB)"

    # Disk usage
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 80 ]; then
        ISSUES+=("High disk usage: ${DISK_USAGE}%")
        send_alert "CRITICAL" "System" "High disk usage: ${DISK_USAGE}%"
    fi
    log "INFO" "Disk Usage: ${DISK_USAGE}%"

    # Load average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
    log "INFO" "Load Average: $LOAD_AVG"
}

##############################################################################
# SERVICE HEALTH CHECKS
##############################################################################

check_backend() {
    log "INFO" "Checking backend service..."

    # Check if backend is responding
    if curl -f -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health | grep -q "200"; then
        log "INFO" "Backend is healthy"

        # Check detailed health
        HEALTH_RESPONSE=$(curl -s $BACKEND_URL/health/detailed 2>/dev/null || echo "{}")

        # Parse response time
        RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" $BACKEND_URL/api/courses?limit=1)
        if (( $(echo "$RESPONSE_TIME > 2" | bc -l) )); then
            ISSUES+=("Slow backend response: ${RESPONSE_TIME}s")
            send_alert "WARNING" "Backend" "Slow response time: ${RESPONSE_TIME}s"
        fi
        log "INFO" "Backend response time: ${RESPONSE_TIME}s"
    else
        ISSUES+=("Backend is down")
        OVERALL_STATUS="critical"
        send_alert "CRITICAL" "Backend" "Backend service is not responding"
    fi

    # Check backend process
    if pgrep -f "uvicorn" > /dev/null; then
        BACKEND_PIDS=$(pgrep -f "uvicorn" | wc -l)
        log "INFO" "Backend processes running: $BACKEND_PIDS"
    else
        ISSUES+=("Backend process not running")
        send_alert "CRITICAL" "Backend" "Uvicorn process not found"
    fi
}

check_frontend() {
    log "INFO" "Checking frontend service..."

    # Check if frontend is responding
    if curl -f -s -o /dev/null -w "%{http_code}" $FRONTEND_URL/api/health | grep -q "200"; then
        log "INFO" "Frontend is healthy"

        # Check response time
        RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" $FRONTEND_URL/)
        if (( $(echo "$RESPONSE_TIME > 1" | bc -l) )); then
            ISSUES+=("Slow frontend response: ${RESPONSE_TIME}s")
            send_alert "WARNING" "Frontend" "Slow response time: ${RESPONSE_TIME}s"
        fi
        log "INFO" "Frontend response time: ${RESPONSE_TIME}s"
    else
        ISSUES+=("Frontend is down")
        OVERALL_STATUS="critical"
        send_alert "CRITICAL" "Frontend" "Frontend service is not responding"
    fi

    # Check Node.js process
    if pgrep -f "node.*next" > /dev/null; then
        FRONTEND_PIDS=$(pgrep -f "node.*next" | wc -l)
        log "INFO" "Frontend processes running: $FRONTEND_PIDS"
    else
        ISSUES+=("Frontend process not running")
        send_alert "CRITICAL" "Frontend" "Next.js process not found"
    fi
}

check_nginx() {
    log "INFO" "Checking Nginx..."

    # Check if Nginx is running
    if systemctl is-active --quiet nginx; then
        log "INFO" "Nginx is running"

        # Check Nginx configuration
        if nginx -t 2>/dev/null; then
            log "INFO" "Nginx configuration is valid"
        else
            ISSUES+=("Nginx configuration error")
            send_alert "CRITICAL" "Nginx" "Configuration test failed"
        fi

        # Check Nginx workers
        NGINX_WORKERS=$(ps aux | grep "nginx: worker" | grep -v grep | wc -l)
        log "INFO" "Nginx workers: $NGINX_WORKERS"
    else
        ISSUES+=("Nginx is not running")
        OVERALL_STATUS="critical"
        send_alert "CRITICAL" "Nginx" "Nginx service is down"
    fi
}

##############################################################################
# DATABASE HEALTH CHECKS
##############################################################################

check_database() {
    log "INFO" "Checking database..."

    if [ -f "$DB_PATH" ]; then
        # Check database size
        DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
        log "INFO" "Database size: $DB_SIZE"

        # Check database integrity
        INTEGRITY=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>/dev/null || echo "failed")
        if [ "$INTEGRITY" = "ok" ]; then
            log "INFO" "Database integrity check passed"
        else
            ISSUES+=("Database integrity check failed")
            send_alert "CRITICAL" "Database" "Integrity check failed"
        fi

        # Check record count
        COURSE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM courses;" 2>/dev/null || echo "0")
        log "INFO" "Total courses in database: $COURSE_COUNT"

        if [ "$COURSE_COUNT" -lt 70000 ]; then
            ISSUES+=("Low course count: $COURSE_COUNT")
            send_alert "WARNING" "Database" "Course count below expected: $COURSE_COUNT"
        fi

        # Check query performance
        START_TIME=$(date +%s%N)
        sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM courses WHERE semester='113-1';" > /dev/null 2>&1
        END_TIME=$(date +%s%N)
        QUERY_TIME=$(echo "scale=3; ($END_TIME - $START_TIME) / 1000000000" | bc)

        if (( $(echo "$QUERY_TIME > 1" | bc -l) )); then
            ISSUES+=("Slow database query: ${QUERY_TIME}s")
            send_alert "WARNING" "Database" "Slow query performance: ${QUERY_TIME}s"
        fi
        log "INFO" "Database query time: ${QUERY_TIME}s"
    else
        ISSUES+=("Database file not found")
        OVERALL_STATUS="critical"
        send_alert "CRITICAL" "Database" "Database file not found at $DB_PATH"
    fi
}

##############################################################################
# SSL CERTIFICATE CHECK
##############################################################################

check_ssl() {
    log "INFO" "Checking SSL certificate..."

    # Check certificate expiration
    CERT_CHECK=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -checkend 604800)

    if [ $? -eq 0 ]; then
        log "INFO" "SSL certificate valid for more than 7 days"
    else
        ISSUES+=("SSL certificate expiring soon")
        send_alert "WARNING" "SSL" "Certificate expiring within 7 days"
    fi

    # Get exact expiry date
    EXPIRY_DATE=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    log "INFO" "SSL certificate expires: $EXPIRY_DATE"
}

##############################################################################
# BACKUP CHECK
##############################################################################

check_backups() {
    log "INFO" "Checking backups..."

    BACKUP_DIR="/var/backups/nycu-platform"

    if [ -d "$BACKUP_DIR" ]; then
        # Check for recent backup
        LATEST_BACKUP=$(find $BACKUP_DIR -name "*.db.gz" -type f -mtime -1 | head -1)

        if [ -z "$LATEST_BACKUP" ]; then
            ISSUES+=("No recent backup found (24h)")
            send_alert "WARNING" "Backup" "No backup created in last 24 hours"
        else
            BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
            log "INFO" "Latest backup: $(basename $LATEST_BACKUP) ($BACKUP_SIZE)"
        fi

        # Check backup disk space
        BACKUP_SPACE=$(df -h $BACKUP_DIR | awk 'NR==2 {print $4}')
        log "INFO" "Backup directory free space: $BACKUP_SPACE"
    else
        ISSUES+=("Backup directory not found")
        send_alert "WARNING" "Backup" "Backup directory does not exist"
    fi
}

##############################################################################
# LOG CHECK
##############################################################################

check_logs() {
    log "INFO" "Checking logs for errors..."

    # Check for recent errors in backend log
    if [ -f "/tmp/backend.log" ]; then
        ERROR_COUNT=$(grep -c "ERROR" /tmp/backend.log 2>/dev/null || echo "0")
        if [ "$ERROR_COUNT" -gt 100 ]; then
            ISSUES+=("High error count in backend log: $ERROR_COUNT")
            send_alert "WARNING" "Logs" "High error count in backend: $ERROR_COUNT"
        fi
    fi

    # Check for recent errors in frontend log
    if [ -f "/tmp/frontend.log" ]; then
        ERROR_COUNT=$(grep -c "Error" /tmp/frontend.log 2>/dev/null || echo "0")
        if [ "$ERROR_COUNT" -gt 100 ]; then
            ISSUES+=("High error count in frontend log: $ERROR_COUNT")
            send_alert "WARNING" "Logs" "High error count in frontend: $ERROR_COUNT"
        fi
    fi

    # Check log sizes
    for logfile in /tmp/*.log /var/log/nginx/*.log; do
        if [ -f "$logfile" ]; then
            SIZE=$(du -m "$logfile" | cut -f1)
            if [ "$SIZE" -gt 1000 ]; then
                ISSUES+=("Large log file: $(basename $logfile) (${SIZE}MB)")
                log "WARNING" "Large log file: $logfile (${SIZE}MB)"
            fi
        fi
    done
}

##############################################################################
# PERFORMANCE METRICS
##############################################################################

collect_metrics() {
    log "INFO" "Collecting performance metrics..."

    # Write metrics for Prometheus
    cat > /tmp/nycu_health_metrics.prom << EOF
# HELP nycu_health_check Health check status (1=healthy, 0=unhealthy)
# TYPE nycu_health_check gauge
nycu_health_check{component="system"} $([ ${#ISSUES[@]} -eq 0 ] && echo 1 || echo 0)
nycu_health_check{component="backend"} $(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health | grep -q "200" && echo 1 || echo 0)
nycu_health_check{component="frontend"} $(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL/api/health | grep -q "200" && echo 1 || echo 0)
nycu_health_check{component="database"} $([ -f "$DB_PATH" ] && echo 1 || echo 0)

# HELP nycu_issue_count Number of health issues detected
# TYPE nycu_issue_count gauge
nycu_issue_count ${#ISSUES[@]}
EOF

    # Copy to Prometheus node exporter directory if it exists
    if [ -d "/var/lib/prometheus/node-exporter" ]; then
        cp /tmp/nycu_health_metrics.prom /var/lib/prometheus/node-exporter/
    fi
}

##############################################################################
# MAIN EXECUTION
##############################################################################

main() {
    log "INFO" "========================================="
    log "INFO" "Starting NYCU Platform Health Check"
    log "INFO" "========================================="

    # Run all checks
    check_system
    check_backend
    check_frontend
    check_nginx
    check_database
    check_ssl
    check_backups
    check_logs
    collect_metrics

    # Summary
    log "INFO" "========================================="
    if [ ${#ISSUES[@]} -eq 0 ]; then
        log "INFO" "Health Check Result: ALL SYSTEMS HEALTHY"
        echo -e "${GREEN}✓ All systems healthy${NC}"
    else
        log "WARNING" "Health Check Result: ISSUES DETECTED"
        echo -e "${YELLOW}⚠ Issues detected:${NC}"
        for issue in "${ISSUES[@]}"; do
            echo -e "${RED}  - $issue${NC}"
            log "WARNING" "Issue: $issue"
        done
    fi
    log "INFO" "========================================="

    # Exit with appropriate code
    if [ "$OVERALL_STATUS" = "critical" ]; then
        exit 2
    elif [ ${#ISSUES[@]} -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main