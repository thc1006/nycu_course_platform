# NYCU Course Platform - Quick Fix Guide

**Status**: 3 Critical Issues Found
**Fix Time**: ~1-2 hours
**Last Updated**: 2025-10-17

---

## ISSUE #1: Backend Won't Start - CRITICAL

### Symptom
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

### Quick Fix (5 minutes)
```bash
cd /home/thc1006/dev/nycu_course_platform/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Verify
```bash
cd /home/thc1006/dev/nycu_course_platform
export PYTHONPATH=/home/thc1006/dev/nycu_course_platform:$PYTHONPATH
cd backend
uvicorn backend.app.main:app --reload --port 8000
# Should see: Uvicorn running on http://0.0.0.0:8000
```

### Test
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "database": "connected"}
```

---

## ISSUE #2: Frontend Can't Connect - HIGH

### Symptom
"Failed to load semesters" error on frontend

### Quick Fix (3 minutes)
```bash
# Create env file
cp /home/thc1006/dev/nycu_course_platform/frontend/.env.local.example \
   /home/thc1006/dev/nycu_course_platform/frontend/.env.local

# Verify content
cat /home/thc1006/dev/nycu_course_platform/frontend/.env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Verify
```bash
cd /home/thc1006/dev/nycu_course_platform/frontend
npm run dev
# Open browser: http://localhost:3000
# Semesters should load without error
```

---

## ISSUE #3: Wrong Database - MEDIUM

### Symptom
API returns empty results even though database exists

### Quick Fix (2 minutes)
```bash
# Edit backend/app/config.py line 27
# OLD: DATABASE_URL: str = "sqlite+aiosqlite:///./nycu_course_platform.db"
# NEW: DATABASE_URL: str = "sqlite+aiosqlite:///./course_platform.db"

# Or use environment variable
export DATABASE_URL="sqlite+aiosqlite:///./course_platform.db"
```

### Verify Which Database to Use
```bash
ls -lh /home/thc1006/dev/nycu_course_platform/backend/*.db

# Should see:
# 24MB  course_platform.db         ← USE THIS (has data)
# 32KB  nycu_course_platform.db    ← NOT THIS (empty)
```

---

## Complete Startup Sequence

### Terminal 1: Backend
```bash
cd /home/thc1006/dev/nycu_course_platform

# Setup environment
export PYTHONPATH=/home/thc1006/dev/nycu_course_platform:$PYTHONPATH
export DATABASE_URL="sqlite+aiosqlite:///./course_platform.db"

# Start backend
cd backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000

# Verify: http://localhost:8000/health
# Verify: http://localhost:8000/api/semesters/
```

### Terminal 2: Frontend
```bash
cd /home/thc1006/dev/nycu_course_platform/frontend

# Ensure .env.local exists
test -f .env.local || cp .env.local.example .env.local

# Start frontend
npm run dev

# Open: http://localhost:3000
```

### Test Endpoints

```bash
# Backend health check
curl http://localhost:8000/health

# Get semesters
curl http://localhost:8000/api/semesters/

# Get courses for semester 113, sem 1
curl "http://localhost:8000/api/courses/?acy=113&sem=1&limit=5"

# Test API docs
# Open: http://localhost:8000/docs
```

---

## Checklist for "Just Make It Work"

- [ ] Run: `cd /home/thc1006/dev/nycu_course_platform/backend && source venv/bin/activate && pip install -r requirements.txt`
- [ ] Run: `cp /home/thc1006/dev/nycu_course_platform/frontend/.env.local.example /home/thc1006/dev/nycu_course_platform/frontend/.env.local`
- [ ] Edit: `backend/app/config.py` line 27 - change database URL
- [ ] Terminal 1: Start backend with PYTHONPATH set
- [ ] Terminal 2: Start frontend
- [ ] Verify: http://localhost:8000/health returns 200
- [ ] Verify: http://localhost:3000 loads without errors
- [ ] Verify: Semesters dropdown populates with data

---

## Files Modified to Fix Issues

1. **backend/app/config.py** (Line 27)
   - OLD: `DATABASE_URL: str = "sqlite+aiosqlite:///./nycu_course_platform.db"`
   - NEW: `DATABASE_URL: str = "sqlite+aiosqlite:///./course_platform.db"`

2. **frontend/.env.local** (Create new file)
   - Copy from `.env.local.example`
   - Ensure: `NEXT_PUBLIC_API_URL=http://localhost:8000/api`

3. **Environment Setup** (Every session)
   - Set: `export PYTHONPATH=/home/thc1006/dev/nycu_course_platform:$PYTHONPATH`
   - Set: `export DATABASE_URL="sqlite+aiosqlite:///./course_platform.db"`

---

## Common Issues & Solutions

### "ModuleNotFoundError: No module named 'backend'"
**Solution**: Set PYTHONPATH before running
```bash
export PYTHONPATH=/home/thc1006/dev/nycu_course_platform:$PYTHONPATH
```

### "Failed to load semesters" in frontend
**Solution**: 
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check frontend .env.local exists and has correct API_URL
3. Check browser console for CORS errors

### "sqlite3.OperationalError: no such table"
**Solution**: Using wrong database file
```bash
# Check which file is being used
export DATABASE_URL="sqlite+aiosqlite:///./course_platform.db"
```

### Frontend stuck on localhost:3001 instead of 3000
**Solution**: Either is fine, but make sure CORS_ORIGINS includes it
- Check: `backend/app/config.py` CORS_ORIGINS list (lines 40-44)
- Add port if needed: `"http://localhost:3001"`

---

## Database Recovery

If something goes wrong:

```bash
# Backup current state
cp backend/course_platform.db backend/course_platform.db.backup

# Check what's in the databases
# (requires sqlite3 tool)
# sqlite3 backend/course_platform.db ".tables"
# sqlite3 backend/course_platform.db "SELECT COUNT(*) FROM course;"

# Use backup
cp backend/course_platform.db.backup backend/course_platform.db
```

---

## Next Steps After Getting Working

1. Run tests: `cd backend && pytest`
2. Run frontend tests: `cd frontend && npm test`
3. Check deployment readiness: Review `COMPREHENSIVE_ANALYSIS_REPORT.md`
4. Prepare for production: Follow `PRODUCTION_DEPLOYMENT_GUIDE.md`

---

**Need more details?** See `COMPREHENSIVE_ANALYSIS_REPORT.md`
