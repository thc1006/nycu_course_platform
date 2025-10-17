#!/bin/bash

##############################################################################
# NYCU Platform - Complete Deployment & Monitoring Setup
# This script deploys the platform and sets up all monitoring
##############################################################################

set -e

# Configuration
SERVER_IP="31.41.34.19"
DOMAIN="nymu.com.tw"
PROJECT_DIR="/home/thc1006/dev/nycu_course_platform"
ENVIRONMENT="production"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}NYCU Platform - Full Stack Deployment${NC}"
echo -e "${BLUE}============================================${NC}"

##############################################################################
# PHASE 1: PRE-DEPLOYMENT CHECKS
##############################################################################

echo -e "${YELLOW}Phase 1: Pre-deployment checks...${NC}"

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run with sudo${NC}"
    exit 1
fi

# Check database exists
if [ ! -f "$PROJECT_DIR/nycu_course_platform.db" ]; then
    echo -e "${RED}Database not found! Please import courses first.${NC}"
    exit 1
fi

# Check course count
COURSE_COUNT=$(sqlite3 "$PROJECT_DIR/nycu_course_platform.db" "SELECT COUNT(*) FROM courses;" 2>/dev/null || echo "0")
echo -e "${GREEN}✓ Database contains $COURSE_COUNT courses${NC}"

if [ "$COURSE_COUNT" -lt 70000 ]; then
    echo -e "${YELLOW}Warning: Expected 70,000+ courses, found $COURSE_COUNT${NC}"
fi

##############################################################################
# PHASE 2: INSTALL DEPENDENCIES
##############################################################################

echo -e "${YELLOW}Phase 2: Installing dependencies...${NC}"

# Update system
apt-get update -q
apt-get upgrade -y -q

# Install monitoring tools
apt-get install -y -q \
    nginx \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    sqlite3 \
    redis-server \
    prometheus \
    grafana \
    fail2ban \
    ufw \
    certbot \
    python3-certbot-nginx \
    htop \
    iotop \
    nethogs \
    vnstat \
    monit

# Install PM2 globally
npm install -g pm2

echo -e "${GREEN}✓ Dependencies installed${NC}"

##############################################################################
# PHASE 3: SETUP BACKEND
##############################################################################

echo -e "${YELLOW}Phase 3: Setting up backend...${NC}"

cd $PROJECT_DIR/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy prometheus-client psutil python-multipart

# Add monitoring endpoints to main.py if not exists
if ! grep -q "/health" main.py; then
    cat >> main.py << 'EOF'

# Health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/metrics")
async def metrics():
    # Basic Prometheus metrics
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")
EOF
fi

deactivate
echo -e "${GREEN}✓ Backend configured${NC}"

##############################################################################
# PHASE 4: SETUP FRONTEND
##############################################################################

echo -e "${YELLOW}Phase 4: Setting up frontend...${NC}"

cd $PROJECT_DIR/frontend

# Install dependencies and build
npm install --production
npm run build

echo -e "${GREEN}✓ Frontend built${NC}"

##############################################################################
# PHASE 5: CONFIGURE PM2
##############################################################################

echo -e "${YELLOW}Phase 5: Configuring PM2 process manager...${NC}"

cat > $PROJECT_DIR/ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'nycu-backend',
      cwd: '$PROJECT_DIR/backend',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000 --workers 4',
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '2G',
      env: {
        DATABASE_URL: 'sqlite:///$PROJECT_DIR/nycu_course_platform.db'
      },
      error_file: '/var/log/nycu-platform/backend-error.log',
      out_file: '/var/log/nycu-platform/backend-out.log',
      log_file: '/var/log/nycu-platform/backend-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'nycu-frontend',
      cwd: '$PROJECT_DIR/frontend',
      script: 'npm',
      args: 'start',
      instances: 2,
      exec_mode: 'cluster',
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'https://$DOMAIN/api'
      },
      error_file: '/var/log/nycu-platform/frontend-error.log',
      out_file: '/var/log/nycu-platform/frontend-out.log',
      log_file: '/var/log/nycu-platform/frontend-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
EOF

# Create log directory
mkdir -p /var/log/nycu-platform

# Start applications with PM2
cd $PROJECT_DIR
pm2 delete all 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u $USER --hp /home/$USER

echo -e "${GREEN}✓ PM2 configured and applications started${NC}"

##############################################################################
# PHASE 6: CONFIGURE NGINX
##############################################################################

echo -e "${YELLOW}Phase 6: Configuring Nginx...${NC}"

cat > /etc/nginx/sites-available/nycu-platform << EOF
# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=general:10m rate=30r/s;

upstream backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream frontend {
    least_conn;
    server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Client body size for file uploads
    client_max_body_size 10M;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    send_timeout 60s;

    # Frontend
    location / {
        limit_req zone=general burst=50 nodelay;

        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";

        # Don't cache API responses
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Health check endpoints
    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }

    location /api/health {
        access_log off;
        proxy_pass http://frontend/api/health;
    }

    # Monitoring endpoints (restrict access)
    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }

    location /metrics {
        proxy_pass http://backend/metrics;
        allow 127.0.0.1;
        deny all;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/nycu-platform /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl restart nginx

echo -e "${GREEN}✓ Nginx configured${NC}"

##############################################################################
# PHASE 7: CONFIGURE FIREWALL
##############################################################################

echo -e "${YELLOW}Phase 7: Configuring firewall...${NC}"

ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 9090/tcp  # Prometheus
ufw allow 3100/tcp  # Grafana
ufw limit 22/tcp     # Rate limit SSH

echo -e "${GREEN}✓ Firewall configured${NC}"

##############################################################################
# PHASE 8: SETUP SSL CERTIFICATE
##############################################################################

echo -e "${YELLOW}Phase 8: Setting up SSL certificate...${NC}"

# Check if certificate already exists
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
else
    echo -e "${GREEN}✓ SSL certificate already exists${NC}"
fi

# Setup auto-renewal
cat > /etc/cron.d/certbot-renewal << EOF
0 2 * * * root certbot renew --quiet --nginx --post-hook "systemctl reload nginx"
EOF

echo -e "${GREEN}✓ SSL configured${NC}"

##############################################################################
# PHASE 9: SETUP MONITORING
##############################################################################

echo -e "${YELLOW}Phase 9: Setting up monitoring...${NC}"

# Configure Prometheus
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

  - job_name: 'backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'frontend'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/api/metrics'
EOF

systemctl restart prometheus

# Configure Grafana
systemctl enable grafana-server
systemctl start grafana-server

echo -e "${GREEN}✓ Monitoring configured${NC}"

##############################################################################
# PHASE 10: SETUP BACKUPS
##############################################################################

echo -e "${YELLOW}Phase 10: Setting up automated backups...${NC}"

# Create backup directory
mkdir -p /var/backups/nycu-platform/{daily,weekly,monthly}

# Create backup script
cat > /usr/local/bin/nycu-backup.sh << 'EOF'
#!/bin/bash
DB_PATH="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"
BACKUP_DIR="/var/backups/nycu-platform"
DATE=$(date +%Y%m%d_%H%M%S)

# Determine backup type
DAY_OF_WEEK=$(date +%u)
DAY_OF_MONTH=$(date +%d)

if [ "$DAY_OF_MONTH" -eq 1 ]; then
    TYPE="monthly"
    RETENTION=365
elif [ "$DAY_OF_WEEK" -eq 7 ]; then
    TYPE="weekly"
    RETENTION=30
else
    TYPE="daily"
    RETENTION=7
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/$TYPE/nycu_db_${DATE}.sqlite"
sqlite3 $DB_PATH ".backup '$BACKUP_FILE'"
gzip -9 "$BACKUP_FILE"

# Clean old backups
find "$BACKUP_DIR/$TYPE" -name "*.sqlite.gz" -mtime +$RETENTION -delete

echo "[$(date)] Backup completed: ${BACKUP_FILE}.gz"
EOF

chmod +x /usr/local/bin/nycu-backup.sh

# Setup cron job
cat > /etc/cron.d/nycu-backup << EOF
0 2 * * * root /usr/local/bin/nycu-backup.sh >> /var/log/nycu-platform/backup.log 2>&1
EOF

echo -e "${GREEN}✓ Backups configured${NC}"

##############################################################################
# PHASE 11: SETUP LOG ROTATION
##############################################################################

echo -e "${YELLOW}Phase 11: Setting up log rotation...${NC}"

cat > /etc/logrotate.d/nycu-platform << EOF
/var/log/nycu-platform/*.log {
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
EOF

echo -e "${GREEN}✓ Log rotation configured${NC}"

##############################################################################
# PHASE 12: PERFORMANCE TUNING
##############################################################################

echo -e "${YELLOW}Phase 12: Applying performance tuning...${NC}"

# System optimizations
cat >> /etc/sysctl.conf << EOF

# NYCU Platform Optimizations
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=8192
net.ipv4.ip_local_port_range=1024 65535
net.core.netdev_max_backlog=5000
net.ipv4.tcp_fin_timeout=30
net.ipv4.tcp_keepalive_time=300
net.ipv4.tcp_keepalive_probes=5
net.ipv4.tcp_keepalive_intvl=15
fs.file-max=2097152
EOF

sysctl -p

echo -e "${GREEN}✓ Performance tuning applied${NC}"

##############################################################################
# PHASE 13: FINAL VERIFICATION
##############################################################################

echo -e "${YELLOW}Phase 13: Running final verification...${NC}"

# Check all services
SERVICES=("nginx" "prometheus" "grafana-server")
for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
    fi
done

# Check PM2 processes
pm2 list

# Check endpoints
echo -e "${YELLOW}Checking endpoints...${NC}"

# Backend health
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Frontend health
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health | grep -q "200"; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
fi

# Database check
COURSE_COUNT=$(sqlite3 "$PROJECT_DIR/nycu_course_platform.db" "SELECT COUNT(*) FROM courses;" 2>/dev/null || echo "0")
echo -e "${GREEN}✓ Database contains $COURSE_COUNT courses${NC}"

##############################################################################
# COMPLETION
##############################################################################

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}Access Points:${NC}"
echo "  Website: https://$DOMAIN"
echo "  API: https://$DOMAIN/api"
echo "  Health Check: https://$DOMAIN/health"
echo "  Prometheus: http://$SERVER_IP:9090"
echo "  Grafana: http://$SERVER_IP:3000 (admin/admin)"
echo ""
echo -e "${YELLOW}Monitoring:${NC}"
echo "  PM2 Status: pm2 status"
echo "  PM2 Logs: pm2 logs"
echo "  PM2 Monitor: pm2 monit"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  Application: /var/log/nycu-platform/"
echo "  Nginx: /var/log/nginx/"
echo ""
echo -e "${YELLOW}Backups:${NC}"
echo "  Location: /var/backups/nycu-platform/"
echo "  Schedule: Daily 2 AM"
echo ""
echo -e "${GREEN}Platform is ready for production use!${NC}"