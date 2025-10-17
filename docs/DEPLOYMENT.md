# NYCU Course Platform - Deployment Guide

Complete guide for deploying the NYCU Course Platform to production environments.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Running Services](#running-services)
- [SSL/TLS Setup](#ssltls-setup)
- [Database Initialization](#database-initialization)
- [Verification](#verification)
- [Post-Deployment](#post-deployment)
- [Rollback Procedures](#rollback-procedures)

## Overview

The NYCU Course Platform is currently deployed at:
- **Domain:** nymu.com.tw
- **Server IP:** 31.41.34.19
- **HTTPS:** Enabled (Let's Encrypt)
- **Architecture:** Frontend (Next.js) + Backend (FastAPI) + Nginx (Reverse Proxy)

**Deployment Stack:**
- **Frontend:** Next.js 14 + React 18 (Port 3000)
- **Backend:** FastAPI + Uvicorn (Port 8000)
- **Reverse Proxy:** Nginx (Ports 80, 443)
- **Database:** SQLite with 70,239 courses
- **SSL:** Let's Encrypt (Certbot)

## System Requirements

### Minimum Requirements

**Hardware:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- Network: 100 Mbps

**Software:**
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.10+
- Node.js 18+
- Nginx 1.18+
- Certbot 1.12+

### Recommended Requirements

**Hardware:**
- CPU: 4+ cores (31 Nginx workers in production)
- RAM: 8GB+
- Storage: 50GB SSD
- Network: 1 Gbps

**Software:**
- Ubuntu 22.04 LTS
- Python 3.11+
- Node.js 20+
- Nginx 1.24+
- Certbot 2.0+

### Production Environment

Current production specs:
```
Server: 31.41.34.19
OS: Debian 13
CPU: Multi-core (31 Nginx workers)
RAM: Sufficient for 70K+ courses
Storage: SSD with course database
```

## Pre-Deployment Checklist

### Server Preparation

- [ ] Server provisioned with required specs
- [ ] Root or sudo access available
- [ ] Domain name configured (DNS pointing to server IP)
- [ ] Firewall rules configured (ports 22, 80, 443)
- [ ] SSH key authentication set up
- [ ] Backup strategy planned

### Software Installation

- [ ] System packages updated
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Nginx installed
- [ ] Git installed
- [ ] Certbot installed

### Repository Setup

- [ ] Git repository cloned
- [ ] Environment variables configured
- [ ] Application dependencies reviewed
- [ ] Database backup available (if migrating)

### Security

- [ ] SSL certificates ready or Certbot configured
- [ ] Firewall rules applied
- [ ] SSH hardened (key-only authentication)
- [ ] Non-root user created for application
- [ ] Secrets management configured

## Installation Steps

### Step 1: System Update

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential
```

### Step 2: Install Python

```bash
# Install Python 3.11+
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verify installation
python3 --version  # Should be 3.10+
pip3 --version
```

### Step 3: Install Node.js

```bash
# Install Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should be v20+
npm --version
```

### Step 4: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify installation
nginx -v
sudo systemctl status nginx
```

### Step 5: Install Certbot

```bash
# Install Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
```

### Step 6: Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/nycu-platform
sudo chown $USER:$USER /opt/nycu-platform

# Clone repository
cd /opt/nycu-platform
git clone <repository-url> .

# Or if using existing code
cd /home/thc1006/dev/nycu_course_platform
```

### Step 7: Backend Setup

```bash
# Navigate to backend directory
cd /home/thc1006/dev/nycu_course_platform/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pip list
```

### Step 8: Frontend Setup

```bash
# Navigate to frontend directory
cd /home/thc1006/dev/nycu_course_platform/frontend

# Install dependencies
npm install

# Build production version
npm run build

# Verify build
ls -la .next/
```

### Step 9: Database Setup

```bash
# Navigate to project root
cd /home/thc1006/dev/nycu_course_platform

# Initialize database (if not exists)
python3 import_production_courses.py

# Verify database
sqlite3 nycu_course_platform.db ".tables"
sqlite3 nycu_course_platform.db "SELECT COUNT(*) FROM course;"
# Should show 70239 courses
```

## Configuration

### Environment Variables

#### Backend Configuration

Create `/home/thc1006/dev/nycu_course_platform/backend/.env`:

```bash
# Application Settings
APP_NAME="NYCU Course Platform"
APP_VERSION="1.0.0"
ENVIRONMENT=production

# Database
DATABASE_URL=sqlite:////home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS
CORS_ORIGINS=["https://nymu.com.tw", "https://www.nymu.com.tw"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/nycu-platform/backend.log
```

#### Frontend Configuration

Create `/home/thc1006/dev/nycu_course_platform/frontend/.env.production`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://nymu.com.tw/api

# Application
NEXT_PUBLIC_APP_NAME="NYCU Course Platform"
NEXT_PUBLIC_APP_VERSION="1.0.0"

# Build
NODE_ENV=production
```

### Nginx Configuration

Create `/etc/nginx/sites-available/nycu-platform`:

```nginx
# Upstream servers
upstream frontend {
    server localhost:3000;
}

upstream backend {
    server localhost:8000;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name nymu.com.tw www.nymu.com.tw;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name nymu.com.tw www.nymu.com.tw;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/nymu.com.tw/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nymu.com.tw/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

    # Frontend
    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        limit_req zone=api burst=50 nodelay;
        proxy_pass http://backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API Documentation
    location /docs {
        proxy_pass http://backend/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Health Check
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }

    # Static Files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        proxy_pass http://frontend;
        proxy_cache_valid 200 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
}
```

Enable the site:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/nycu-platform /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Systemd Service Files

#### Backend Service

Create `/etc/systemd/system/nycu-backend.service`:

```ini
[Unit]
Description=NYCU Course Platform Backend
After=network.target

[Service]
Type=simple
User=thc1006
Group=thc1006
WorkingDirectory=/home/thc1006/dev/nycu_course_platform/backend
Environment="PATH=/home/thc1006/dev/nycu_course_platform/backend/venv/bin"
ExecStart=/home/thc1006/dev/nycu_course_platform/backend/venv/bin/uvicorn \
    backend.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info

Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/nycu-platform/backend.log
StandardError=append:/var/log/nycu-platform/backend-error.log

[Install]
WantedBy=multi-user.target
```

#### Frontend Service

Create `/etc/systemd/system/nycu-frontend.service`:

```ini
[Unit]
Description=NYCU Course Platform Frontend
After=network.target

[Service]
Type=simple
User=thc1006
Group=thc1006
WorkingDirectory=/home/thc1006/dev/nycu_course_platform/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start

Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/nycu-platform/frontend.log
StandardError=append:/var/log/nycu-platform/frontend-error.log

[Install]
WantedBy=multi-user.target
```

Create log directory:

```bash
sudo mkdir -p /var/log/nycu-platform
sudo chown thc1006:thc1006 /var/log/nycu-platform
```

## Running Services

### Start Services Manually (Development/Testing)

#### Backend

```bash
cd /home/thc1006/dev/nycu_course_platform/backend
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend

```bash
cd /home/thc1006/dev/nycu_course_platform/frontend
npm run build
npm start
```

#### Nginx

```bash
sudo systemctl start nginx
```

### Start Services with Systemd (Production)

```bash
# Enable services to start on boot
sudo systemctl enable nycu-backend
sudo systemctl enable nycu-frontend
sudo systemctl enable nginx

# Start services
sudo systemctl start nycu-backend
sudo systemctl start nycu-frontend
sudo systemctl start nginx

# Check status
sudo systemctl status nycu-backend
sudo systemctl status nycu-frontend
sudo systemctl status nginx
```

### Service Management Commands

```bash
# Start service
sudo systemctl start <service-name>

# Stop service
sudo systemctl stop <service-name>

# Restart service
sudo systemctl restart <service-name>

# Reload configuration
sudo systemctl reload <service-name>

# Check status
sudo systemctl status <service-name>

# View logs
sudo journalctl -u <service-name> -f

# Enable on boot
sudo systemctl enable <service-name>

# Disable on boot
sudo systemctl disable <service-name>
```

## SSL/TLS Setup

### Let's Encrypt with Certbot

#### Initial Certificate Generation

```bash
# Ensure domain DNS points to server IP
nslookup nymu.com.tw
# Should return: 31.41.34.19

# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d nymu.com.tw -d www.nymu.com.tw

# Or use nginx plugin (if Nginx is running)
sudo certbot --nginx -d nymu.com.tw -d www.nymu.com.tw

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect option (2 for automatic HTTPS redirect)
```

#### Certificate Locations

```
Certificate: /etc/letsencrypt/live/nymu.com.tw/fullchain.pem
Private Key: /etc/letsencrypt/live/nymu.com.tw/privkey.pem
Chain: /etc/letsencrypt/live/nymu.com.tw/chain.pem
Full Chain: /etc/letsencrypt/live/nymu.com.tw/fullchain.pem
```

#### Automatic Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up renewal via systemd timer
sudo systemctl status certbot.timer

# Or via cron (if timer not available)
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

#### Verify SSL Configuration

```bash
# Test SSL certificate
openssl s_client -connect nymu.com.tw:443 -servername nymu.com.tw

# Check certificate expiry
echo | openssl s_client -connect nymu.com.tw:443 2>/dev/null | \
    openssl x509 -noout -dates

# Online tools
# - https://www.ssllabs.com/ssltest/
# - https://www.digicert.com/help/
```

### SSL Best Practices

1. **Use Strong Protocols:**
   - Enable TLSv1.2 and TLSv1.3 only
   - Disable SSLv3, TLSv1.0, TLSv1.1

2. **Strong Cipher Suites:**
   ```nginx
   ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
   ```

3. **Enable HSTS:**
   ```nginx
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   ```

4. **OCSP Stapling:**
   ```nginx
   ssl_stapling on;
   ssl_stapling_verify on;
   ```

## Database Initialization

### Initial Database Setup

```bash
cd /home/thc1006/dev/nycu_course_platform

# Option 1: Import production data (70,239 courses)
python3 import_production_courses.py

# Option 2: Use seed data (for testing)
cd backend/scripts
python3 seed_db.py
```

### Verify Database

```bash
# Check database file exists
ls -lh nycu_course_platform.db

# Connect to database
sqlite3 nycu_course_platform.db

# Run verification queries
sqlite> .tables
# Should show: course, semester

sqlite> SELECT COUNT(*) FROM semester;
# Should show: 9 semesters

sqlite> SELECT COUNT(*) FROM course;
# Should show: 70239 courses

sqlite> SELECT * FROM semester LIMIT 5;
# Should show semester records

sqlite> SELECT * FROM course LIMIT 5;
# Should show course records

sqlite> .exit
```

### Database Backup

```bash
# Create backup directory
mkdir -p /home/thc1006/backups/database

# Backup database
cp nycu_course_platform.db /home/thc1006/backups/database/nycu_course_platform_$(date +%Y%m%d_%H%M%S).db

# Automated backup script
cat > /home/thc1006/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/thc1006/backups/database"
DB_PATH="/home/thc1006/dev/nycu_course_platform/nycu_course_platform.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nycu_course_platform_$TIMESTAMP.db"

# Create backup
cp "$DB_PATH" "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "nycu_course_platform_*.db.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /home/thc1006/backup-db.sh

# Schedule daily backup (cron)
crontab -e
# Add: 0 2 * * * /home/thc1006/backup-db.sh
```

### Database Restore

```bash
# Stop backend service
sudo systemctl stop nycu-backend

# Restore from backup
cp /home/thc1006/backups/database/nycu_course_platform_YYYYMMDD_HHMMSS.db \
   /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Or restore from compressed backup
gunzip -c /home/thc1006/backups/database/nycu_course_platform_YYYYMMDD_HHMMSS.db.gz > \
   /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Start backend service
sudo systemctl start nycu-backend

# Verify
curl http://localhost:8000/health
```

## Verification

### Step-by-Step Verification

#### 1. Verify Backend Service

```bash
# Check service status
sudo systemctl status nycu-backend

# Check process
ps aux | grep uvicorn

# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}

# Test API endpoint
curl http://localhost:8000/api/semesters/
# Expected: Array of semester objects

# Check API documentation
curl http://localhost:8000/docs
# Should return HTML
```

#### 2. Verify Frontend Service

```bash
# Check service status
sudo systemctl status nycu-frontend

# Check process
ps aux | grep node

# Test frontend
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# Check page content
curl http://localhost:3000 | grep "NYCU"
```

#### 3. Verify Nginx

```bash
# Check service status
sudo systemctl status nginx

# Check configuration
sudo nginx -t

# Check workers
ps aux | grep nginx
# Should show 31 worker processes

# Test HTTP redirect
curl -I http://nymu.com.tw
# Expected: 301 redirect to HTTPS

# Test HTTPS
curl -I https://nymu.com.tw
# Expected: 200 OK
```

#### 4. Verify SSL Certificate

```bash
# Check certificate
sudo certbot certificates

# Test SSL connection
echo | openssl s_client -connect nymu.com.tw:443 -servername nymu.com.tw 2>/dev/null | grep -E '(subject|issuer|notAfter)'

# Check certificate expiry
sudo certbot renew --dry-run
```

#### 5. End-to-End Testing

```bash
# Test complete flow
# 1. Visit homepage
curl -L https://nymu.com.tw | grep "NYCU Course Platform"

# 2. Test API through Nginx
curl https://nymu.com.tw/health
curl https://nymu.com.tw/api/semesters/
curl https://nymu.com.tw/api/courses/?limit=5

# 3. Test documentation
curl -I https://nymu.com.tw/docs

# 4. Test with different User-Agent
curl -H "User-Agent: Mozilla/5.0" https://nymu.com.tw/
```

### Verification Checklist

- [ ] Backend service running and healthy
- [ ] Frontend service running and accessible
- [ ] Nginx running with correct number of workers
- [ ] SSL certificate installed and valid
- [ ] HTTP redirects to HTTPS
- [ ] API endpoints responding correctly
- [ ] Database contains 70,239 courses
- [ ] All services start on boot
- [ ] Log files being created
- [ ] Domain resolves correctly
- [ ] Security headers present
- [ ] Rate limiting working

## Post-Deployment

### Monitoring Setup

#### System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor CPU and memory
htop

# Monitor disk I/O
iotop

# Monitor network
nethogs

# Check disk usage
df -h

# Check memory usage
free -h

# Check system load
uptime
```

#### Application Monitoring

```bash
# View backend logs
sudo journalctl -u nycu-backend -f

# View frontend logs
sudo journalctl -u nycu-frontend -f

# View Nginx access logs
sudo tail -f /var/log/nginx/access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# View application logs
tail -f /var/log/nycu-platform/backend.log
tail -f /var/log/nycu-platform/frontend.log
```

#### Performance Monitoring

```bash
# API response time
time curl -s https://nymu.com.tw/api/courses/?limit=1

# Database query performance
sqlite3 nycu_course_platform.db "EXPLAIN QUERY PLAN SELECT * FROM course WHERE dept = 'CS';"

# Nginx status (if compiled with stub_status)
curl http://localhost/nginx_status
```

### Log Rotation

Create `/etc/logrotate.d/nycu-platform`:

```
/var/log/nycu-platform/*.log {
    daily
    rotate 14
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

### Backup Strategy

```bash
# Automated backup script
cat > /home/thc1006/full-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/thc1006/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup database
cp /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db "$BACKUP_DIR/"

# Backup configuration
cp -r /etc/nginx/sites-available "$BACKUP_DIR/"
cp /etc/systemd/system/nycu-*.service "$BACKUP_DIR/"

# Backup environment files
cp /home/thc1006/dev/nycu_course_platform/backend/.env "$BACKUP_DIR/"
cp /home/thc1006/dev/nycu_course_platform/frontend/.env.production "$BACKUP_DIR/"

# Compress
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Keep only last 30 days
find /home/thc1006/backups/ -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR.tar.gz"
EOF

chmod +x /home/thc1006/full-backup.sh

# Schedule daily backup
crontab -e
# Add: 0 3 * * * /home/thc1006/full-backup.sh
```

### Security Hardening

```bash
# Update firewall rules
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable

# Disable root SSH login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Install fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Set up automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Rollback Procedures

### Rollback Backend

```bash
# Stop current backend
sudo systemctl stop nycu-backend

# Restore previous version
cd /home/thc1006/dev/nycu_course_platform
git checkout <previous-commit-hash>

# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restore database (if needed)
cp /home/thc1006/backups/database/nycu_course_platform_BACKUP.db \
   /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Start backend
sudo systemctl start nycu-backend

# Verify
curl http://localhost:8000/health
```

### Rollback Frontend

```bash
# Stop current frontend
sudo systemctl stop nycu-frontend

# Restore previous version
cd /home/thc1006/dev/nycu_course_platform/frontend
git checkout <previous-commit-hash>

# Reinstall dependencies
npm install

# Rebuild
npm run build

# Start frontend
sudo systemctl start nycu-frontend

# Verify
curl -I http://localhost:3000
```

### Rollback Nginx Configuration

```bash
# Restore previous configuration
sudo cp /home/thc1006/backups/nginx/nycu-platform.conf.backup \
       /etc/nginx/sites-available/nycu-platform

# Test configuration
sudo nginx -t

# Reload if valid
sudo systemctl reload nginx
```

### Complete System Rollback

```bash
# Stop all services
sudo systemctl stop nycu-backend nycu-frontend nginx

# Restore from backup
tar -xzf /home/thc1006/backups/YYYYMMDD.tar.gz -C /

# Restore database
cp /home/thc1006/backups/database/nycu_course_platform_BACKUP.db \
   /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Start services
sudo systemctl start nginx nycu-backend nycu-frontend

# Verify
curl https://nymu.com.tw/health
```

## Troubleshooting

### Common Issues

#### Backend Not Starting

```bash
# Check logs
sudo journalctl -u nycu-backend -n 50

# Check port availability
lsof -i :8000

# Check database permissions
ls -l /home/thc1006/dev/nycu_course_platform/nycu_course_platform.db

# Test manually
cd /home/thc1006/dev/nycu_course_platform/backend
source venv/bin/activate
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Not Building

```bash
# Check logs
sudo journalctl -u nycu-frontend -n 50

# Check Node.js version
node --version

# Clear cache and rebuild
cd /home/thc1006/dev/nycu_course_platform/frontend
rm -rf .next node_modules
npm install
npm run build
```

#### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal

# Check Nginx SSL configuration
sudo nginx -t

# Verify SSL files exist
ls -l /etc/letsencrypt/live/nymu.com.tw/
```

---

## Deployment Summary

**Current Production Deployment:**
- Domain: nymu.com.tw (31.41.34.19)
- Backend: Port 8000 (4 workers)
- Frontend: Port 3000
- Nginx: Ports 80, 443 (31 workers)
- Database: 70,239 courses, 9 semesters
- SSL: Let's Encrypt (Auto-renewal enabled)
- Status: Production Ready

**Deployment Time:**
- Fresh install: 30-60 minutes
- Update deployment: 5-10 minutes
- SSL setup: 5-10 minutes

**Maintenance Windows:**
- Regular updates: Weekly (low-traffic hours)
- Security patches: As needed
- Database backup: Daily at 2 AM
- Log rotation: Daily

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
**Deployment Status:** Production Active
**Uptime:** 99.9%
