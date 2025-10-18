# NYCU Course Platform - Deep Scan Report

**Date:** 2025-10-18
**Total Project Size:** 1.4 GB
**Status:** Production-ready with cleanup needed

---

## Executive Summary

Comprehensive deep scan reveals a well-structured full-stack application with:
- **Backend:** FastAPI with 34 Python files
- **Frontend:** Next.js with 29+ TypeScript/React files
- **Scraper:** 40+ Python scraping modules
- **Documentation:** 51 MD files (21,664 lines)

**Critical Issues Identified:**
1. Multiple database versions (6 DB files) - Need consolidation
2. Large files in Git (should use Git LFS)
3. Build artifacts present (953 MB) - Should be excluded

---

## Project Structure

```
nycu_course_platform/ (1.4 GB)
├── frontend/         (674 MB) - Next.js React application
├── scraper/          (349 MB) - Data scraping module
├── backend/          (147 MB) - FastAPI REST API
├── data/             (34 MB)  - Course data files
├── .git/             (~150 MB) - Version control
├── .playwright-mcp/  (~50 MB) - Test screenshots
└── docs/             (168 KB) - Documentation
```

---

## Files by Category

### Active Code Files: 475 Total

#### Backend (34 Python files)
- **Core:** `/backend/app/main.py`, `config.py`, `__init__.py`
- **Database:** 5 files (course.py, semester.py, schedule.py, session.py, base.py)
- **Models:** 3 files (course.py, semester.py, schedule.py)
- **Routes:** 5 files (courses.py, advanced_search.py, search.py, schedules.py, semesters.py)
- **Services:** 5 files (course_service.py, advanced_search_service.py, etc.)
- **Schemas:** 3 files (course.py, semester.py, schedule.py)
- **Utils:** 2 files (cache.py, exceptions.py)
- **Middleware:** 1 file (performance.py)

#### Frontend (29+ TypeScript/React files)
- **Pages:** 7 files (index.tsx, browse.tsx, schedule.tsx, _app.tsx, etc.)
- **Components:** 29+ files across common/, course/, form/, ui/, schedule/
- **Utilities:** 6 files (conflictDetection, courseComparison, nycuParser, etc.)
- **Library:** 2 files (types.ts, utils.ts)

#### Scraper (40+ Python files)
- **Core:** 10+ files (scraper.py, http_client.py, course_parser.py, etc.)
- **Variants:** 20+ different scraper implementations
- **Tests:** 4+ test files

### Configuration Files: 25+

- **Docker:** Dockerfile.backend, Dockerfile.frontend, docker-compose.yml
- **Environment:** .env.example, .env.local, .env.local.example
- **Web Server:** nginx.conf, nginx-local.conf
- **Build:** requirements.txt, package.json, tsconfig.json, tailwind.config.js
- **Git:** .gitignore, .gitattributes
- **Testing:** pytest.ini, jest.config.js, playwright.config.ts

### Documentation: 51 Files

#### Main Guides
- README.md (14 KB) - Primary documentation
- README_PRODUCTION.md (5.6 KB)
- DEPLOYMENT.md, DEPLOYMENT_GUIDE.md (multiple deployment docs)

#### Specialized Guides
- SEO_OPTIMIZATION_GUIDE.md (11 KB)
- OG_IMAGE_CREATION_GUIDE.md (9.6 KB)
- MONITORING_INFRASTRUCTURE_GUIDE.md (12 KB)
- PERFORMANCE_ANALYSIS.md (17 KB)

#### Project Reports
- COMPREHENSIVE_PROJECT_STRUCTURE_ANALYSIS.md (26 KB)
- AUTONOMOUS_DEVELOPMENT_COMPLETE.md (9.0 KB)
- PROJECT_COMPLETION_REPORT.md (7.5 KB)

**Total:** 21,664 lines of documentation

### Data Files

- **JSON:** 10+ course data files
- **Databases:** 6 .db files (48 MB total)
- **Schemas:** schema.sql

### Build & Temporary Files

- **Next.js:** `/frontend/.next/` (653 MB)
- **Node Modules:** `/frontend/node_modules/` (638 MB)
- **Python Virtual Envs:** backend/venv/ (123 MB), scraper/venv/ (192 MB)
- **Cache:** `__pycache__/`, `.pytest_cache/`, `.swc/`

---

## Critical Issues

### 🔴 Database Management
**Problem:** 6 different database files in various locations
- `nycu_course_platform.db` (17 MB) - Main
- `nycu_course_platform.db.current_broken` (14 MB) - Unclear purpose
- `nycu_course_platform.db.backup.*` (4 backup files)
- Various `/backend/` DB copies

**Recommendation:**
- Consolidate to single source of truth
- Delete `.current_broken` file
- Keep only latest 2 backups
- Move backups to `/backups/` directory

### 🔴 Git LFS Configuration
**Problem:** Large files (17 MB databases) tracked in regular Git

**Current LFS Config:**
```
.node files
scraper/data/real_courses_nycu/raw_data_all_semesters.json
```

**Recommendation:**
```bash
git lfs track "*.db"
git lfs track "*.sqlite"
git lfs track "scraper/data/**/*.json"
```

### 🔴 Build Artifacts in Repository
**Problem:** 953 MB of dependencies and build files

- `/frontend/node_modules/` - 638 MB
- `/backend/venv/` - 123 MB
- `/scraper/venv/` - 192 MB

**Recommendation:** Verify these are in `.gitignore` and not committed

---

## Warnings

### 🟡 Excessive Documentation
**Issue:** 51 markdown files, many are progress reports

**Examples:**
- DEPLOYMENT_COMPLETE.md
- DEPLOYMENT_COMPLETE_REPORT.md
- DEPLOYMENT_COMPLETE_SUMMARY.md
- AUTONOMOUS_DEVELOPMENT_COMPLETE.md

**Recommendation:** Archive old reports to `/docs/archived/`

### 🟡 Multiple Scraper Implementations
**Issue:** 20+ different scraper files

**Examples:**
- nycu_real_scraper.py
- real_course_scraper.py
- advanced_real_scraper.py
- scraper_v2_real.py
- playwright_scraper.py

**Recommendation:**
- Keep primary: `/scraper/app/scraper.py`
- Archive others: `/scraper/archived/`

### 🟡 Deployment Script Confusion
**Issue:** 6+ deployment scripts with unclear purpose

- deploy-production.sh
- deploy-ssl.sh
- quick-deploy.sh
- production_deploy.sh

**Recommendation:** Standardize on single deployment script

### 🟡 Component Folder Casing
**Issue:** Inconsistent naming conventions

- `/frontend/components/Common/` (capital C)
- `/frontend/components/common/` (lowercase c)

**Recommendation:** Standardize to lowercase

---

## Size Analysis

### Distribution
```
Total: 1.4 GB

Components:
- frontend/           674 MB (48%) - Includes node_modules
- scraper/           349 MB (25%) - Includes venv
- backend/           147 MB (10%) - Includes venv
- .git/              150 MB (11%) - Version history
- data/              34 MB  (2%)  - Course data
- .playwright-mcp/   50 MB  (3%)  - Test artifacts
- Databases          48 MB  (3%)  - 6 DB files
```

### Production-Ready Size
**After cleanup:** ~350 MB (75% reduction)

### Largest Files
1. frontend/node_modules/ - 638 MB
2. scraper/venv/ - 192 MB
3. backend/venv/ - 123 MB
4. frontend/.next/ - 653 MB (build)
5. nycu_course_platform.db - 17 MB
6. Database backups - 31 MB

---

## Git Status

### Modified Files (14 files)
1. backend/app/database/course.py
2. backend/app/models/course.py
3. backend/app/models/semester.py
4. backend/app/routes/courses.py
5. backend/app/services/course_service.py
6. frontend/components/common/Footer.tsx
7. frontend/components/common/Header.tsx
8. frontend/components/course/CourseCard.tsx
9. frontend/components/ui/button.tsx
10. frontend/pages/browse.tsx
11. frontend/pages/index.tsx
12. frontend/pages/schedule.tsx
13. frontend/tailwind.config.js
14. nginx.conf

### Untracked Files
- .playwright-mcp/*.png (screenshots)
- NDHU_COURSE_PLATFORM_COMPLETE_SPECIFICATION.md
- backend/import_syllabi.py
- data/real_courses_nycu/
- frontend/components/ui/badge.tsx
- monitor_scraper.sh
- scraper/data/course_outlines/

---

## Cleanup Recommendations

### Priority 1: Data Integrity
1. Consolidate databases
2. Configure Git LFS for large files
3. Delete broken database file

### Priority 2: Repository Cleanup
1. Remove build artifacts (if in git)
2. Verify node_modules/venv are ignored
3. Archive old documentation

### Priority 3: Code Quality
1. Remove experimental scrapers
2. Consolidate deployment scripts
3. Standardize component naming

---

## Action Plan

### Immediate Actions
```bash
# 1. Consolidate databases
mkdir -p backups
mv nycu_course_platform.db.backup.* backups/
rm nycu_course_platform.db.current_broken

# 2. Configure Git LFS
git lfs track "*.db"
git lfs track "*.sqlite"
git add .gitattributes

# 3. Archive documentation
mkdir -p docs/archived
mv DEPLOYMENT_*_COMPLETE*.md docs/archived/
mv AUTONOMOUS_*.md docs/archived/

# 4. Archive experimental scrapers
mkdir -p scraper/archived
mv scraper/*_scraper*.py scraper/archived/
# Keep only scraper/app/scraper.py
```

### Verification
```bash
# Check .gitignore
cat .gitignore | grep -E "node_modules|venv|\.next"

# Check Git LFS
git lfs ls-files

# Check repository size
git count-objects -vH
```

---

## Conclusion

**Status:** Well-structured production-ready application

**Strengths:**
✅ Clean separation of concerns
✅ Comprehensive documentation
✅ Multiple deployment strategies
✅ Active development

**Needs Improvement:**
⚠️ Database consolidation
⚠️ Repository size optimization
⚠️ Documentation archival
⚠️ Code cleanup

**Expected Impact:**
- Repository size: 1.4 GB → 350 MB (75% reduction)
- Clarity: Much improved with consolidated docs
- Maintainability: Better with archived experimental code

---

**Next Steps:**
1. Execute cleanup actions
2. Update .gitignore
3. Configure Git LFS completely
4. Archive old documentation
5. Remove experimental code
6. Commit and push changes

---

*Generated: 2025-10-18*
*Tool: Claude Code Explore Agent*
