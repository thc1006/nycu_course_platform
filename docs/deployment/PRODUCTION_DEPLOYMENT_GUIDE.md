# NYCU Platform - Production Deployment Guide

**Platform:** NYCU Course Management System
**Domain:** `nymu.com.tw`
**Status:** ✅ Ready for Production Deployment
**Last Updated:** October 17, 2025

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Process](#deployment-process)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Verification & Testing](#verification--testing)
8. [Scaling & Performance](#scaling--performance)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

For experienced DevOps engineers, the deployment can be summarized as:

```bash
# 1. Clone and prepare
git clone <repo> /opt/nycu-platform
cd /opt/nycu-platform

# 2. Deploy all services
sudo bash deploy-production.sh

# 3. Setup SSL certificates
sudo bash deploy-ssl.sh

# 4. Configure monitoring
sudo bash setup-monitoring.sh

# 5. Verify deployment
sudo bash verify-deployment.sh
```

**Expected deployment time:** 10-15 minutes

---

## System Requirements

### Minimum Requirements (Proof of Concept)
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 20 GB
- **Bandwidth:** 1 Mbps

### Recommended Requirements (Production)
- **CPU:** 4+ cores (8 cores recommended for 1000+ concurrent users)
- **RAM:** 8+ GB (16 GB for high traffic)
- **Storage:** 50+ GB SSD (NVME preferred for better I/O)
- **Bandwidth:** 10+ Mbps
- **OS:** Ubuntu 20.04 LTS or later / Debian 11+

### Current Local Environment (Optimal)
```
✅ CPU:    32 cores (AMD EPYC 7R32)
✅ RAM:    15 GB (11 GB free)
✅ Disk:   50 GB (31 GB free)
✅ OS:     Linux (kernel 6.12.48)
```

### Recommended Resource Allocation
```
Backend (FastAPI + uvicorn):
  - CPU: 8 cores (25% of 32)
  - RAM: 2 GB (13% of 15 GB)
  - Workers: 4

Frontend (Next.js):
  - CPU: 4 cores (12% of 32)
  - RAM: 1.5 GB (10% of 15 GB)

Nginx (Reverse Proxy):
  - CPU: 2 cores (6% of 32)
  - RAM: 512 MB (3% of 15 GB)

System Reserve:
  - CPU: 18 cores (56% for spikes)
  - RAM: 3 GB (20% for OS & buffers)
```

---

## Pre-Deployment Checklist

### Infrastructure Preparation
- [ ] Server provisioned with Ubuntu 20.04 LTS or Debian 11+
- [ ] SSH access configured and keys set up
- [ ] Firewall configured to allow ports 80, 443, and SSH
- [ ] Domain `nymu.com.tw` registered and accessible
- [ ] Backup solution in place
- [ ] Monitoring solution selected (optional)

### Software Requirements
- [ ] Docker installed (version 20.10+)
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

- [ ] docker-compose installed (version 1.29+)
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

- [ ] Git installed
  ```bash
  sudo apt update && sudo apt install git
  ```

- [ ] Certbot installed (for SSL)
  ```bash
  sudo apt install certbot
  ```

### Directory Structure
```
/opt/nycu-platform/
├── backend/
│   ├── app/
│   ├── courses.db
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
├── nginx.conf
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── deploy-production.sh
├── deploy-ssl.sh
├── setup-monitoring.sh
├── verify-deployment.sh
└── .env
```

---

## Deployment Process

### Step 1: Environment Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Create deployment directory
sudo mkdir -p /opt/nycu-platform
cd /opt/nycu-platform

# Clone repository
sudo git clone <repository-url> .
cd /opt/nycu-platform

# Create .env file
sudo cp .env.example .env
sudo nano .env  # Edit configuration

# Set proper permissions
sudo chown -R $USER:$USER /opt/nycu-platform
chmod 750 deploy-*.sh setup-monitoring.sh verify-deployment.sh
```

### Step 2: Production Deployment

```bash
# Make script executable
chmod +x deploy-production.sh

# Run deployment
sudo bash deploy-production.sh

# Expected output:
# ✅ Docker images built
# ✅ Services started
# ✅ Backend healthy (HTTP 200)
# ✅ Frontend healthy (HTTP 200)
# ✅ Nginx configured
```

**What the script does:**
- Clones/updates repository
- Backs up existing data
- Builds Docker images
- Starts all containers
- Verifies service health
- Creates systemd service file
- Configures log rotation

### Step 3: SSL/TLS Setup

```bash
# Run SSL setup
sudo bash deploy-ssl.sh

# When prompted:
# 1. Select staging (test) or production
# 2. Enter email for certificate notifications
# 3. Confirm domain names (nymu.com.tw www.nymu.com.tw)

# Expected output:
# ✅ Certificate obtained
# ✅ Auto-renewal configured
# ✅ Nginx reloaded with SSL
```

**Configuration Details:**
- Uses Let's Encrypt for free SSL certificates
- Automatic renewal via systemd timer
- HSTS, Security headers configured
- HTTP → HTTPS redirection enabled

### Step 4: Monitoring Setup

```bash
# Configure monitoring and logging
sudo bash setup-monitoring.sh

# Expected output:
# ✅ Log directories created
# ✅ Performance monitoring enabled
# ✅ Health checks configured
# ✅ Log rotation set up
# ✅ Cron jobs installed
```

**Configured monitoring:**
- Performance metrics (CPU, memory, disk) - every 5 minutes
- API health checks - every 10 minutes
- Daily log aggregation and summary
- Alert system for threshold violations

### Step 5: Verification

```bash
# Run comprehensive verification
sudo bash verify-deployment.sh

# Should see:
# ✅ Docker daemon running
# ✅ All containers running
# ✅ Backend health check passed
# ✅ Frontend is serving content
# ✅ Nginx configuration valid
# ✅ Database accessible
# ✅ SSL certificates valid
```

---

## SSL/TLS Configuration

### Automated Setup (Recommended)

```bash
sudo bash deploy-ssl.sh
```

### Manual Setup

```bash
# Stop services temporarily
docker-compose down

# Request certificate
certbot certonly --standalone \
  -d nymu.com.tw \
  -d www.nymu.com.tw \
  --email admin@nymu.com.tw \
  --agree-tos \
  --no-eff-email

# Start services
docker-compose up -d nginx
```

### Certificate Management

```bash
# Check certificate status
certbot certificates

# Manually renew
certbot renew --force-renewal

# Test renewal (dry-run)
certbot renew --dry-run

# View certificate details
openssl x509 -in /etc/letsencrypt/live/nymu.com.tw/fullchain.pem -text -noout

# Check expiration date
openssl x509 -in /etc/letsencrypt/live/nymu.com.tw/fullchain.pem -noout -dates
```

### HTTPS Security Configuration

```nginx
# Configured in nginx.conf

# SSL Protocols
ssl_protocols TLSv1.2 TLSv1.3;

# Strong Ciphers
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

# Session Settings
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;

# Security Headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
```

---

## Monitoring & Logging

### Log Locations

```
/var/log/nycu-platform/
├── backend/          # Backend application logs
├── frontend/         # Frontend server logs
├── nginx/            # Nginx reverse proxy logs
├── system/           # System events
├── performance/      # Performance metrics
└── api/              # API health checks
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f nycu-backend
docker logs -f nycu-frontend
docker logs -f nycu-nginx

# System logs
tail -f /var/log/nycu-platform/system/system.log
tail -f /var/log/nycu-platform/performance/metrics.log

# API logs
tail -f /var/log/nycu-platform/api/health.log
```

### Monitoring Commands

```bash
# Health check (manual)
/usr/local/bin/nycu-health-check.sh

# Performance metrics
tail -f /var/log/nycu-platform/performance/metrics.log

# Container status
docker stats
docker ps

# System metrics
uptime
free -h
df -h
```

### Cron Jobs (Automatic)

```bash
# View installed cron jobs
crontab -l

# Expected jobs:
# */5 * * * * /opt/nycu-platform/monitoring/monitor-performance.sh
# */10 * * * * /opt/nycu-platform/monitoring/monitor-api.sh
# 0 0 * * * /opt/nycu-platform/monitoring/aggregate-logs.sh
# 0 3 * * * certbot renew --quiet --post-hook 'docker-compose up -d nginx'
```

---

## Verification & Testing

### Post-Deployment Verification

```bash
# Run verification script
sudo bash verify-deployment.sh

# Manual verification

# 1. Check container status
docker-compose ps

# 2. Test backend API
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl "http://localhost:8000/api/v1/courses?limit=1"

# 3. Test frontend
curl http://localhost:3000

# 4. Test through Nginx
curl http://localhost/health
curl https://localhost/health -k

# 5. Test domain (after DNS update)
curl https://nymu.com.tw/health
curl https://nymu.com.tw/api/docs

# 6. Check database
sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;"

# 7. Verify SSL certificate
openssl s_client -connect nymu.com.tw:443 -showcerts
```

### Performance Testing

```bash
# Test API response time
time curl "http://localhost:8000/api/v1/courses?limit=10"

# Load test (using Apache Bench)
sudo apt install apache2-utils
ab -n 1000 -c 100 http://localhost:8000/health

# Monitor during load test
watch -n 1 'docker stats --no-stream'
```

### Smoke Tests

```bash
# Quick functionality tests
echo "Testing Backend..."
curl -f http://localhost:8000/health || echo "Backend FAILED"

echo "Testing Frontend..."
curl -f http://localhost:3000 || echo "Frontend FAILED"

echo "Testing Nginx..."
curl -f http://localhost/health || echo "Nginx FAILED"

echo "Testing Database..."
sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;" || echo "Database FAILED"
```

---

## Scaling & Performance

### Performance Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| API Response Time (p95) | <100ms | >200ms | >500ms |
| Frontend Load Time | <3s | >5s | >10s |
| CPU Usage | <50% | >70% | >85% |
| Memory Usage | <60% | >75% | >90% |
| Disk Usage | <70% | >80% | >90% |
| Error Rate | <0.1% | >0.5% | >1% |

### Vertical Scaling (More Resources)

```bash
# Increase Docker limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '16'      # Increase from 8
          memory: 4G      # Increase from 2G

# Rebuild and restart
docker-compose up -d --force-recreate
```

### Horizontal Scaling (Multiple Instances)

For scaling beyond single-server capacity:

```bash
# Phase 2 Scaling Strategy
1. Add load balancer (HAProxy/AWS ELB)
2. Separate backend servers
3. Shared database (PostgreSQL)
4. Redis cache layer
5. CDN for static assets
6. Database replication
```

### Optimization Tips

```bash
# 1. Enable Gzip compression (nginx.conf)
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript;

# 2. Cache static assets
expires 30d;
add_header Cache-Control "public, max-age=2592000";

# 3. Connection pooling
keepalive 32;
keepalive_timeout 65;

# 4. Database indexing
CREATE INDEX idx_courses_semester ON courses(semester);
CREATE INDEX idx_courses_department ON courses(department);

# 5. Database optimization
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
```

---

## Maintenance

### Daily Tasks

```bash
# Health check
/usr/local/bin/nycu-health-check.sh

# Check logs for errors
grep ERROR /var/log/nycu-platform/*/*.log || echo "No errors"

# Verify services running
docker-compose ps

# Monitor key metrics
docker stats --no-stream
```

### Weekly Tasks

```bash
# Database backup
cp /opt/nycu-platform/backend/courses.db /backup/courses.db.$(date +%Y%m%d)

# Review performance metrics
tail -50 /var/log/nycu-platform/performance/metrics.log

# Check disk space
df -h /

# Review error logs
grep -i error /var/log/nycu-platform/*/*.log | tail -20
```

### Monthly Tasks

```bash
# Full system backup
rsync -av /opt/nycu-platform/ /backup/nycu-platform-$(date +%Y%m%d)/

# SSL certificate check
certbot certificates

# Analyze API performance
sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;"

# Update security policies
# Review firewall rules
# Plan capacity upgrades
```

### Quarterly Tasks

```bash
# Full disaster recovery test
# Restore from backup to test system

# Security audit
# Penetration testing
# Access review

# Performance optimization review
# Database statistics refresh
# Index analysis

# Capacity planning
# Growth analysis
# Infrastructure updates
```

---

## Troubleshooting

### Services Not Starting

```bash
# Check Docker daemon
sudo systemctl status docker
sudo systemctl restart docker

# View service logs
docker-compose logs

# Check for port conflicts
sudo lsof -i :80 -i :443 -i :8000 -i :3000

# Rebuild and start
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### High CPU/Memory Usage

```bash
# Identify resource hogs
docker stats

# Check running processes
top
htop

# Reduce workload or scale up
docker-compose restart
# Increase resource limits if needed
```

### Disk Space Issues

```bash
# Check disk usage
df -h
du -sh /opt/nycu-platform/

# Clean old logs
find /var/log/nycu-platform -name "*.log" -mtime +30 -delete

# Clean Docker artifacts
docker system prune -a --volumes

# Backup and remove large files
tar -czf /backup/old-logs.tar.gz /var/log/nycu-platform/
rm -rf /var/log/nycu-platform/*/*.log.*
```

### Certificate Issues

```bash
# Check certificate status
certbot certificates

# Check certificate in nginx
openssl x509 -in /etc/letsencrypt/live/nymu.com.tw/fullchain.pem -text -noout

# Force renewal
certbot renew --force-renewal

# Check renewal logs
tail -f /var/log/letsencrypt/letsencrypt.log
```

### Database Corruption

```bash
# Check database integrity
sqlite3 /opt/nycu-platform/backend/courses.db "PRAGMA integrity_check;"

# Restore from backup
cp /backup/courses.db.backup /opt/nycu-platform/backend/courses.db

# Rebuild index
sqlite3 /opt/nycu-platform/backend/courses.db "REINDEX;"
```

### Network Connectivity

```bash
# Test backend connectivity
curl http://localhost:8000/health

# Test frontend connectivity
curl http://localhost:3000

# Check container networking
docker network inspect nycu-network

# Test external connectivity
curl https://www.google.com

# Check DNS resolution
nslookup nymu.com.tw
```

---

## Rollback Procedure

If deployment fails or critical issues occur:

```bash
# 1. Stop all services
docker-compose down

# 2. Restore database from backup
cp /backup/courses.db.TIMESTAMP /opt/nycu-platform/backend/courses.db

# 3. Restart services
docker-compose up -d

# 4. Verify health
bash verify-deployment.sh

# If still issues, restore entire system
rsync -av /backup/nycu-platform-TIMESTAMP/ /opt/nycu-platform/
docker-compose restart
```

---

## Emergency Procedures

### Service Down

```bash
# Immediate restart
docker-compose restart

# If persists, check logs
docker-compose logs | tail -100

# Restart docker daemon
sudo systemctl restart docker
docker-compose up -d
```

### Data Loss

```bash
# Restore from backup
cp /backup/courses.db.RECENT /opt/nycu-platform/backend/courses.db

# Verify restore
sqlite3 /opt/nycu-platform/backend/courses.db "SELECT COUNT(*) FROM courses;"

# Restart services
docker-compose restart backend
```

### Security Breach

```bash
# Immediately isolate
docker-compose down

# Review logs
sudo journalctl -xe

# Check for unauthorized access
grep "FAILED\|error" /var/log/auth.log | tail -50

# Change credentials
# Update firewall rules
# Patch vulnerabilities
```

---

## Support & Documentation

| Topic | Location |
|-------|----------|
| API Documentation | `/backend/README.md` |
| Frontend Setup | `/frontend/README.md` |
| Deployment Scripts | `/deploy-*.sh` |
| Monitoring Setup | `/setup-monitoring.sh` |
| Nginx Configuration | `/nginx.conf` |
| Docker Compose | `/docker-compose.yml` |
| Deployment Checklist | `/DEPLOYMENT_CHECKLIST.md` |

---

## Success Criteria

✅ **Deployment is successful when:**

- [ ] All containers running and healthy
- [ ] Frontend accessible at https://nymu.com.tw
- [ ] Backend API accessible at https://nymu.com.tw/api
- [ ] API documentation available at https://nymu.com.tw/api/docs
- [ ] SSL certificate valid and auto-renewal configured
- [ ] Monitoring and logging operational
- [ ] Database accessible with data
- [ ] Backup strategy in place
- [ ] Performance within targets
- [ ] No critical security warnings

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-17 | Initial production deployment guide |

---

**Last Updated:** October 17, 2025
**Maintained By:** DevOps Team
**Status:** ✅ Production Ready

---

**For additional support, contact:** devops@nymu.com.tw
