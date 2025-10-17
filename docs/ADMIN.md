# NYCU Course Platform - Administrator Guide

Comprehensive guide for system administrators managing the NYCU Course Platform.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Monitoring Procedures](#monitoring-procedures)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)
- [Log Management](#log-management)
- [Database Maintenance](#database-maintenance)
- [Security Management](#security-management)
- [Scaling Guidelines](#scaling-guidelines)

## Overview

### Platform Information

**Production Environment:**
- **Domain:** nymu.com.tw
- **Server:** 31.41.34.19
- **Total Courses:** 70,239
- **Academic Semesters:** 9 (110-1 through 114-1)
- **Uptime Target:** 99.9%

**Technology Stack:**
- Frontend: Next.js 14 + React 18 (Port 3000)
- Backend: FastAPI + Uvicorn (Port 8000, 4 workers)
- Reverse Proxy: Nginx (Ports 80, 443, 31 workers)
- Database: SQLite
- SSL: Let's Encrypt

### Administrator Responsibilities

- System monitoring and health checks
- Backup and disaster recovery
- Performance optimization
- Security management
- Log analysis and troubleshooting
- Database maintenance
- Service management
- User support escalation

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────┐
│                  Internet Users                     │
│              https://nymu.com.tw                    │
└────────────────────┬────────────────────────────────┘
                     │
              ┌──────▼──────┐
              │  Cloudflare │
              │   DNS + CDN │
              └──────┬──────┘
                     │
         ┌───────────▼──────────┐
         │   Nginx (80, 443)    │
         │   31 Workers         │
         │   Rate Limiting      │
         └───┬──────────────┬───┘
             │              │
    ┌────────▼──────┐  ┌────▼─────────┐
    │  Frontend     │  │  Backend     │
    │  Next.js      │  │  FastAPI     │
    │  Port 3000    │  │  Port 8000   │
    └────────┬──────┘  └────┬─────────┘
             │              │
             └──────┬───────┘
                    │
            ┌───────▼────────┐
            │  SQLite DB     │
            │  70,239 courses│
            └────────────────┘
```

### Service Dependencies

```
nginx → depends on: nothing (reverse proxy)
  ├─> frontend → depends on: backend API
  └─> backend → depends on: database file
```

### File Locations

**Application:**
```
/home/thc1006/dev/nycu_course_platform/
├── backend/               # Backend application
│   ├── app/              # Application code
│   ├── venv/             # Python virtual environment
│   └── requirements.txt  # Dependencies
├── frontend/             # Frontend application
│   ├── pages/           # Next.js pages
│   ├── components/      # React components
│   ├── .next/           # Build output
│   └── package.json     # Dependencies
└── nycu_course_platform.db  # SQLite database (70,239 courses)
```

**Configuration:**
```
/etc/nginx/sites-available/nycu-platform    # Nginx config
/etc/systemd/system/nycu-backend.service    # Backend service
/etc/systemd/system/nycu-frontend.service   # Frontend service
/etc/letsencrypt/live/nymu.com.tw/          # SSL certificates
```

**Logs:**
```
/var/log/nginx/access.log                   # Nginx access logs
/var/log/nginx/error.log                    # Nginx error logs
/var/log/nycu-platform/backend.log          # Backend logs
/var/log/nycu-platform/frontend.log         # Frontend logs
```

## Monitoring Procedures

### Daily Health Checks

#### Automated Health Check Script

Create `/home/thc1006/scripts/health-check.sh`:

```bash
#!/bin/bash

# NYCU Platform Health Check Script
# Run every 5 minutes via cron

LOG_FILE="/var/log/nycu-platform/health-check.log"
ALERT_EMAIL="admin@nycu.edu.tw"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

send_alert() {
    echo "$1" | mail -s "NYCU Platform Alert" "$ALERT_EMAIL"
}

# Check Backend Health
check_backend() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$response" != "200" ]; then
        log_message "ERROR: Backend health check failed (HTTP $response)"
        send_alert "Backend service is not responding. HTTP status: $response"
        return 1
    fi
    log_message "OK: Backend health check passed"
    return 0
}

# Check Frontend
check_frontend() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    if [ "$response" != "200" ]; then
        log_message "ERROR: Frontend health check failed (HTTP $response)"
        send_alert "Frontend service is not responding. HTTP status: $response"
        return 1
    fi
    log_message "OK: Frontend health check passed"
    return 0
}

# Check Nginx
check_nginx() {
    if ! systemctl is-active --quiet nginx; then
        log_message "ERROR: Nginx is not running"
        send_alert "Nginx service is down"
        return 1
    fi
    log_message "OK: Nginx is running"
    return 0
}

# Check SSL Certificate Expiry
check_ssl() {
    expiry_date=$(echo | openssl s_client -connect nymu.com.tw:443 -servername nymu.com.tw 2>/dev/null | \
                  openssl x509 -noout -enddate | cut -d= -f2)
    expiry_epoch=$(date -d "$expiry_date" +%s)
    current_epoch=$(date +%s)
    days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))

    if [ $days_until_expiry -lt 30 ]; then
        log_message "WARNING: SSL certificate expires in $days_until_expiry days"
        send_alert "SSL certificate expires in $days_until_expiry days"
    else
        log_message "OK: SSL certificate valid for $days_until_expiry days"
    fi
}

# Check Database
check_database() {
    if [ ! -f "/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db" ]; then
        log_message "ERROR: Database file not found"
        send_alert "Database file is missing"
        return 1
    fi

    course_count=$(sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
                   "SELECT COUNT(*) FROM course;" 2>/dev/null)

    if [ -z "$course_count" ]; then
        log_message "ERROR: Cannot query database"
        send_alert "Database query failed"
        return 1
    fi

    if [ "$course_count" -ne 70239 ]; then
        log_message "WARNING: Course count is $course_count (expected 70239)"
        send_alert "Course count mismatch: $course_count"
    else
        log_message "OK: Database contains $course_count courses"
    fi
}

# Check Disk Space
check_disk() {
    usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 90 ]; then
        log_message "ERROR: Disk usage is ${usage}%"
        send_alert "Disk usage critical: ${usage}%"
        return 1
    elif [ $usage -gt 80 ]; then
        log_message "WARNING: Disk usage is ${usage}%"
    else
        log_message "OK: Disk usage is ${usage}%"
    fi
}

# Check Memory
check_memory() {
    available=$(free | grep Mem | awk '{print $7}')
    total=$(free | grep Mem | awk '{print $2}')
    percentage=$(( ($available * 100) / $total ))

    if [ $percentage -lt 10 ]; then
        log_message "ERROR: Low memory: ${percentage}% available"
        send_alert "Low memory: ${percentage}% available"
        return 1
    elif [ $percentage -lt 20 ]; then
        log_message "WARNING: Memory running low: ${percentage}% available"
    else
        log_message "OK: Memory available: ${percentage}%"
    fi
}

# Run all checks
log_message "===== Starting Health Check ====="
check_nginx
check_backend
check_frontend
check_ssl
check_database
check_disk
check_memory
log_message "===== Health Check Complete ====="
```

Make executable and schedule:

```bash
chmod +x /home/thc1006/scripts/health-check.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /home/thc1006/scripts/health-check.sh
```

### Manual Monitoring Commands

#### Service Status

```bash
# Check all services
sudo systemctl status nginx nycu-backend nycu-frontend

# Check service uptime
systemctl show nycu-backend --property=ActiveEnterTimestamp
systemctl show nycu-frontend --property=ActiveEnterTimestamp

# View real-time status
watch -n 2 'systemctl status nginx nycu-backend nycu-frontend'
```

#### Resource Usage

```bash
# CPU and Memory
htop
top

# Disk I/O
iotop

# Network traffic
nethogs

# Detailed process info
ps aux | grep -E '(uvicorn|node|nginx)'

# System load
uptime
w
```

#### API Performance

```bash
# Test API response time
time curl -s http://localhost:8000/health
time curl -s http://localhost:8000/api/semesters/
time curl -s "http://localhost:8000/api/courses/?limit=50"

# Continuous monitoring
watch -n 5 'time curl -s http://localhost:8000/health'

# Load testing
ab -n 1000 -c 10 http://localhost:8000/api/courses/
```

#### Database Monitoring

```bash
# Database size
du -h /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Course count
sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
  "SELECT COUNT(*) FROM course;"

# Check integrity
sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
  "PRAGMA integrity_check;"

# Database statistics
sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
  "SELECT
    (SELECT COUNT(*) FROM course) as total_courses,
    (SELECT COUNT(*) FROM semester) as total_semesters;"
```

### Monitoring Dashboard

Create a simple monitoring dashboard:

```bash
# Create dashboard script
cat > /home/thc1006/scripts/dashboard.sh << 'EOF'
#!/bin/bash

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          NYCU Course Platform - Admin Dashboard               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# System Info
echo "📊 SYSTEM STATUS"
echo "────────────────────────────────────────────────────────────────"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# Services
echo "🔧 SERVICES"
echo "────────────────────────────────────────────────────────────────"
systemctl is-active nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Stopped"
systemctl is-active nycu-backend && echo "✅ Backend: Running" || echo "❌ Backend: Stopped"
systemctl is-active nycu-frontend && echo "✅ Frontend: Running" || echo "❌ Frontend: Stopped"
echo ""

# Health Checks
echo "🏥 HEALTH CHECKS"
echo "────────────────────────────────────────────────────────────────"
backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
echo "Backend API: HTTP $backend_status"
echo "Frontend App: HTTP $frontend_status"
echo ""

# Database
echo "💾 DATABASE"
echo "────────────────────────────────────────────────────────────────"
db_path="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"
if [ -f "$db_path" ]; then
    db_size=$(du -h "$db_path" | cut -f1)
    course_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM course;" 2>/dev/null || echo "N/A")
    echo "Database Size: $db_size"
    echo "Total Courses: $course_count"
else
    echo "❌ Database file not found"
fi
echo ""

# Resources
echo "💻 RESOURCES"
echo "────────────────────────────────────────────────────────────────"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo ""

# Recent Errors
echo "⚠️  RECENT ERRORS (Last 10)"
echo "────────────────────────────────────────────────────────────────"
sudo journalctl -u nycu-backend -u nycu-frontend --priority=err --since="1 hour ago" --no-pager | tail -10
echo ""

echo "Last updated: $(date)"
EOF

chmod +x /home/thc1006/scripts/dashboard.sh

# Run dashboard
/home/thc1006/scripts/dashboard.sh
```

## Backup and Recovery

### Automated Backup Strategy

#### Full System Backup

```bash
# Create comprehensive backup script
cat > /home/thc1006/scripts/full-backup.sh << 'EOF'
#!/bin/bash

# NYCU Platform Full Backup Script
# Run daily at 2 AM

BACKUP_ROOT="/home/thc1006/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"
LOG_FILE="$BACKUP_ROOT/backup.log"

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting full backup..."

# Backup database
log "Backing up database..."
cp /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
   "$BACKUP_DIR/nycu_course_platform.db"

# Backup configuration files
log "Backing up configuration..."
mkdir -p "$BACKUP_DIR/config"
cp /etc/nginx/sites-available/nycu-platform "$BACKUP_DIR/config/"
cp /etc/systemd/system/nycu-*.service "$BACKUP_DIR/config/"

# Backup environment files
log "Backing up environment files..."
cp /home/thc1006/dev/nycu_course_platform/backend/.env "$BACKUP_DIR/" 2>/dev/null
cp /home/thc1006/dev/nycu_course_platform/frontend/.env.production "$BACKUP_DIR/" 2>/dev/null

# Backup logs (last 7 days)
log "Backing up logs..."
mkdir -p "$BACKUP_DIR/logs"
find /var/log/nycu-platform/ -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/logs/" \;

# Create metadata file
log "Creating metadata..."
cat > "$BACKUP_DIR/metadata.txt" << METADATA
Backup Date: $(date)
Server: $(hostname)
Database Size: $(du -h "$BACKUP_DIR/nycu_course_platform.db" | cut -f1)
Course Count: $(sqlite3 "$BACKUP_DIR/nycu_course_platform.db" "SELECT COUNT(*) FROM course;")
Nginx Version: $(nginx -v 2>&1)
Backend Status: $(systemctl is-active nycu-backend)
Frontend Status: $(systemctl is-active nycu-frontend)
METADATA

# Compress backup
log "Compressing backup..."
cd "$BACKUP_ROOT"
tar -czf "${DATE}.tar.gz" "$DATE"
rm -rf "$DATE"

# Calculate checksum
log "Calculating checksum..."
sha256sum "${DATE}.tar.gz" > "${DATE}.tar.gz.sha256"

# Upload to remote storage (optional)
# rsync -avz "${DATE}.tar.gz" user@remote-server:/backups/

# Cleanup old backups (keep last 30 days)
log "Cleaning up old backups..."
find "$BACKUP_ROOT" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_ROOT" -name "*.sha256" -mtime +30 -delete

# Get backup size
BACKUP_SIZE=$(du -h "${DATE}.tar.gz" | cut -f1)
log "Backup completed: ${DATE}.tar.gz (${BACKUP_SIZE})"

# Send notification (optional)
# echo "Backup completed: ${DATE}.tar.gz (${BACKUP_SIZE})" | \
#   mail -s "NYCU Platform Backup Complete" admin@nycu.edu.tw

log "Full backup finished successfully"
EOF

chmod +x /home/thc1006/scripts/full-backup.sh

# Schedule daily backup
crontab -e
# Add: 0 2 * * * /home/thc1006/scripts/full-backup.sh
```

#### Database-Only Backup (Lightweight)

```bash
# Quick database backup
cat > /home/thc1006/scripts/backup-db-quick.sh << 'EOF'
#!/bin/bash

DB_SOURCE="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"
BACKUP_DIR="/home/thc1006/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nycu_db_$TIMESTAMP.db"

mkdir -p "$BACKUP_DIR"

# Create backup
cp "$DB_SOURCE" "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Verify
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "✅ Backup created: $BACKUP_FILE.gz"
    ls -lh "$BACKUP_FILE.gz"
else
    echo "❌ Backup failed"
    exit 1
fi

# Cleanup old backups (keep last 14 days)
find "$BACKUP_DIR" -name "nycu_db_*.db.gz" -mtime +14 -delete

echo "Database backup completed successfully"
EOF

chmod +x /home/thc1006/scripts/backup-db-quick.sh
```

### Recovery Procedures

#### Complete System Recovery

```bash
#!/bin/bash
# Complete system recovery from backup

# Stop services
echo "Stopping services..."
sudo systemctl stop nycu-backend nycu-frontend nginx

# Extract backup
BACKUP_FILE="/home/thc1006/backups/20251017_020000.tar.gz"
RESTORE_DIR="/tmp/restore"

echo "Extracting backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Restore database
echo "Restoring database..."
cp "$RESTORE_DIR"/*/nycu_course_platform.db \
   /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Restore configuration
echo "Restoring configuration..."
sudo cp "$RESTORE_DIR"/*/config/nycu-platform \
        /etc/nginx/sites-available/nycu-platform
sudo cp "$RESTORE_DIR"/*/config/nycu-*.service \
        /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Test configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Start services
echo "Starting services..."
sudo systemctl start nginx
sudo systemctl start nycu-backend
sudo systemctl start nycu-frontend

# Verify
echo "Verifying services..."
sleep 5
systemctl is-active nginx && echo "✅ Nginx running"
systemctl is-active nycu-backend && echo "✅ Backend running"
systemctl is-active nycu-frontend && echo "✅ Frontend running"

# Test API
curl -s http://localhost:8000/health | grep "healthy" && echo "✅ API responding"

echo "Recovery completed"
```

#### Database-Only Recovery

```bash
#!/bin/bash
# Restore database only

# Stop backend
sudo systemctl stop nycu-backend

# Backup current database
cp /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
   /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db.before-restore

# Restore from backup
BACKUP="/home/thc1006/backups/database/nycu_db_20251017_020000.db.gz"
gunzip -c "$BACKUP" > /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Verify integrity
sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db "PRAGMA integrity_check;"

# Check course count
COURSE_COUNT=$(sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db \
               "SELECT COUNT(*) FROM course;")
echo "Course count after restore: $COURSE_COUNT"

if [ "$COURSE_COUNT" -eq 70239 ]; then
    echo "✅ Database restored successfully"
    # Start backend
    sudo systemctl start nycu-backend
else
    echo "❌ Course count mismatch. Rolling back..."
    cp /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db.before-restore \
       /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db
    sudo systemctl start nycu-backend
    exit 1
fi
```

### Disaster Recovery Plan

#### Scenario 1: Database Corruption

```bash
# 1. Stop backend
sudo systemctl stop nycu-backend

# 2. Check database integrity
sqlite3 nycu_course_platform.db "PRAGMA integrity_check;"

# 3. If corrupted, restore from backup
cp /home/thc1006/backups/database/latest.db.gz /tmp/
gunzip /tmp/latest.db.gz
mv /tmp/latest.db nycu_course_platform.db

# 4. Verify
sqlite3 nycu_course_platform.db "SELECT COUNT(*) FROM course;"

# 5. Restart backend
sudo systemctl start nycu-backend
```

#### Scenario 2: Complete Server Failure

```
1. Provision new server with same specs
2. Install required software (Python, Node.js, Nginx)
3. Clone repository
4. Restore latest backup
5. Configure domain DNS to point to new server
6. Update SSL certificates
7. Start services
8. Verify functionality
9. Update monitoring systems
```

#### Scenario 3: SSL Certificate Expiry

```bash
# Emergency SSL renewal
sudo certbot renew --force-renewal
sudo systemctl reload nginx

# Verify
echo | openssl s_client -connect nymu.com.tw:443 | grep "Verify return code"
```

## Troubleshooting

### Common Issues

#### Issue 1: Backend Service Won't Start

**Symptoms:**
```
systemctl status nycu-backend
● nycu-backend.service - NYCU Course Platform Backend
   Loaded: loaded
   Active: failed
```

**Diagnosis:**
```bash
# Check detailed logs
sudo journalctl -u nycu-backend -n 100 --no-pager

# Check port availability
lsof -i :8000

# Test manually
cd /home/thc1006/dev/nycu_course_platform/backend
source venv/bin/activate
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

**Solutions:**
```bash
# Kill process using port 8000
kill $(lsof -t -i:8000)

# Check Python environment
source /home/thc1006/dev/nycu_course_platform/backend/venv/bin/activate
python --version
pip list

# Reinstall dependencies
pip install -r requirements.txt

# Check database access
ls -l /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db
sqlite3 nycu_course_platform.db "SELECT COUNT(*) FROM course;"

# Restart service
sudo systemctl restart nycu-backend
```

#### Issue 2: High Memory Usage

**Symptoms:**
```bash
free -h
#              total        used        free
# Mem:          8.0Gi       7.5Gi       500Mi
```

**Diagnosis:**
```bash
# Identify memory hogs
ps aux --sort=-%mem | head -10

# Check for memory leaks
watch -n 2 'ps aux | grep -E "(uvicorn|node)" | awk "{print \$2, \$4, \$11}"'

# View detailed memory usage
sudo pmap -x $(pgrep uvicorn)
```

**Solutions:**
```bash
# Restart services to clear memory
sudo systemctl restart nycu-backend nycu-frontend

# Adjust worker count if needed
# Edit /etc/systemd/system/nycu-backend.service
# Change --workers 4 to --workers 2

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Monitor after changes
watch -n 5 free -h
```

#### Issue 3: Slow API Response

**Symptoms:**
```bash
time curl http://localhost:8000/api/courses/?limit=50
# real    0m5.234s  (should be < 0m0.200s)
```

**Diagnosis:**
```bash
# Check database performance
sqlite3 nycu_course_platform.db "EXPLAIN QUERY PLAN SELECT * FROM course LIMIT 50;"

# Check indexes
sqlite3 nycu_course_platform.db ".schema course"

# Monitor backend load
htop -p $(pgrep -d',' uvicorn)

# Check Nginx logs for slow requests
sudo tail -f /var/log/nginx/access.log | grep -v "0.0[0-9][0-9]"
```

**Solutions:**
```bash
# Add missing indexes
sqlite3 nycu_course_platform.db << EOF
CREATE INDEX IF NOT EXISTS idx_course_acy ON course(acy);
CREATE INDEX IF NOT EXISTS idx_course_sem ON course(sem);
CREATE INDEX IF NOT EXISTS idx_course_dept ON course(dept);
CREATE INDEX IF NOT EXISTS idx_course_crs_no ON course(crs_no);
EOF

# Analyze database
sqlite3 nycu_course_platform.db "ANALYZE;"

# Restart backend with more workers
# Edit /etc/systemd/system/nycu-backend.service
# Change --workers 4 to --workers 8

# Restart services
sudo systemctl daemon-reload
sudo systemctl restart nycu-backend
```

#### Issue 4: SSL Certificate Not Renewing

**Symptoms:**
```bash
sudo certbot certificates
# Expiry Date: 2025-11-01 (EXPIRED!)
```

**Diagnosis:**
```bash
# Check certbot timer
systemctl status certbot.timer

# Test renewal
sudo certbot renew --dry-run

# Check logs
sudo journalctl -u certbot -n 50
```

**Solutions:**
```bash
# Force renewal
sudo certbot renew --force-renewal

# If that fails, obtain new certificate
sudo certbot --nginx -d nymu.com.tw -d www.nymu.com.tw

# Verify
echo | openssl s_client -connect nymu.com.tw:443 | grep "Verify return code"

# Restart Nginx
sudo systemctl reload nginx
```

#### Issue 5: Database Lock Error

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Diagnosis:**
```bash
# Check for locks
lsof | grep nycu_course_platform.db

# Check processes accessing database
fuser /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db
```

**Solutions:**
```bash
# Stop all services
sudo systemctl stop nycu-backend

# Clear any stuck processes
fuser -k /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Check database integrity
sqlite3 nycu_course_platform.db "PRAGMA integrity_check;"

# If database is locked, try waiting
# SQLite locks are usually temporary

# Restart service
sudo systemctl start nycu-backend
```

### Debugging Tools

#### Log Analysis

```bash
# Real-time log monitoring
sudo journalctl -u nycu-backend -f

# Filter by priority
sudo journalctl -u nycu-backend -p err -n 50

# Search for specific errors
sudo journalctl -u nycu-backend | grep -i "error\|exception\|failed"

# Export logs for analysis
sudo journalctl -u nycu-backend --since "2025-10-17 00:00:00" > backend-logs.txt

# Analyze error frequency
sudo journalctl -u nycu-backend -p err --since "1 day ago" | \
  grep -oP 'ERROR:.*' | sort | uniq -c | sort -rn
```

#### Network Debugging

```bash
# Check port listeners
sudo netstat -tlnp | grep -E '(3000|8000|80|443)'

# Monitor connections
sudo ss -s

# Check firewall
sudo ufw status verbose

# Test connectivity
curl -v http://localhost:8000/health
curl -v https://nymu.com.tw/health

# DNS check
nslookup nymu.com.tw
dig nymu.com.tw +short
```

#### Performance Profiling

```bash
# Backend profiling (add to code)
# pip install py-spy
sudo py-spy top --pid $(pgrep -f uvicorn)

# Record profile for 30 seconds
sudo py-spy record -o profile.svg --pid $(pgrep -f uvicorn) -- sleep 30

# Database query analysis
sqlite3 nycu_course_platform.db << EOF
.timer on
EXPLAIN QUERY PLAN SELECT * FROM course WHERE dept = 'CS';
SELECT * FROM course WHERE dept = 'CS' LIMIT 10;
EOF
```

## Performance Optimization

### Database Optimization

```bash
# Create comprehensive indexes
sqlite3 nycu_course_platform.db << EOF
-- Main indexes
CREATE INDEX IF NOT EXISTS idx_course_acy_sem ON course(acy, sem);
CREATE INDEX IF NOT EXISTS idx_course_dept ON course(dept);
CREATE INDEX IF NOT EXISTS idx_course_teacher ON course(teacher);
CREATE INDEX IF NOT EXISTS idx_course_crs_no ON course(crs_no);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_course_acy_sem_dept ON course(acy, sem, dept);

-- Analyze tables for query optimization
ANALYZE;
EOF

# Vacuum database to reclaim space and optimize
sqlite3 nycu_course_platform.db "VACUUM;"

# Enable WAL mode for better concurrency
sqlite3 nycu_course_platform.db "PRAGMA journal_mode=WAL;"

# Optimize cache size
sqlite3 nycu_course_platform.db "PRAGMA cache_size=-64000;"  # 64MB
```

### Backend Optimization

Edit `/etc/systemd/system/nycu-backend.service`:

```ini
[Service]
# Increase workers for better performance
ExecStart=/home/thc1006/dev/nycu_course_platform/backend/venv/bin/uvicorn \
    backend.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 8 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level warning \
    --access-log \
    --limit-concurrency 1000 \
    --backlog 2048

# Set resource limits
LimitNOFILE=65536
LimitNPROC=32768
```

### Nginx Optimization

Edit `/etc/nginx/nginx.conf`:

```nginx
user www-data;
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 10000;
    use epoll;
    multi_accept on;
}

http {
    # Connection keep-alive
    keepalive_timeout 65;
    keepalive_requests 1000;

    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 100M;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # Caching
    open_file_cache max=10000 inactive=30s;
    open_file_cache_valid 60s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # ... rest of configuration
}
```

### System-Level Optimization

```bash
# Increase file descriptors
sudo sysctl -w fs.file-max=2097152
sudo sysctl -w fs.nr_open=2097152

# TCP optimization
sudo sysctl -w net.core.somaxconn=65535
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0

# Make persistent
sudo tee -a /etc/sysctl.conf << EOF
fs.file-max = 2097152
fs.nr_open = 2097152
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_slow_start_after_idle = 0
EOF

sudo sysctl -p
```

## Log Management

### Log Rotation

Configure `/etc/logrotate.d/nycu-platform`:

```
/var/log/nycu-platform/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 thc1006 thc1006
    sharedscripts
    postrotate
        systemctl reload nycu-backend > /dev/null 2>&1 || true
        systemctl reload nycu-frontend > /dev/null 2>&1 || true
    endscript
}
```

### Log Analysis

```bash
# Error frequency analysis
grep -i error /var/log/nycu-platform/backend.log | \
  awk '{print $1, $2, $3}' | sort | uniq -c | sort -rn | head -20

# Find slow requests
awk '$NF > 1 {print $0}' /var/log/nginx/access.log | tail -50

# Count status codes
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Top requesting IPs
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
```

## Database Maintenance

### Regular Maintenance Tasks

```bash
# Weekly maintenance script
cat > /home/thc1006/scripts/db-maintenance.sh << 'EOF'
#!/bin/bash

DB_PATH="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"

echo "Starting database maintenance..."

# Integrity check
echo "Running integrity check..."
sqlite3 "$DB_PATH" "PRAGMA integrity_check;" | grep -v "^ok$" && \
    echo "⚠️  Database integrity issues found!" || \
    echo "✅ Database integrity OK"

# Analyze tables
echo "Analyzing tables..."
sqlite3 "$DB_PATH" "ANALYZE;"

# Vacuum database
echo "Vacuuming database..."
sqlite3 "$DB_PATH" "VACUUM;"

# Update statistics
echo "Updating statistics..."
sqlite3 "$DB_PATH" << SQL
SELECT
    'Total Courses: ' || COUNT(*) FROM course;
SELECT
    'Total Semesters: ' || COUNT(*) FROM semester;
SQL

# Check database size
echo "Database size: $(du -h "$DB_PATH" | cut -f1)"

echo "Database maintenance completed"
EOF

chmod +x /home/thc1006/scripts/db-maintenance.sh

# Schedule weekly maintenance
crontab -e
# Add: 0 3 * * 0 /home/thc1006/scripts/db-maintenance.sh
```

## Security Management

### Security Audit

```bash
# Check open ports
sudo netstat -tulpn | grep LISTEN

# Check firewall status
sudo ufw status verbose

# Check failed login attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# Check for suspicious processes
ps aux | grep -E "(nc|ncat|wget|curl)" | grep -v grep

# Check SSL configuration
sudo openssl s_client -connect nymu.com.tw:443 -showcerts

# Check file permissions
find /home/thc1006/dev/nycu_course_platform -type f -perm /go+w
```

### Security Hardening

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install security updates automatically
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Harden SSH
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Scaling Guidelines

### Vertical Scaling (Current Server)

```bash
# Current configuration supports:
# - 70,239 courses
# - Moderate concurrent users
# - 31 Nginx workers
# - 4 Uvicorn workers

# To handle more load:
# 1. Increase Uvicorn workers to 8-16
# 2. Add more RAM (16GB recommended for high traffic)
# 3. Use SSD for database (already in production)
```

### Horizontal Scaling (Multiple Servers)

```
Future architecture:
┌────────────────┐
│  Load Balancer │
└───────┬────────┘
        │
    ┌───┴──────────────┐
    │                  │
┌───▼───┐          ┌───▼───┐
│Server1│          │Server2│
│Backend│          │Backend│
└───┬───┘          └───┬───┘
    │                  │
    └──────┬───────────┘
           │
    ┌──────▼──────┐
    │  Database   │
    │  (PostgreSQL)│
    └─────────────┘
```

### Database Migration to PostgreSQL (Future)

```bash
# When scaling beyond SQLite:
# 1. Export SQLite data
# 2. Set up PostgreSQL cluster
# 3. Import data to PostgreSQL
# 4. Update backend configuration
# 5. Test thoroughly
# 6. Switch over

# Benefits:
# - Better concurrent access
# - Advanced features
# - Replication support
# - Better performance at scale
```

---

## Quick Reference

### Essential Commands

```bash
# Service Management
sudo systemctl status nginx nycu-backend nycu-frontend
sudo systemctl restart nycu-backend
sudo systemctl reload nginx

# Logs
sudo journalctl -u nycu-backend -f
tail -f /var/log/nginx/error.log

# Health Checks
curl http://localhost:8000/health
curl http://localhost:3000

# Database
sqlite3 nycu_course_platform.db "SELECT COUNT(*) FROM course;"

# Backups
/home/thc1006/scripts/full-backup.sh
/home/thc1006/scripts/backup-db-quick.sh

# Performance
htop
iotop
nethogs
```

### Emergency Contacts

```
System Administrator: [Your Contact]
Database Administrator: [Your Contact]
Network Administrator: [Your Contact]
Security Team: [Your Contact]
```

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
**Platform:** NYCU Course Platform
**Environment:** Production
