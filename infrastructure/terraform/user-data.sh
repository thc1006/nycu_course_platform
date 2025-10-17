#!/bin/bash

##############################################################################
# Cloud-Init User Data Script for NYCU Platform
# This script runs on first boot to configure the server
##############################################################################

set -e

# Variables passed from Terraform
PROJECT_NAME="${project_name}"
DOMAIN="${domain}"
ENVIRONMENT="${environment}"

# System update
apt-get update -y
apt-get upgrade -y

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    htop \
    vim \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    sqlite3 \
    redis-server \
    supervisor \
    prometheus \
    grafana \
    rsyslog \
    logrotate

# Configure firewall
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Create application user
useradd -m -s /bin/bash nycu-app || true
usermod -aG sudo nycu-app

# Create directory structure
mkdir -p /opt/$PROJECT_NAME/{frontend,backend,logs,backups}
mkdir -p /var/log/$PROJECT_NAME
mkdir -p /var/backups/$PROJECT_NAME

# Clone application (if using git)
# git clone https://github.com/nycu/course-platform.git /opt/$PROJECT_NAME/app

# Set up Python virtual environment
python3 -m venv /opt/$PROJECT_NAME/backend/venv
source /opt/$PROJECT_NAME/backend/venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy prometheus-client

# Set up Node.js application
cd /opt/$PROJECT_NAME/frontend
npm install --production

# Configure Nginx
cat > /etc/nginx/sites-available/$PROJECT_NAME << 'EOF'
upstream backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

upstream frontend {
    server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req zone=general burst=20 nodelay;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for large course queries
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health checks
    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }

    # Monitoring endpoints
    location /metrics {
        allow 127.0.0.1;
        deny all;
        proxy_pass http://backend/metrics;
    }

    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/

# Configure Supervisor for process management
cat > /etc/supervisor/conf.d/$PROJECT_NAME.conf << 'EOF'
[program:backend]
command=/opt/${PROJECT_NAME}/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/opt/${PROJECT_NAME}/backend
user=nycu-app
autostart=true
autorestart=true
stopwaitsecs=10
stdout_logfile=/var/log/${PROJECT_NAME}/backend.log
stderr_logfile=/var/log/${PROJECT_NAME}/backend-error.log
environment=PATH="/opt/${PROJECT_NAME}/backend/venv/bin",DATABASE_URL="sqlite:////opt/${PROJECT_NAME}/nycu_course_platform.db"

[program:frontend]
command=npm start
directory=/opt/${PROJECT_NAME}/frontend
user=nycu-app
autostart=true
autorestart=true
stopwaitsecs=10
stdout_logfile=/var/log/${PROJECT_NAME}/frontend.log
stderr_logfile=/var/log/${PROJECT_NAME}/frontend-error.log
environment=NODE_ENV="production",PORT="3000",NEXT_PUBLIC_API_URL="https://${DOMAIN}/api"
EOF

# Set up automated backups
cat > /etc/cron.d/$PROJECT_NAME-backup << 'EOF'
0 2 * * * root sqlite3 /opt/${PROJECT_NAME}/nycu_course_platform.db ".backup '/var/backups/${PROJECT_NAME}/db-$(date +\%Y\%m\%d).sqlite'" 2>&1 | logger -t backup
0 3 * * * root find /var/backups/${PROJECT_NAME} -name "*.sqlite" -mtime +30 -delete 2>&1 | logger -t backup
EOF

# Configure log rotation
cat > /etc/logrotate.d/$PROJECT_NAME << 'EOF'
/var/log/${PROJECT_NAME}/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 nycu-app nycu-app
    sharedscripts
    postrotate
        supervisorctl restart all
    endscript
}
EOF

# Set permissions
chown -R nycu-app:nycu-app /opt/$PROJECT_NAME
chown -R nycu-app:nycu-app /var/log/$PROJECT_NAME
chmod -R 755 /opt/$PROJECT_NAME

# Enable and start services
systemctl enable nginx
systemctl enable supervisor
systemctl enable prometheus
systemctl enable grafana-server

systemctl restart nginx
systemctl restart supervisor
systemctl restart prometheus
systemctl restart grafana-server

# Request SSL certificate
certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN}

# Final system optimization
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sysctl -w net.ipv4.ip_local_port_range="1024 65535"
echo "net.core.somaxconn=65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog=8192" >> /etc/sysctl.conf
echo "net.ipv4.ip_local_port_range=1024 65535" >> /etc/sysctl.conf

# Setup complete
echo "NYCU Platform setup complete for $ENVIRONMENT environment" | logger -t cloud-init