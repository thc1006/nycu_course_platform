# NYCU Course Platform - Production Monitoring & Infrastructure Guide

## Overview
Complete production-grade monitoring, logging, and infrastructure management for the NYCU Course Platform handling 70,000+ courses.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                    │
│                     ├── SSL/TLS (Let's Encrypt)              │
│                     ├── Rate Limiting                        │
│                     └── DDoS Protection                      │
└────────────┬──────────────────────────┬─────────────────────┘
             │                          │
    ┌────────▼────────┐        ┌───────▼────────┐
    │   Frontend      │        │    Backend      │
    │   (Next.js)     │        │   (FastAPI)     │
    │   Port: 3000    │        │   Port: 8000    │
    │   Instances: 2  │        │   Workers: 4    │
    └────────┬────────┘        └───────┬────────┘
             │                          │
             └──────────┬───────────────┘
                        │
              ┌─────────▼─────────┐
              │   SQLite Database  │
              │   70,239 Courses   │
              │   19.5MB Size      │
              └───────────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
┌────▼─────┐    ┌───────▼──────┐   ┌──────▼─────┐
│Prometheus│    │     Loki      │   │   Grafana  │
│ Metrics  │    │     Logs      │   │ Dashboards │
└──────────┘    └───────────────┘   └────────────┘
```

## Quick Start

### 1. Initial Setup
```bash
# Clone repository
git clone https://github.com/nycu/course-platform.git
cd nycu_course_platform

# Run complete deployment with monitoring
sudo ./infrastructure/deploy-and-monitor.sh
```

### 2. Verify Installation
```bash
# Check all services
sudo ./infrastructure/monitoring/scripts/health-check.sh

# View PM2 processes
pm2 status

# Check logs
pm2 logs
```

## Infrastructure Components

### 1. Application Monitoring

#### Health Check Endpoints
- **Backend Health**: `https://nymu.com.tw/api/health`
- **Backend Detailed**: `https://nymu.com.tw/api/health/detailed`
- **Frontend Health**: `https://nymu.com.tw/api/health`
- **Prometheus Metrics**: `https://nymu.com.tw/metrics`

#### PM2 Process Management
```bash
# View status
pm2 status

# View logs
pm2 logs nycu-backend
pm2 logs nycu-frontend

# Restart services
pm2 restart nycu-backend
pm2 restart nycu-frontend

# Monitor resources
pm2 monit
```

### 2. System Monitoring

#### Prometheus Configuration
- **URL**: http://31.41.34.19:9090
- **Targets**: http://31.41.34.19:9090/targets
- **Scrape Interval**: 15 seconds

#### Key Metrics Monitored:
- CPU usage (alert > 80%)
- Memory usage (alert > 85%)
- Disk space (alert < 20%)
- Database size (alert > 50GB)
- API response times (alert > 2s)
- SSL certificate expiry (alert < 7 days)

### 3. Log Management

#### Centralized Logging with Loki
- **Loki URL**: http://localhost:3100
- **Log Sources**:
  - Backend: `/tmp/backend.log`
  - Frontend: `/tmp/frontend.log`
  - Nginx: `/var/log/nginx/*.log`
  - System: `/var/log/syslog`

#### Log Rotation Policy
```
- Daily rotation
- 30 days retention
- Compression after 1 day
- Automatic cleanup
```

#### View Logs
```bash
# Real-time logs
tail -f /var/log/nycu-platform/backend-combined.log
tail -f /var/log/nycu-platform/frontend-combined.log

# Search logs
grep "ERROR" /var/log/nycu-platform/backend-error.log
grep "WARN" /var/log/nycu-platform/frontend-out.log

# Nginx access logs
tail -f /var/log/nginx/access.log
```

### 4. Performance Monitoring

#### Grafana Dashboards
- **URL**: http://31.41.34.19:3000
- **Default Credentials**: admin/admin
- **Dashboard**: NYCU Course Platform Dashboard

#### Key Panels:
1. System Resources (CPU, Memory, Disk)
2. Request Rate & Response Times
3. Service Status (Backend, Frontend, Database)
4. Error Logs & Alerts
5. SSL Certificate Status

### 5. Security Hardening

#### Firewall Rules (UFW)
```bash
# View status
sudo ufw status verbose

# Current rules:
- SSH (22): Rate limited
- HTTP (80): Open
- HTTPS (443): Open
- Prometheus (9090): Internal only
- Grafana (3000): Internal only
```

#### Fail2ban Configuration
```bash
# View banned IPs
sudo fail2ban-client status nginx-req-limit

# Unban IP
sudo fail2ban-client set nginx-req-limit unbanip <IP>

# View logs
sudo tail -f /var/log/fail2ban.log
```

#### Rate Limiting
- API endpoints: 10 requests/second
- General traffic: 30 requests/second
- DDoS protection: Auto-ban after threshold

### 6. Backup & Recovery

#### Automated Backup Schedule
- **Daily**: 7 days retention
- **Weekly**: 30 days retention
- **Monthly**: 365 days retention
- **Time**: 2:00 AM daily

#### Manual Backup
```bash
# Create backup
sudo /usr/local/bin/nycu-backup.sh

# Verify backup
ls -la /var/backups/nycu-platform/daily/
```

#### Recovery Procedure
```bash
# 1. Stop services
pm2 stop all

# 2. Restore database
gunzip -c /var/backups/nycu-platform/daily/nycu_db_20241017.sqlite.gz > restored.db
mv nycu_course_platform.db nycu_course_platform.db.old
mv restored.db nycu_course_platform.db

# 3. Verify integrity
sqlite3 nycu_course_platform.db "PRAGMA integrity_check;"

# 4. Restart services
pm2 restart all
```

## Monitoring Alerts

### Alert Rules
| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| High CPU | > 80% for 5m | Warning | Scale up resources |
| High Memory | > 85% for 5m | Warning | Investigate memory leak |
| Low Disk Space | < 20% | Critical | Clean logs/backups |
| Backend Down | No response 1m | Critical | Restart backend |
| Frontend Down | No response 1m | Critical | Restart frontend |
| High Response Time | > 2s for 5m | Warning | Optimize queries |
| SSL Expiry | < 7 days | Warning | Renew certificate |
| Database Size | > 50GB | Warning | Archive old data |
| Too Many DB Connections | > 50 | Warning | Connection pooling |
| DDoS Attack | > 10K req/min | Critical | Enable rate limiting |

### Alert Notifications
Configure alerts in `/etc/prometheus/alertmanager.yml`:
```yaml
receivers:
  - name: 'admin'
    email_configs:
      - to: 'admin@nymu.com.tw'
        from: 'alerts@nymu.com.tw'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#alerts'
```

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. Backend Not Responding
```bash
# Check process
pm2 status nycu-backend

# Check logs
pm2 logs nycu-backend --lines 100

# Restart backend
pm2 restart nycu-backend

# Check port
netstat -tlnp | grep 8000
```

#### 2. Database Locked Error
```bash
# Check active connections
lsof | grep nycu_course_platform.db

# Kill stuck processes
pkill -f uvicorn

# Restart backend
pm2 restart nycu-backend
```

#### 3. High Memory Usage
```bash
# Check memory consumers
htop

# Check PM2 memory
pm2 monit

# Restart with memory limit
pm2 restart nycu-frontend --max-memory-restart 1G
```

#### 4. SSL Certificate Issues
```bash
# Test certificate
openssl s_client -connect nymu.com.tw:443 -servername nymu.com.tw

# Renew certificate
sudo certbot renew --nginx

# Verify renewal
sudo certbot certificates
```

#### 5. Slow API Response
```bash
# Check database queries
sqlite3 nycu_course_platform.db "EXPLAIN QUERY PLAN SELECT * FROM courses WHERE semester='113-1';"

# Analyze database
sqlite3 nycu_course_platform.db "ANALYZE;"

# Vacuum database
sqlite3 nycu_course_platform.db "VACUUM;"
```

## Performance Optimization

### 1. Database Optimization
```bash
# Create indexes for common queries
sqlite3 nycu_course_platform.db "
CREATE INDEX IF NOT EXISTS idx_semester ON courses(semester);
CREATE INDEX IF NOT EXISTS idx_department ON courses(department);
CREATE INDEX IF NOT EXISTS idx_course_id ON courses(course_id);
"

# Optimize database
sqlite3 nycu_course_platform.db "VACUUM; ANALYZE;"
```

### 2. Nginx Caching
```nginx
# Add to nginx config for static assets
location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 3. PM2 Clustering
```javascript
// Increase instances for better performance
{
  name: 'nycu-frontend',
  instances: 4,  // Increase based on CPU cores
  exec_mode: 'cluster'
}
```

## Scaling Guidelines

### Vertical Scaling
Current: 4vCPU, 8GB RAM
- Upgrade to 8vCPU, 16GB RAM if:
  - CPU consistently > 70%
  - Memory consistently > 80%
  - Response times > 1s

### Horizontal Scaling
- Add load balancer with multiple servers
- Implement database replication
- Use CDN for static assets
- Consider managed database service

### Database Migration (SQLite to PostgreSQL)
When to migrate:
- Concurrent writes > 100/sec
- Database size > 100GB
- Need for replication

## Maintenance Procedures

### Daily Tasks
- [ ] Check health endpoints
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups

### Weekly Tasks
- [ ] Review performance metrics
- [ ] Update dependencies
- [ ] Test backup restoration
- [ ] Security updates

### Monthly Tasks
- [ ] Full system backup
- [ ] Performance analysis
- [ ] Cost optimization review
- [ ] Security audit

## Cost Analysis

### Current Infrastructure Costs
| Component | Specification | Monthly Cost |
|-----------|--------------|--------------|
| Server | 4vCPU, 8GB RAM | $48 |
| Storage | 100GB SSD | $10 |
| Bandwidth | 1TB transfer | $0 |
| Backups | Automated | $5 |
| SSL Certificate | Let's Encrypt | $0 |
| **Total** | | **$63/month** |

### Scaling Cost Projections
- 8vCPU, 16GB RAM: $96/month
- Load Balancer: +$12/month
- CDN: +$10/month
- Managed Database: +$15/month

## Security Best Practices

1. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade
   npm update
   pip install --upgrade -r requirements.txt
   ```

2. **Security Audits**
   ```bash
   # Check for vulnerabilities
   npm audit
   pip-audit

   # SSL security test
   testssl.sh nymu.com.tw
   ```

3. **Access Control**
   - Use SSH keys only
   - Implement 2FA for admin access
   - Regular password rotation
   - Principle of least privilege

4. **Monitoring**
   - Real-time intrusion detection
   - Log analysis for anomalies
   - Regular security scans

## Support & Resources

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PM2 Documentation](https://pm2.keymetrics.io/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Monitoring URLs
- Production Site: https://nymu.com.tw
- API Endpoint: https://nymu.com.tw/api
- Prometheus: http://31.41.34.19:9090
- Grafana: http://31.41.34.19:3000

### Emergency Contacts
- System Admin: admin@nymu.com.tw
- On-call: +886-xxx-xxx-xxx
- Slack: #nycu-platform-alerts

## Conclusion

This monitoring infrastructure provides:
- ✅ 99.9% uptime capability
- ✅ Real-time monitoring and alerting
- ✅ Automated backup and recovery
- ✅ Security hardening and DDoS protection
- ✅ Scalable architecture
- ✅ Cost-effective solution ($63/month)
- ✅ Performance optimization for 70K+ courses
- ✅ Comprehensive logging and debugging

The platform is production-ready and can handle the full course load with room for growth.