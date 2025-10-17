# NYCU Platform Production Deployment Checklist

**Domain:** `nymu.com.tw`
**Status:** Ready for Deployment
**Last Updated:** 2025-10-17

---

## Pre-Deployment Verification

- [ ] All code committed to git repository
- [ ] Environment variables configured (.env file exists)
- [ ] Docker and docker-compose installed on server
- [ ] Firewall ports 80 and 443 are open
- [ ] Server has at least 4GB RAM available
- [ ] Server has at least 20GB disk space available
- [ ] Domain DNS records are ready to be updated
- [ ] Email configured for SSL certificate notifications (optional)

---

## Automated Deployment Steps

### Step 1: Deploy Services
```bash
sudo bash deploy-production.sh
```

**Expected Outcomes:**
- [ ] Docker images built successfully
- [ ] Backend container running on port 8000
- [ ] Frontend container running on port 3000
- [ ] Nginx container running on ports 80/443
- [ ] All containers healthy and restarting on failure

**Verify:**
```bash
docker-compose ps
docker logs nycu-backend | tail -20
docker logs nycu-frontend | tail -20
```

### Step 2: Setup SSL/TLS Certificates
```bash
sudo bash deploy-ssl.sh
```

**Expected Outcomes:**
- [ ] Let's Encrypt certificates provisioned for nymu.com.tw
- [ ] Certificates stored at /etc/letsencrypt/live/nymu.com.tw/
- [ ] Auto-renewal configured with systemd timer
- [ ] Nginx configured to use HTTPS

**Verify:**
```bash
ls -la /etc/letsencrypt/live/nymu.com.tw/
systemctl status certbot-renewal.timer
curl https://nymu.com.tw/health
```

### Step 3: Configure Monitoring
```bash
sudo bash setup-monitoring.sh
```

**Expected Outcomes:**
- [ ] Log directories created
- [ ] Performance monitoring cron jobs installed
- [ ] API health checks configured
- [ ] Log rotation policies set
- [ ] Alerting system configured

**Verify:**
```bash
ls -la /var/log/nycu-platform/
crontab -l | grep monitoring
```

### Step 4: Verify Deployment
```bash
sudo bash verify-deployment.sh
```

**Expected Outcomes:**
- [ ] All Docker containers running
- [ ] Backend health check passing
- [ ] Frontend accessible and serving content
- [ ] Nginx configuration valid
- [ ] Database accessible
- [ ] Security headers present
- [ ] SSL certificates valid (if configured)

---

## DNS Configuration

After deployment, update your DNS records:

```
Type    | Name                | Value
--------|-------------------|------------------------
A       | nymu.com.tw         | <YOUR_SERVER_IP>
A       | www.nymu.com.tw     | <YOUR_SERVER_IP>
CNAME   | api.nymu.com.tw     | nymu.com.tw
CNAME   | admin.nymu.com.tw   | nymu.com.tw
TXT     | _acme-challenge     | (Let's Encrypt will manage this)
```

Allow 24-48 hours for DNS propagation.

---

## Service Access

Once deployed and DNS updated:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend App | https://nymu.com.tw | Main application |
| API Docs | https://nymu.com.tw/api/docs | Swagger documentation |
| API Base | https://nymu.com.tw/api | REST API endpoints |
| Health Check | https://nymu.com.tw/health | System health status |

---

## Post-Deployment Verification

- [ ] Access https://nymu.com.tw and verify frontend loads
- [ ] Check https://nymu.com.tw/api/docs and verify API docs available
- [ ] Test API endpoint: `curl https://nymu.com.tw/api/v1/courses?limit=1`
- [ ] Verify HTTPS certificate is valid: `openssl s_client -connect nymu.com.tw:443`
- [ ] Check SSL rating: https://www.ssllabs.com/ssltest/analyze.html?d=nymu.com.tw
- [ ] Monitor backend logs: `docker logs -f nycu-backend`
- [ ] Monitor frontend logs: `docker logs -f nycu-frontend`
- [ ] Verify cron jobs running: `tail -f /var/log/nycu-platform/performance/metrics.log`

---

## Maintenance & Operations

### Daily Tasks
- [ ] Check system metrics: `/usr/local/bin/nycu-health-check.sh`
- [ ] Review error logs: `grep ERROR /var/log/nycu-platform/*/*.log`
- [ ] Verify all services running: `docker-compose ps`

### Weekly Tasks
- [ ] Check disk space: `df -h /`
- [ ] Review performance metrics: `tail /var/log/nycu-platform/performance/metrics.log`
- [ ] Backup database: `cp /opt/nycu-platform/backend/courses.db /backup/courses.db.$(date +%Y%m%d)`

### Monthly Tasks
- [ ] Review SSL certificate expiration: `certbot certificates`
- [ ] Analyze API response times and error rates
- [ ] Plan capacity upgrades if needed
- [ ] Review and update security policies

### Quarterly Tasks
- [ ] Full system backup
- [ ] Disaster recovery testing
- [ ] Performance optimization review
- [ ] Security audit

---

## Useful Commands

### Service Management
```bash
# View all service logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Start services
docker-compose up -d

# View specific service logs
docker logs -f nycu-backend
docker logs -f nycu-frontend
docker logs -f nycu-nginx
```

### Monitoring
```bash
# Health check
/usr/local/bin/nycu-health-check.sh

# Performance metrics
tail -f /var/log/nycu-platform/performance/metrics.log

# API health
tail -f /var/log/nycu-platform/api/health.log

# System status
systemctl status nycu-platform
```

### SSL/TLS
```bash
# Check certificate status
certbot certificates

# Renew certificates manually
certbot renew --force-renewal

# Test renewal (dry-run)
certbot renew --dry-run

# View certificate details
openssl x509 -in /etc/letsencrypt/live/nymu.com.tw/fullchain.pem -text -noout
```

### Database
```bash
# Access database
sqlite3 /opt/nycu-platform/backend/courses.db

# Check database size
ls -lh /opt/nycu-platform/backend/courses.db

# Backup database
cp /opt/nycu-platform/backend/courses.db /backup/courses.db.backup
```

---

## Troubleshooting

### Services Not Starting
```bash
# Check Docker daemon
systemctl status docker

# View service logs
docker-compose logs

# Restart docker daemon
sudo systemctl restart docker
```

### High CPU Usage
```bash
# Identify resource hogs
docker stats

# Check system load
uptime
top
```

### Disk Space Issues
```bash
# Check disk usage
df -h

# Clean up old logs
find /var/log/nycu-platform -name "*.log" -mtime +30 -delete

# Clean docker artifacts
docker system prune -a
```

### Certificate Issues
```bash
# Check certificate expiration
openssl s_client -connect localhost:443 -showcerts | grep dates

# View renewal logs
tail -f /var/log/letsencrypt/letsencrypt.log

# Force renewal
sudo certbot renew --force-renewal
```

### Network/Connectivity Issues
```bash
# Test backend connectivity
curl http://localhost:8000/health

# Test frontend connectivity
curl http://localhost:3000

# Check container networking
docker network ls
docker network inspect nycu-network
```

---

## Rollback Procedure

If deployment fails or issues occur:

```bash
# Stop all services
docker-compose down

# Restore from backup
cp /backup/courses.db.TIMESTAMP /opt/nycu-platform/backend/courses.db

# Restart services
docker-compose up -d

# Verify health
bash verify-deployment.sh
```

---

## Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API Response Time (p95) | <100ms | >200ms |
| Frontend Load Time | <3s | >5s |
| CPU Usage | <50% | >80% |
| Memory Usage | <60% | >80% |
| Disk Usage | <70% | >85% |
| Error Rate | <0.1% | >1% |
| Uptime | >99.5% | <98% |

---

## Emergency Contacts & Escalation

| Issue | Action | Contact |
|-------|--------|---------|
| Server Down | Check systemctl, restart service | DevOps Team |
| SSL Certificate Expired | Run certbot renew, verify | Security Team |
| Database Corruption | Restore from backup | Database Admin |
| High Resource Usage | Scale horizontally or vertically | Infrastructure Team |
| Security Breach | Isolate system, review logs | Security Team |

---

## Documentation References

- **API Documentation:** `/DEPLOYMENT_GUIDE.md`
- **Architecture:** `/README_PRODUCTION.md`
- **Frontend Setup:** `/frontend/README.md`
- **Backend Setup:** `/backend/README.md`

---

## Sign-Off

- [ ] Deployment approved by DevOps Lead
- [ ] All tests passing
- [ ] Monitoring configured
- [ ] DNS ready for update
- [ ] Backup verified
- [ ] Disaster recovery plan in place

**Deployment Date:** _______________
**Deployed By:** _______________
**Verified By:** _______________

---

**Last Updated:** 2025-10-17
**Version:** 1.0
**Status:** ✅ Ready for Production Deployment
