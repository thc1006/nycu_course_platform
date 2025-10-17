# NYCU Course Platform - Production Deployment Guide

**Platform Name:** NYCU Course Management System
**Version:** 1.0.0
**Domain:** `nymu.com.tw`
**Status:** ✅ Production Ready
**Last Updated:** 2025-10-17

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)
9. [Support](#support)

---

## 🎯 Overview

The NYCU Course Platform is a comprehensive course management system built for National Yang Ming Chiao Tung University.

### Key Features

✅ **Real Course Data**
- 70,239+ courses from academic years 110-114
- Data scraped directly from NYCU official sources
- Complete course information

✅ **Advanced Search**
- Filter by semester, department, credits
- Full-text search capabilities

✅ **Modern UI**
- Responsive design (desktop, tablet, mobile)
- Real-time filtering
- Intuitive course browsing

✅ **Enterprise Ready**
- Docker containerization
- SSL/TLS encryption
- Monitoring and alerting
- Automated backups

---

## 🚀 Quick Start (Production)

### One-Command Deployment

```bash
sudo bash quick-deploy.sh
```

This handles everything:
- Prerequisites check
- Docker setup
- Service deployment
- SSL configuration
- Monitoring setup
- Verification

---

## 🏗️ System Architecture

### Components

```
Users @ https://nymu.com.tw
         ↓
  Nginx Reverse Proxy (443/SSL)
    ↙            ↘
Frontend (3000)  Backend API (8000)
  (Next.js)        (FastAPI)
                    ↓
              SQLite Database
              70,239+ Courses
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | Next.js + React + TailwindCSS | 14.x + 18.x |
| Backend | FastAPI + Uvicorn | Latest |
| Database | SQLite | 3.x |
| Proxy | Nginx | 1.x |
| Container | Docker | Latest |
| SSL | Let's Encrypt | Via Certbot |

---

## 📦 Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose curl git

# Check installations
docker --version
docker-compose --version

# System resources (recommended)
free -h  # 8GB+ RAM
df -h    # 50GB+ disk
nproc    # 4+ cores
```

### Deployment Steps

```bash
# 1. Clone repository
git clone <repo-url> /opt/nycu-platform
cd /opt/nycu-platform

# 2. Run deployment
sudo bash quick-deploy.sh

# 3. Verify
sudo bash verify-deployment.sh

# 4. Configure DNS
# Update your DNS records to point to server IP
```

---

## ⚙️ Configuration

### Environment Files

Edit these before deployment:

**Backend** (`backend/.env.production`):
```bash
DEBUG=false
DOMAIN=nymu.com.tw
CORS_ORIGINS=https://nymu.com.tw
```

**Frontend** (`frontend/.env.production`):
```bash
NEXT_PUBLIC_API_URL=https://nymu.com.tw/api
```

---

## 🌐 Service Access

### Development (Local)
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production
- Frontend: https://nymu.com.tw
- API: https://nymu.com.tw/api
- API Docs: https://nymu.com.tw/api/docs

---

## 📊 Monitoring

### Health Check

```bash
/usr/local/bin/nycu-health-check.sh
```

### View Logs

```bash
docker-compose logs -f
docker logs -f nycu-backend
docker logs -f nycu-frontend
```

### Performance Metrics

```bash
tail -f /var/log/nycu-platform/performance/metrics.log
```

---

## 🔧 Management

### Common Commands

```bash
# View services
docker-compose ps

# Restart service
docker-compose restart nycu-backend

# Stop all services
docker-compose stop

# Start services
docker-compose up -d

# View service logs
docker logs -f nycu-backend
```

### Database Backup

```bash
cp /opt/nycu-platform/backend/courses.db \
   /backup/courses.db.$(date +%Y%m%d)
```

### SSL Certificate Renewal

```bash
certbot renew --dry-run  # Test renewal
certbot renew           # Force renewal
```

---

## 🔍 Troubleshooting

### Backend Not Starting

```bash
docker logs nycu-backend
lsof -i :8000
```

### Frontend Issues

```bash
docker logs nycu-frontend
docker exec nycu-frontend rm -rf .next
docker-compose restart nycu-frontend
```

### High Resource Usage

```bash
docker stats
top
df -h
```

### Database Issues

```bash
# Check integrity
sqlite3 /opt/nycu-platform/backend/courses.db \
  "PRAGMA integrity_check;"

# Repair
sqlite3 /opt/nycu-platform/backend/courses.db "VACUUM;"
```

---

## 📞 Documentation

- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Detailed guide
- `DEPLOYMENT_CHECKLIST.md` - Verification checklist
- `DEPLOYMENT_SUMMARY.md` - Platform overview
- `backend/README.md` - Backend docs
- `frontend/README.md` - Frontend docs

---

## 📈 Performance Targets

| Metric | Target | Alert |
|--------|--------|-------|
| API Response (p95) | <100ms | >200ms |
| Frontend Load | <3s | >5s |
| CPU | <50% | >80% |
| Memory | <60% | >80% |
| Disk | <70% | >85% |
| Error Rate | <0.1% | >1% |
| Uptime | >99.5% | <98% |

---

## 🎯 Deployment Checklist

- [ ] All services running: `docker-compose ps`
- [ ] Backend health: `curl http://localhost:8000/health`
- [ ] Frontend accessible: `curl http://localhost:3001`
- [ ] SSL configured: `certbot certificates`
- [ ] Monitoring active: Check logs
- [ ] DNS updated: `nslookup nymu.com.tw`
- [ ] Backups ready: Check `/backup/`
- [ ] Verification passing: `verify-deployment.sh`

---

## 🎉 Ready!

Your platform is production-ready!

**Status:** ✅ All systems operational
**Last Updated:** 2025-10-17

For help: Check documentation or review logs with `docker-compose logs`
