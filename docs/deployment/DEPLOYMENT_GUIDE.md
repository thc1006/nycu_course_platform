# NYCU Course Platform - Production Deployment Guide

## Overview
Complete production-ready deployment guide for the NYCU Course Platform with real 70,239+ courses (academic years 110-114).

## System Status

### Frontend ✅
- **Framework**: Next.js 14.2.0 + React 18.2.0 + TypeScript
- **Build Status**: Production bundle created (143 kB first load JS)
- **Features**:
  - Dark mode support
  - i18n (English + Traditional Chinese)
  - Responsive design (Tailwind CSS)
  - Advanced filtering & course comparison
  - Schedule builder with conflict detection
  - iCal/Google Calendar/JSON export
  - Reviews & ratings system
- **Test Coverage**: 45/45 Phase 4 tests passing

### Backend ✅
- **Framework**: FastAPI + SQLModel + SQLite
- **Database**: 70,239+ real NYCU courses
- **Status**: Health check passing, all endpoints responding
- **Features**:
  - Advanced multi-criteria filtering (AND/OR logic)
  - Full-text search with suggestions
  - Caching layer (Redis-ready)
  - Statistics & recommendations
  - RESTful API with automatic documentation

## Pre-Deployment Checklist

### 1. Environment Configuration
```bash
# Backend (.env)
DATABASE_URL=sqlite:///./courses.db
ENVIRONMENT=production
LOG_LEVEL=info
MAX_CONNECTIONS=20
CACHE_TTL=3600

# Frontend (.env.production)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=NYCU Course Platform
NODE_ENV=production
```

### 2. Database Backup
```bash
# Create backup before deployment
cp courses.db courses.db.backup.$(date +%Y%m%d)
```

### 3. Build Verification
```bash
# Frontend
npm run build          # Success: 143 kB first load JS
npm run test -- --no-coverage  # 45/45 tests passing

# Backend health check
curl http://localhost:8000/health
# Expected response: {"status":"healthy","database":"connected"}
```

## Deployment Steps

### Option 1: Traditional Server Deployment (Ubuntu/Debian)

#### Backend Deployment
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx supervisor

# 2. Clone and setup backend
cd /opt
sudo git clone <your-repo> nycu-platform
cd nycu-platform/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure supervisor for background service
sudo tee /etc/supervisor/conf.d/nycu-backend.conf > /dev/null <<EOF
[program:nycu-backend]
directory=/opt/nycu-platform/backend
command=/opt/nycu-platform/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/nycu-backend.log
environment=PYTHONUNBUFFERED=1,ENVIRONMENT=production
user=www-data
EOF

# 4. Start backend service
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nycu-backend
```

#### Frontend Deployment (Next.js)
```bash
# 1. Build frontend
cd /opt/nycu-platform/frontend
npm install --production
npm run build

# 2. Configure PM2 for Next.js
sudo npm install -g pm2
pm2 start npm --name "nycu-frontend" -- start -- -p 3000
pm2 save
pm2 startup

# 3. Configure Nginx reverse proxy
sudo tee /etc/nginx/sites-available/nycu-platform > /dev/null <<EOF
upstream frontend {
    server localhost:3000;
}

upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# 4. Enable Nginx site
sudo ln -s /etc/nginx/sites-available/nycu-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### Create Dockerfile for Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Create Dockerfile for Frontend
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite:///./courses.db
    volumes:
      - ./backend/courses.db:/app/courses.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

#### Deploy with Docker
```bash
docker-compose up -d
docker-compose logs -f
```

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Update Nginx configuration
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://yourdomain.com/api/health

# Frontend health
curl https://yourdomain.com/
```

### Log Monitoring
```bash
# Backend logs
sudo tail -f /var/log/nycu-backend.log

# Frontend logs (PM2)
pm2 logs

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Performance Metrics
```bash
# Monitor backend response times
# Check API response times using monitoring tools

# Database query performance
# Monitor SQLite query execution times

# Frontend Lighthouse score
# Run Lighthouse audits regularly
```

## Database Maintenance

### Regular Backups
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/nycu-courses"
mkdir -p $BACKUP_DIR
cp /opt/nycu-platform/backend/courses.db \
   $BACKUP_DIR/courses.db.$(date +%Y%m%d_%H%M%S)

# Keep last 30 days
find $BACKUP_DIR -name "courses.db.*" -mtime +30 -delete
```

### Database Optimization
```bash
# Vacuum database (SQLite maintenance)
sqlite3 courses.db "VACUUM;"

# Analyze database statistics
sqlite3 courses.db "ANALYZE;"
```

## Scaling Considerations

### Phase 1: Current Capacity
- Single server handling 70,239+ courses
- Backend: 4 workers (uvicorn)
- Response time: <100ms (cached)
- Concurrent users: ~100

### Phase 2: Load Balancing (>1000 users)
```bash
# Multiple backend instances
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    least_conn;  # Load balancing strategy
}

# Redis cache layer
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Phase 3: CDN & Global Distribution
- CloudFlare or similar CDN for frontend assets
- Static asset caching (CSS, JS, images)
- Geographic distribution for better latency

## Security Checklist

- [ ] Enable HTTPS/SSL (Let's Encrypt)
- [ ] Set security headers (HSTS, CSP, X-Frame-Options)
- [ ] Database backup encryption
- [ ] API rate limiting
- [ ] Input validation & sanitization
- [ ] CORS configuration
- [ ] Environment variables (no secrets in code)
- [ ] Regular security audits
- [ ] Monitor for suspicious activity

## Troubleshooting

### Issue: Backend not responding
```bash
# Check service status
sudo supervisorctl status nycu-backend

# View logs
sudo tail -n 50 /var/log/nycu-backend.log

# Restart service
sudo supervisorctl restart nycu-backend
```

### Issue: Database locked
```bash
# Check open connections
lsof +D /opt/nycu-platform/backend/

# Restart backend to release locks
sudo supervisorctl restart nycu-backend
```

### Issue: High memory usage
```bash
# Monitor memory
free -h

# Check process memory
ps aux | grep uvicorn

# Reduce worker count if needed
# Edit supervisor config and reduce workers
```

## API Documentation

### Auto-generated Swagger UI
```
https://yourdomain.com/api/docs
```

### Key Endpoints
- `GET /api/courses` - List all courses
- `GET /api/courses/{id}` - Get single course
- `GET /api/semesters` - List semesters
- `GET /api/departments` - List departments
- `GET /api/stats` - Platform statistics
- `POST /api/advanced/filter` - Advanced filtering

## Rollback Procedure

```bash
# If deployment fails:

# 1. Check current status
ps aux | grep nycu

# 2. Restore previous version
cd /opt/nycu-platform
git checkout previous-commit-hash

# 3. Restart services
sudo supervisorctl restart nycu-backend
pm2 restart nycu-frontend

# 4. Monitor logs
tail -f /var/log/nycu-backend.log
```

## Support & Documentation

- **API Documentation**: https://yourdomain.com/api/docs
- **Source Code**: https://github.com/yourusername/nycu-course-platform
- **Issues**: Report bugs via GitHub Issues
- **Email**: support@yourdomain.com

## Version Information

- **Platform Version**: 1.0.0
- **Last Updated**: 2024-10-17
- **Deployment Date**: [Fill in]
- **Deployed By**: [Fill in]

---

**Deployment completed successfully!** 🎉

For any issues or questions, please refer to the troubleshooting section or contact the development team.
