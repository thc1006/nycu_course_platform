# NYCU Course Platform - Deployment Guide

## System Status

###Current State (Development)
- ✅ Backend API: Running on http://localhost:8000
- ✅ Frontend: Running on http://localhost:3003
- ✅ Database: 33,554 courses imported across 9 semesters
- ✅ Schedule API: Fully functional and integrated

### What's Completed
1. ✅ Schedule API integration with homepage
2. ✅ All course data imported (70,239 entries → 33,554 unique courses)
3. ✅ Nginx configuration prepared (`nginx-local.conf` for testing, `nginx.conf` for production)

---

## Quick Start Testing

The platform is currently running in development mode and ready for testing:

```bash
# Access the application
Frontend: http://localhost:3003
API: http://localhost:8000/api/
API Docs: http://localhost:8000/docs

# Test endpoints
curl http://localhost:8000/api/semesters
curl "http://localhost:8000/api/courses/?acy=113&sem=1&limit=10"
curl http://localhost:8000/api/schedules/user/guest_user
```

---

## Production Deployment Steps

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx -y
nginx -v
```

### 2. Build Frontend for Production

```bash
cd /home/thc1006/dev/nycu_course_platform/frontend
npm install
npm run build
```

### 3. Create Systemd Services

Create `/etc/systemd/system/nycu-backend.service`:
```ini
[Unit]
Description=NYCU Course Platform Backend API
After=network.target

[Service]
Type=simple
User=thc1006
WorkingDirectory=/home/thc1006/dev/nycu_course_platform
Environment="PATH=/home/thc1006/dev/nycu_course_platform/backend/venv/bin"
ExecStart=/home/thc1006/dev/nycu_course_platform/backend/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/nycu-frontend.service`:
```ini
[Unit]
Description=NYCU Course Platform Frontend
After=network.target

[Service]
Type=simple
User=thc1006
WorkingDirectory=/home/thc1006/dev/nycu_course_platform/frontend
Environment="NODE_ENV=production"
Environment="PORT=3003"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 4. Deploy Services

```bash
# Start backend
sudo systemctl enable nycu-backend
sudo systemctl start nycu-backend
sudo systemctl status nycu-backend

# Start frontend
sudo systemctl enable nycu-frontend
sudo systemctl start nycu-frontend
sudo systemctl status nycu-frontend
```

### 5. Configure Nginx

```bash
# For testing (HTTP localhost)
sudo cp nginx-local.conf /etc/nginx/nginx.conf

# OR for production (HTTPS with domain)
sudo cp nginx.conf /etc/nginx/nginx.conf

# Test and restart
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 6. Verify Deployment

```bash
curl http://localhost/health
curl http://localhost/api/semesters
curl -I http://localhost/
```

---

## Architecture

```
Client → Nginx (Port 80/443)
   ├→ Frontend (Port 3003)
   ├→ Backend API (Port 8000)
   └→ SQLite Database (33,554 courses)
```

---

## Monitoring

```bash
# Service status
sudo systemctl status nycu-backend nycu-frontend nginx

# Logs
sudo journalctl -u nycu-backend -f
sudo journalctl -u nycu-frontend -f
sudo tail -f /var/log/nginx/access.log

# Database backup
cp nycu_course_platform.db backups/backup_$(date +%Y%m%d).db
```

---

## Next Steps

1. Install nginx: `sudo apt install nginx`
2. Test current setup: `curl http://localhost:3003` and `curl http://localhost:8000/api/semesters`
3. Deploy systemd services (requires sudo)
4. Configure and start nginx

For detailed instructions, see sections above.
