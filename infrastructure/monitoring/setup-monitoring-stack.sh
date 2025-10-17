#!/bin/bash

##############################################################################
# NYCU Course Platform - Production Monitoring Setup
# This script sets up comprehensive monitoring, logging, and alerting
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="31.41.34.19"
DOMAIN="nymu.com.tw"
PROJECT_DIR="/home/thc1006/dev/nycu_course_platform"
MONITORING_DIR="$PROJECT_DIR/infrastructure/monitoring"
LOGS_DIR="/var/log/nycu-platform"
BACKUP_DIR="/var/backups/nycu-platform"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}NYCU Platform - Monitoring Infrastructure${NC}"
echo -e "${BLUE}==========================================${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating monitoring directories...${NC}"
sudo mkdir -p $MONITORING_DIR/{configs,scripts,dashboards,alerts}
sudo mkdir -p $LOGS_DIR/{app,nginx,system}
sudo mkdir -p $BACKUP_DIR/{daily,weekly,monthly}
sudo mkdir -p /etc/prometheus
sudo mkdir -p /etc/grafana
sudo mkdir -p /etc/loki

##############################################################################
# 1. INSTALL MONITORING TOOLS
##############################################################################

echo -e "${GREEN}Installing monitoring dependencies...${NC}"

# Update system
sudo apt-get update -q

# Install essential monitoring tools
sudo apt-get install -y \
    prometheus \
    prometheus-node-exporter \
    prometheus-alertmanager \
    grafana \
    rsyslog \
    logrotate \
    htop \
    iotop \
    netdata \
    monit \
    fail2ban \
    ufw \
    redis-tools \
    postgresql-client \
    sqlite3 \
    jq \
    curl \
    wget \
    gnupg \
    software-properties-common

# Install Grafana Loki for log aggregation
echo -e "${YELLOW}Installing Grafana Loki...${NC}"
cd /tmp
wget https://github.com/grafana/loki/releases/download/v2.9.0/loki-linux-amd64.zip
unzip -o loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/local/bin/loki
sudo chmod +x /usr/local/bin/loki

wget https://github.com/grafana/loki/releases/download/v2.9.0/promtail-linux-amd64.zip
unzip -o promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail
sudo chmod +x /usr/local/bin/promtail

# Install PM2 for process management
echo -e "${YELLOW}Installing PM2...${NC}"
sudo npm install -g pm2
sudo pm2 startup systemd -u $USER --hp /home/$USER

##############################################################################
# 2. PROMETHEUS CONFIGURATION
##############################################################################

echo -e "${GREEN}Configuring Prometheus...${NC}"

cat << 'EOF' | sudo tee /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'nycu-platform'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  # Node Exporter - System Metrics
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          instance: 'nycu-server'

  # FastAPI Backend
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          service: 'backend'
    metrics_path: '/metrics'

  # Next.js Frontend
  - job_name: 'nextjs'
    static_configs:
      - targets: ['localhost:3000']
        labels:
          service: 'frontend'
    metrics_path: '/api/metrics'

  # Nginx
  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
        labels:
          service: 'nginx'

  # SQLite Database Exporter
  - job_name: 'sqlite'
    static_configs:
      - targets: ['localhost:9187']
        labels:
          service: 'database'
EOF

##############################################################################
# 3. ALERT RULES
##############################################################################

echo -e "${GREEN}Setting up alert rules...${NC}"

sudo mkdir -p /etc/prometheus/rules

cat << 'EOF' | sudo tee /etc/prometheus/rules/alerts.yml
groups:
  - name: system_alerts
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% (current value: {{ $value }}%)"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% (current value: {{ $value }}%)"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20
        for: 5m
        labels:
          severity: critical
          service: system
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 20% (current value: {{ $value }}%)"

      - alert: DatabaseSizeLarge
        expr: file_size_bytes{file="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"} > 50000000000
        for: 5m
        labels:
          severity: warning
          service: database
        annotations:
          summary: "Database size exceeding threshold"
          description: "SQLite database is larger than 50GB (current: {{ $value | humanize }})"

  - name: application_alerts
    interval: 30s
    rules:
      - alert: BackendDown
        expr: up{job="fastapi"} == 0
        for: 1m
        labels:
          severity: critical
          service: backend
        annotations:
          summary: "FastAPI backend is down"
          description: "Backend service at port 8000 is not responding"

      - alert: FrontendDown
        expr: up{job="nextjs"} == 0
        for: 1m
        labels:
          severity: critical
          service: frontend
        annotations:
          summary: "Next.js frontend is down"
          description: "Frontend service at port 3000 is not responding"

      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 2
        for: 5m
        labels:
          severity: warning
          service: api
        annotations:
          summary: "High API response time"
          description: "95th percentile response time is above 2 seconds"

      - alert: TooManyDatabaseConnections
        expr: sqlite_connections > 50
        for: 5m
        labels:
          severity: warning
          service: database
        annotations:
          summary: "High number of SQLite connections"
          description: "More than 50 concurrent connections to SQLite"

  - name: security_alerts
    interval: 30s
    rules:
      - alert: SSLCertificateExpiringSoon
        expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 7
        for: 1h
        labels:
          severity: warning
          service: ssl
        annotations:
          summary: "SSL certificate expiring soon"
          description: "SSL certificate will expire in less than 7 days"

      - alert: TooManyFailedLogins
        expr: rate(auth_failed_attempts[5m]) > 10
        for: 5m
        labels:
          severity: critical
          service: security
        annotations:
          summary: "Possible brute force attack"
          description: "More than 10 failed login attempts per minute"

      - alert: DDoSAttack
        expr: rate(nginx_requests_total[1m]) > 10000
        for: 2m
        labels:
          severity: critical
          service: security
        annotations:
          summary: "Possible DDoS attack"
          description: "Request rate exceeds 10000 requests per minute"
EOF

##############################################################################
# 4. LOKI CONFIGURATION FOR LOG AGGREGATION
##############################################################################

echo -e "${GREEN}Configuring Loki for log aggregation...${NC}"

cat << 'EOF' | sudo tee /etc/loki/loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

analytics:
  reporting_enabled: false

limits_config:
  retention_period: 720h
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  max_entries_limit_per_query: 100000
EOF

##############################################################################
# 5. PROMTAIL CONFIGURATION FOR LOG COLLECTION
##############################################################################

echo -e "${GREEN}Configuring Promtail for log collection...${NC}"

cat << 'EOF' | sudo tee /etc/promtail/promtail-config.yml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: fastapi
          app: backend
          env: production
          __path__: /tmp/backend.log
    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            module: module
      - timestamp:
          source: timestamp
          format: RFC3339
      - labels:
          level:
          module:

  - job_name: frontend
    static_configs:
      - targets:
          - localhost
        labels:
          job: nextjs
          app: frontend
          env: production
          __path__: /tmp/frontend.log
    pipeline_stages:
      - regex:
          expression: '^(?P<timestamp>[\d\-T:\.]+Z?\s+)?(?P<level>\w+)?\s+(?P<message>.*)$'
      - labels:
          level:

  - job_name: nginx
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          app: proxy
          env: production
          __path__: /var/log/nginx/*.log
    pipeline_stages:
      - regex:
          expression: '^(?P<remote_addr>[\d\.]+) - (?P<remote_user>[^ ]+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<path>[^ ]+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<bytes_sent>\d+)'
      - timestamp:
          source: timestamp
          format: '02/Jan/2006:15:04:05 -0700'
      - labels:
          method:
          status:

  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          env: production
          __path__: /var/log/syslog
EOF

##############################################################################
# 6. GRAFANA CONFIGURATION
##############################################################################

echo -e "${GREEN}Configuring Grafana...${NC}"

# Add Prometheus data source
cat << 'EOF' | sudo tee /etc/grafana/provisioning/datasources/prometheus.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    orgId: 1
    url: http://localhost:9090
    basicAuth: false
    isDefault: true
    jsonData:
      timeInterval: "15s"
    editable: true

  - name: Loki
    type: loki
    access: proxy
    orgId: 1
    url: http://localhost:3100
    basicAuth: false
    jsonData:
      maxLines: 1000
    editable: true
EOF

##############################################################################
# 7. SYSTEMD SERVICES
##############################################################################

echo -e "${GREEN}Creating systemd services...${NC}"

# Loki service
cat << 'EOF' | sudo tee /etc/systemd/system/loki.service
[Unit]
Description=Loki
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/loki -config.file=/etc/loki/loki-config.yml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Promtail service
cat << 'EOF' | sudo tee /etc/systemd/system/promtail.service
[Unit]
Description=Promtail
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/promtail -config.file=/etc/promtail/promtail-config.yml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

##############################################################################
# 8. PM2 PROCESS MANAGEMENT
##############################################################################

echo -e "${GREEN}Setting up PM2 process management...${NC}"

cat << EOF > $MONITORING_DIR/ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'nycu-frontend',
      cwd: '$PROJECT_DIR/frontend',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'https://nymu.com.tw/api'
      },
      instances: 2,
      exec_mode: 'cluster',
      max_memory_restart: '1G',
      error_file: '$LOGS_DIR/app/frontend-error.log',
      out_file: '$LOGS_DIR/app/frontend-out.log',
      log_file: '$LOGS_DIR/app/frontend-combined.log',
      time: true,
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      listen_timeout: 10000,
      kill_timeout: 5000,
    },
    {
      name: 'nycu-backend',
      cwd: '$PROJECT_DIR/backend',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info --access-log',
      interpreter: 'python3',
      env: {
        PYTHONPATH: '$PROJECT_DIR/backend',
        DATABASE_URL: 'sqlite:///$PROJECT_DIR/nycu_course_platform.db',
        ENVIRONMENT: 'production'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      error_file: '$LOGS_DIR/app/backend-error.log',
      out_file: '$LOGS_DIR/app/backend-out.log',
      log_file: '$LOGS_DIR/app/backend-combined.log',
      time: true,
      merge_logs: true,
      max_restarts: 10,
      min_uptime: '10s',
    }
  ]
};
EOF

##############################################################################
# 9. LOG ROTATION
##############################################################################

echo -e "${GREEN}Configuring log rotation...${NC}"

cat << 'EOF' | sudo tee /etc/logrotate.d/nycu-platform
/var/log/nycu-platform/app/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}

/var/log/nycu-platform/nginx/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}

/tmp/backend.log /tmp/frontend.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    copytruncate
}
EOF

##############################################################################
# 10. DATABASE BACKUP SCRIPT
##############################################################################

echo -e "${GREEN}Creating database backup script...${NC}"

cat << 'EOF' > $MONITORING_DIR/scripts/backup-database.sh
#!/bin/bash

# Configuration
DB_PATH="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"
BACKUP_DIR="/var/backups/nycu-platform"
S3_BUCKET="nycu-platform-backups"  # Configure if using S3
DATE=$(date +%Y%m%d_%H%M%S)

# Function to create backup
create_backup() {
    local type=$1
    local retention=$2
    local backup_path="$BACKUP_DIR/$type/nycu_course_platform_${DATE}.db"

    echo "[$(date)] Starting $type backup..."

    # Create SQLite backup
    sqlite3 $DB_PATH ".backup '$backup_path'"

    if [ $? -eq 0 ]; then
        # Compress backup
        gzip -9 "$backup_path"
        echo "[$(date)] $type backup completed: ${backup_path}.gz"

        # Calculate checksum
        sha256sum "${backup_path}.gz" > "${backup_path}.gz.sha256"

        # Upload to cloud storage (optional)
        # aws s3 cp "${backup_path}.gz" "s3://$S3_BUCKET/$type/" --storage-class GLACIER

        # Clean old backups
        find "$BACKUP_DIR/$type" -name "*.db.gz" -mtime +$retention -delete
    else
        echo "[$(date)] ERROR: $type backup failed!"
        exit 1
    fi
}

# Determine backup type based on day
DAY_OF_WEEK=$(date +%u)
DAY_OF_MONTH=$(date +%d)

if [ "$DAY_OF_MONTH" -eq 1 ]; then
    create_backup "monthly" 365
elif [ "$DAY_OF_WEEK" -eq 7 ]; then
    create_backup "weekly" 30
else
    create_backup "daily" 7
fi

# Verify database integrity
echo "[$(date)] Verifying database integrity..."
sqlite3 $DB_PATH "PRAGMA integrity_check;" > /tmp/db_integrity.log

if grep -q "ok" /tmp/db_integrity.log; then
    echo "[$(date)] Database integrity check passed"
else
    echo "[$(date)] WARNING: Database integrity check failed!"
    # Send alert
fi

# Log backup statistics
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
DB_SIZE=$(du -sh "$DB_PATH" | cut -f1)
RECORD_COUNT=$(sqlite3 $DB_PATH "SELECT COUNT(*) FROM courses;" 2>/dev/null || echo "N/A")

echo "[$(date)] Backup Statistics:"
echo "  - Database Size: $DB_SIZE"
echo "  - Total Backups Size: $BACKUP_SIZE"
echo "  - Course Records: $RECORD_COUNT"
EOF

chmod +x $MONITORING_DIR/scripts/backup-database.sh

##############################################################################
# 11. HEALTH CHECK ENDPOINTS
##############################################################################

echo -e "${GREEN}Creating health check endpoints...${NC}"

# Backend health check
cat << 'EOF' > $PROJECT_DIR/backend/app/monitoring.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import os
from typing import Dict, Any
from app.database import get_db
from app.models import Course

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "backend"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with system metrics"""

    # Check database connection
    try:
        course_count = db.query(Course).count()
        db_status = "healthy"
        db_error = None
    except Exception as e:
        course_count = 0
        db_status = "unhealthy"
        db_error = str(e)

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Process metrics
    process = psutil.Process(os.getpid())

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "backend",
        "database": {
            "status": db_status,
            "course_count": course_count,
            "error": db_error
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3)
        },
        "process": {
            "pid": process.pid,
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / (1024**2),
            "num_threads": process.num_threads(),
            "uptime_seconds": (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds()
        }
    }

@router.get("/metrics")
async def prometheus_metrics(db: Session = Depends(get_db)) -> str:
    """Prometheus-compatible metrics endpoint"""

    try:
        course_count = db.query(Course).count()
    except:
        course_count = 0

    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    metrics = []
    metrics.append(f'# HELP nycu_courses_total Total number of courses')
    metrics.append(f'# TYPE nycu_courses_total gauge')
    metrics.append(f'nycu_courses_total {course_count}')

    metrics.append(f'# HELP nycu_backend_cpu_usage CPU usage percentage')
    metrics.append(f'# TYPE nycu_backend_cpu_usage gauge')
    metrics.append(f'nycu_backend_cpu_usage {cpu_percent}')

    metrics.append(f'# HELP nycu_backend_memory_usage Memory usage percentage')
    metrics.append(f'# TYPE nycu_backend_memory_usage gauge')
    metrics.append(f'nycu_backend_memory_usage {memory.percent}')

    return "\n".join(metrics)
EOF

# Frontend health check API route
cat << 'EOF' > $PROJECT_DIR/frontend/pages/api/health.js
import os from 'os';

export default function handler(req, res) {
  const uptime = process.uptime();
  const memoryUsage = process.memoryUsage();

  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'frontend',
    uptime: uptime,
    memory: {
      rss_mb: memoryUsage.rss / 1024 / 1024,
      heap_used_mb: memoryUsage.heapUsed / 1024 / 1024,
      heap_total_mb: memoryUsage.heapTotal / 1024 / 1024,
    },
    system: {
      platform: os.platform(),
      nodejs_version: process.version,
      loadavg: os.loadavg(),
    }
  });
}
EOF

# Frontend Prometheus metrics
cat << 'EOF' > $PROJECT_DIR/frontend/pages/api/metrics.js
import os from 'os';

export default function handler(req, res) {
  const memoryUsage = process.memoryUsage();
  const uptime = process.uptime();

  const metrics = [
    '# HELP nycu_frontend_uptime Frontend uptime in seconds',
    '# TYPE nycu_frontend_uptime gauge',
    `nycu_frontend_uptime ${uptime}`,
    '',
    '# HELP nycu_frontend_memory_rss Frontend RSS memory in bytes',
    '# TYPE nycu_frontend_memory_rss gauge',
    `nycu_frontend_memory_rss ${memoryUsage.rss}`,
    '',
    '# HELP nycu_frontend_memory_heap_used Frontend heap used in bytes',
    '# TYPE nycu_frontend_memory_heap_used gauge',
    `nycu_frontend_memory_heap_used ${memoryUsage.heapUsed}`,
  ];

  res.setHeader('Content-Type', 'text/plain');
  res.status(200).send(metrics.join('\n'));
}
EOF

##############################################################################
# 12. SECURITY HARDENING
##############################################################################

echo -e "${GREEN}Applying security hardening...${NC}"

# Configure fail2ban for DDoS protection
cat << 'EOF' | sudo tee /etc/fail2ban/jail.d/nycu-platform.conf
[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https"]
logpath = /var/log/nginx/error.log
findtime = 60
maxretry = 10
bantime = 3600

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400

[nginx-rate-limit]
enabled = true
filter = nginx-rate-limit
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 60
bantime = 3600
EOF

# Configure UFW firewall
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # Frontend (internal only)
sudo ufw allow 8000/tcp  # Backend (internal only)
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 3100/tcp  # Grafana
sudo ufw limit ssh/tcp   # Rate limit SSH

##############################################################################
# 13. SSL CERTIFICATE MONITORING
##############################################################################

echo -e "${GREEN}Setting up SSL certificate monitoring...${NC}"

cat << 'EOF' > $MONITORING_DIR/scripts/check-ssl-cert.sh
#!/bin/bash

DOMAIN="nymu.com.tw"
ALERT_DAYS=14
EMAIL="admin@nymu.com.tw"

# Check certificate expiration
EXPIRY_DATE=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))

echo "[$(date)] SSL Certificate Status for $DOMAIN:"
echo "  Expires: $EXPIRY_DATE"
echo "  Days remaining: $DAYS_LEFT"

if [ $DAYS_LEFT -lt $ALERT_DAYS ]; then
    echo "WARNING: SSL certificate expires in $DAYS_LEFT days!"
    # Send alert email
    # echo "SSL certificate for $DOMAIN expires in $DAYS_LEFT days" | mail -s "SSL Certificate Expiration Warning" $EMAIL

    # Try to auto-renew with Let's Encrypt
    if [ $DAYS_LEFT -lt 7 ]; then
        echo "Attempting automatic renewal..."
        sudo certbot renew --nginx
    fi
fi

# Log to Prometheus
cat << METRICS > /var/lib/prometheus/node-exporter/ssl_cert_expiry.prom
# HELP ssl_cert_expiry_days Days until SSL certificate expires
# TYPE ssl_cert_expiry_days gauge
ssl_cert_expiry_days{domain="$DOMAIN"} $DAYS_LEFT
METRICS
EOF

chmod +x $MONITORING_DIR/scripts/check-ssl-cert.sh

##############################################################################
# 14. CRON JOBS
##############################################################################

echo -e "${GREEN}Setting up cron jobs...${NC}"

cat << 'EOF' | sudo tee /etc/cron.d/nycu-platform
# NYCU Platform Monitoring Cron Jobs
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Database backups
0 2 * * * root /home/thc1006/dev/nycu_course_platform/infrastructure/monitoring/scripts/backup-database.sh >> /var/log/nycu-platform/backup.log 2>&1

# SSL certificate check (daily at 3 AM)
0 3 * * * root /home/thc1006/dev/nycu_course_platform/infrastructure/monitoring/scripts/check-ssl-cert.sh >> /var/log/nycu-platform/ssl-check.log 2>&1

# Database optimization (weekly)
0 4 * * 0 root sqlite3 /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db "VACUUM; ANALYZE;" >> /var/log/nycu-platform/db-maintenance.log 2>&1

# Log cleanup (daily)
0 5 * * * root find /var/log/nycu-platform -name "*.log" -mtime +30 -delete

# System health report (every 6 hours)
0 */6 * * * root /home/thc1006/dev/nycu_course_platform/infrastructure/monitoring/scripts/health-report.sh
EOF

##############################################################################
# 15. START SERVICES
##############################################################################

echo -e "${GREEN}Starting monitoring services...${NC}"

# Reload systemd
sudo systemctl daemon-reload

# Start and enable services
sudo systemctl enable --now prometheus
sudo systemctl enable --now prometheus-node-exporter
sudo systemctl enable --now grafana-server
sudo systemctl enable --now loki
sudo systemctl enable --now promtail
sudo systemctl enable --now fail2ban
sudo systemctl enable --now monit

# Start PM2 apps
cd $PROJECT_DIR
pm2 start $MONITORING_DIR/ecosystem.config.js
pm2 save

##############################################################################
# 16. NGINX MONITORING MODULE
##############################################################################

echo -e "${GREEN}Adding Nginx monitoring...${NC}"

cat << 'EOF' | sudo tee -a /etc/nginx/sites-available/nycu-platform
    # Monitoring endpoints
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    # DDoS protection headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
EOF

sudo nginx -s reload

##############################################################################
# FINAL SUMMARY
##############################################################################

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Monitoring Stack Setup Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${YELLOW}Access Points:${NC}"
echo "  - Prometheus: http://$SERVER_IP:9090"
echo "  - Grafana: http://$SERVER_IP:3000 (admin/admin)"
echo "  - Health Check (Backend): https://$DOMAIN/api/health"
echo "  - Health Check (Frontend): https://$DOMAIN/api/health"
echo "  - Metrics: http://$SERVER_IP:9090/targets"
echo ""
echo -e "${YELLOW}Logs Location:${NC}"
echo "  - Application: $LOGS_DIR/app/"
echo "  - Nginx: $LOGS_DIR/nginx/"
echo "  - System: $LOGS_DIR/system/"
echo ""
echo -e "${YELLOW}Backup Location:${NC}"
echo "  - Database: $BACKUP_DIR/"
echo ""
echo -e "${YELLOW}PM2 Commands:${NC}"
echo "  - pm2 status"
echo "  - pm2 logs"
echo "  - pm2 monit"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "1. Configure Grafana dashboards"
echo "2. Set up alert notifications (email/Slack)"
echo "3. Test backup restoration procedure"
echo "4. Review security settings"
echo "5. Configure off-site backup storage"