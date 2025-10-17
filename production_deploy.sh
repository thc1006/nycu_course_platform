#!/bin/bash

################################################################################
# NYCU Course Platform - Production Deployment Script
# Server: 31.41.34.19
# Domain: nymu.com.tw
# This script will deploy the complete system to production
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/thc1006/dev/nycu_course_platform"
DB_PATH="$PROJECT_ROOT/nycu_course_platform.db"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
SCHEMA_SQL="$PROJECT_ROOT/data/schema.sql"
LOG_DIR="/var/log/nycu-platform"
VENV="$BACKEND_DIR/venv"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                   NYCU COURSE PLATFORM - PRODUCTION DEPLOY                ║"
    echo "║                                                                            ║"
    echo "║        Server IP: 31.41.34.19     Domain: nymu.com.tw                    ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Step 1: Kill all existing processes
kill_existing_processes() {
    log_info "Step 1/6: Killing existing processes..."

    pkill -9 -f "uvicorn" 2>/dev/null || true
    pkill -9 -f "next dev" 2>/dev/null || true
    pkill -9 -f "npm run dev" 2>/dev/null || true
    pkill -9 -f "fetch_real_courses" 2>/dev/null || true
    pkill -9 -f "scraper_v2_real" 2>/dev/null || true
    pkill -9 -f "nycu_github_scraper" 2>/dev/null || true

    sleep 2
    log_success "All processes terminated"
}

# Step 2: Initialize database
init_database() {
    log_info "Step 2/6: Initializing database..."

    if [ -f "$DB_PATH" ]; then
        log_warn "Database already exists, backing up..."
        cp "$DB_PATH" "$DB_PATH.backup.$(date +%s)"
    fi

    # Create fresh database with schema
    if [ -f "$SCHEMA_SQL" ]; then
        sqlite3 "$DB_PATH" < "$SCHEMA_SQL"
        log_success "Database initialized with schema"
    else
        log_error "Schema file not found: $SCHEMA_SQL"
        return 1
    fi

    # Verify tables exist
    TABLES=$(sqlite3 "$DB_PATH" ".tables")
    if [[ "$TABLES" == *"courses"* ]] && [[ "$TABLES" == *"semesters"* ]]; then
        log_success "Database tables verified: $TABLES"
    else
        log_error "Database tables missing!"
        return 1
    fi
}

# Step 3: Seed with demo data
seed_demo_data() {
    log_info "Step 3/6: Seeding database with demo data..."

    # Create temporary Python script to seed data
    cat > /tmp/seed_db.py << 'PYTHON_EOF'
import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else "nycu_course_platform.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert sample semesters
semesters = [
    (113, 1),
    (113, 2),
]

for acy, sem in semesters:
    cursor.execute(
        "INSERT OR IGNORE INTO semesters (acy, sem) VALUES (?, ?)",
        (acy, sem)
    )

# Get semester IDs
cursor.execute("SELECT id, acy, sem FROM semesters")
sem_map = {(acy, sem): sid for sid, acy, sem in cursor.fetchall()}

# Insert sample courses
sample_courses = [
    (sem_map[(113, 1)], "CHEM0160", "General Chemistry II", 3.0, "Dr. Carol Liu", "CHEM", "Mon 09:00-12:00"),
    (sem_map[(113, 1)], "PHYS0210", "Physics I", 4.0, "Dr. Michael Chen", "PHYS", "Tue 10:00-12:00"),
    (sem_map[(113, 1)], "MATH0120", "Calculus I", 3.0, "Dr. Wang Li", "MATH", "Wed 13:00-16:00"),
    (sem_map[(113, 2)], "CHEM0181", "Analytical Chemistry", 3.0, "Dr. Alice Chen", "CHEM", "Mon 13:00-16:00"),
    (sem_map[(113, 2)], "PHYS0230", "Physics II", 4.0, "Dr. James Liu", "PHYS", "Thu 10:00-12:00"),
]

for sem_id, crs_no, name, credits, teacher, dept, time in sample_courses:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO courses
            (semester_id, crs_no, name, credits, teacher, dept, day_codes, time_codes)
            VALUES (?, ?, ?, ?, ?, ?, '', ?)
        """, (sem_id, crs_no, name, credits, teacher, dept, time))
    except Exception as e:
        print(f"Error inserting {crs_no}: {e}")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM courses")
count = cursor.fetchone()[0]
print(f"Database seeded with {count} courses")

conn.close()
PYTHON_EOF

    python3 /tmp/seed_db.py "$DB_PATH"
    log_success "Demo data seeded"
    rm /tmp/seed_db.py
}

# Step 4: Start backend service
start_backend() {
    log_info "Step 4/6: Starting backend service..."

    mkdir -p "$LOG_DIR"

    cd "$BACKEND_DIR"

    # Activate virtual environment and start backend
    source "$VENV/bin/activate"

    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

    python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --timeout-keep-alive 5 \
        > "$LOG_DIR/backend.log" 2>&1 &

    BACKEND_PID=$!
    echo $BACKEND_PID > "$LOG_DIR/backend.pid"

    sleep 3

    # Verify backend is running
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "Backend started (PID: $BACKEND_PID)"
    else
        log_error "Backend failed to start!"
        tail -20 "$LOG_DIR/backend.log"
        return 1
    fi
}

# Step 5: Build and start frontend
start_frontend() {
    log_info "Step 5/6: Building and starting frontend..."

    cd "$FRONTEND_DIR"

    # Build frontend for production
    npm run build > "$LOG_DIR/frontend-build.log" 2>&1

    # Start frontend
    npm run start > "$LOG_DIR/frontend.log" 2>&1 &

    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"

    sleep 3

    # Verify frontend is running (port 3000 normally)
    if curl -s http://localhost:3000 > /dev/null; then
        log_success "Frontend started (PID: $FRONTEND_PID)"
    else
        log_error "Frontend may not be fully ready"
        tail -5 "$LOG_DIR/frontend.log"
    fi
}

# Step 6: Verify services
verify_services() {
    log_info "Step 6/6: Verifying services..."

    # Check backend
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        log_success "Backend health check: OK"
    else
        log_error "Backend health check failed"
        return 1
    fi

    # Check database
    COURSE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM courses;")
    log_success "Database contains $COURSE_COUNT courses"

    # Check ports
    log_info "Open ports:"
    ss -tuln | grep LISTEN | grep -E ":(80|443|8000|3000)" || true
}

# Main execution
main() {
    banner

    cd "$PROJECT_ROOT"

    # Execute steps
    kill_existing_processes || return 1
    init_database || return 1
    seed_demo_data || return 1
    start_backend || return 1
    start_frontend || return 1
    verify_services || return 1

    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                     ✅ DEPLOYMENT COMPLETE                                ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Services running:"
    echo "  • Backend API: http://localhost:8000 (0.0.0.0:8000)"
    echo "  • Frontend: http://localhost:3000"
    echo ""
    echo "Next steps:"
    echo "  1. Configure Nginx reverse proxy (port 80/443)"
    echo "  2. Setup SSL certificate (Let's Encrypt or Cloudflare)"
    echo "  3. Point DNS: nymu.com.tw → 31.41.34.19"
    echo "  4. Test: curl https://nymu.com.tw/api/health"
    echo ""
    echo "Logs:"
    echo "  • Backend: $LOG_DIR/backend.log"
    echo "  • Frontend: $LOG_DIR/frontend.log"
    echo ""
}

# Run main function
main "$@"
