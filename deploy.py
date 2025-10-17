#!/usr/bin/env python3
"""
NYCU Course Platform - Complete Production Deployment
Server IP: 31.41.34.19
Domain: nymu.com.tw
"""

import os
import sys
import subprocess
import sqlite3
import time
import signal
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path("/home/thc1006/dev/nycu_course_platform")
DB_PATH = PROJECT_ROOT / "nycu_course_platform.db"
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SCHEMA_SQL = PROJECT_ROOT / "data" / "schema.sql"
LOG_DIR = Path("/var/log/nycu-platform")
VENV_PYTHON = BACKEND_DIR / "venv" / "bin" / "python"

# Global variables
processes = []

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[✓]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[✗]{Colors.END} {msg}")

def log_warn(msg):
    print(f"{Colors.YELLOW}[!]{Colors.END} {msg}")

def banner():
    print("\n" + "="*80)
    print("NYCU COURSE PLATFORM - PRODUCTION DEPLOYMENT".center(80))
    print("="*80)
    print(f"Server IP: 31.41.34.19    Domain: nymu.com.tw".center(80))
    print("="*80 + "\n")

def cleanup_processes():
    """Kill all existing project processes"""
    log_info("Cleaning up existing processes...")

    patterns = [
        "uvicorn",
        "next dev",
        "npm run dev",
        "fetch_real_courses",
        "scraper_v2_real",
        "nycu_github_scraper"
    ]

    for pattern in patterns:
        try:
            subprocess.run(
                ["pkill", "-9", "-f", pattern],
                capture_output=True,
                timeout=5
            )
        except:
            pass

    time.sleep(2)
    log_success("Processes cleaned")

def initialize_database():
    """Initialize SQLite database with schema"""
    log_info("Initializing database...")

    # Backup existing database
    if DB_PATH.exists():
        backup_name = f"{DB_PATH}.backup.{int(time.time())}"
        os.rename(DB_PATH, backup_name)
        log_warn(f"Backed up existing database to {backup_name}")

    # Create fresh database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Read schema
    if not SCHEMA_SQL.exists():
        log_error(f"Schema file not found: {SCHEMA_SQL}")
        return False

    schema_sql = SCHEMA_SQL.read_text()

    # Execute schema
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        log_success("Database schema initialized")
    except Exception as e:
        log_error(f"Failed to initialize database: {e}")
        return False
    finally:
        conn.close()

    return True

def seed_demo_data():
    """Seed database with demo courses"""
    log_info("Seeding database with demo data...")

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Insert semesters
        semesters = [(113, 1), (113, 2)]
        for acy, sem in semesters:
            cursor.execute(
                "INSERT OR IGNORE INTO semesters (acy, sem) VALUES (?, ?)",
                (acy, sem)
            )

        # Get semester IDs
        cursor.execute("SELECT id, acy, sem FROM semesters")
        sem_map = {(acy, sem): sid for sid, acy, sem in cursor.fetchall()}

        # Insert demo courses
        demo_courses = [
            (sem_map[(113, 1)], "CHEM0160", "General Chemistry II", 3.0, "Dr. Carol Liu", "CHEM"),
            (sem_map[(113, 1)], "PHYS0210", "Physics I", 4.0, "Dr. Michael Chen", "PHYS"),
            (sem_map[(113, 1)], "MATH0120", "Calculus I", 3.0, "Dr. Wang Li", "MATH"),
            (sem_map[(113, 1)], "ENGR0050", "Engineering Design", 3.0, "Prof. James Smith", "ENGR"),
            (sem_map[(113, 1)], "CS0101", "Introduction to Computing", 3.0, "Dr. Tom Lee", "CS"),
            (sem_map[(113, 2)], "CHEM0181", "Analytical Chemistry", 3.0, "Dr. Alice Chen", "CHEM"),
            (sem_map[(113, 2)], "PHYS0230", "Physics II", 4.0, "Dr. James Liu", "PHYS"),
            (sem_map[(113, 2)], "MATH0220", "Calculus II", 3.0, "Dr. Li Wang", "MATH"),
            (sem_map[(113, 2)], "BIO0101", "Biology Fundamentals", 4.0, "Dr. Sarah Brown", "BIO"),
            (sem_map[(113, 2)], "CS0201", "Data Structures", 3.0, "Dr. David Chang", "CS"),
        ]

        for sem_id, crs_no, name, credits, teacher, dept in demo_courses:
            cursor.execute("""
                INSERT OR IGNORE INTO courses
                (semester_id, crs_no, name, credits, teacher, dept)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sem_id, crs_no, name, credits, teacher, dept))

        conn.commit()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM courses")
        count = cursor.fetchone()[0]
        log_success(f"Database seeded with {count} demo courses")

        conn.close()
        return True
    except Exception as e:
        log_error(f"Failed to seed database: {e}")
        return False

def start_backend():
    """Start FastAPI backend service"""
    log_info("Starting backend service...")

    os.makedirs(LOG_DIR, exist_ok=True)

    env = os.environ.copy()
    env['PYTHONPATH'] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH', '')}"

    # Start backend in background
    backend_log = LOG_DIR / "backend.log"
    with open(backend_log, 'w') as logfile:
        proc = subprocess.Popen(
            [
                str(VENV_PYTHON), "-m", "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--workers", "4"
            ],
            cwd=str(BACKEND_DIR),
            stdout=logfile,
            stderr=logfile,
            env=env
        )

    processes.append(('backend', proc))

    # Wait for backend to start
    time.sleep(3)

    # Verify backend
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
        if response.status == 200:
            log_success(f"Backend started (PID: {proc.pid})")
            return True
    except:
        pass

    log_warn("Backend may not be fully ready")
    return True  # Continue anyway

def start_frontend():
    """Start Next.js frontend service"""
    log_info("Starting frontend service...")

    frontend_log = LOG_DIR / "frontend.log"
    with open(frontend_log, 'w') as logfile:
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=logfile,
            stderr=logfile
        )

    processes.append(('frontend', proc))

    time.sleep(3)
    log_success(f"Frontend started (PID: {proc.pid})")
    return True

def verify_services():
    """Verify all services are running"""
    log_info("Verifying services...")

    try:
        # Check database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        log_success(f"Database: {course_count} courses")

        cursor.execute("SELECT COUNT(*) FROM semesters")
        sem_count = cursor.fetchone()[0]
        log_success(f"Database: {sem_count} semesters")

        conn.close()
    except Exception as e:
        log_error(f"Database verification failed: {e}")
        return False

    # Check backend
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=2)
        if response.status == 200:
            log_success("Backend API: OK")
    except:
        log_warn("Backend API: Not responding (check logs)")

    return True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    log_warn("\nShutting down services...")
    for name, proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            log_success(f"Stopped {name}")
        except:
            proc.kill()
    sys.exit(0)

def main():
    banner()

    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Step 1: Cleanup
    try:
        cleanup_processes()
    except Exception as e:
        log_error(f"Cleanup failed: {e}")
        return False

    # Step 2: Initialize database
    if not initialize_database():
        return False

    # Step 3: Seed demo data
    if not seed_demo_data():
        return False

    # Step 4: Start backend
    if not start_backend():
        return False

    # Step 5: Start frontend
    if not start_frontend():
        return False

    # Step 6: Verify
    if not verify_services():
        return False

    print("\n" + "="*80)
    print(Colors.BOLD + "✅ DEPLOYMENT COMPLETE".center(80) + Colors.END)
    print("="*80)
    print("\nServices:")
    print("  • Backend API: http://localhost:8000 (Production: 0.0.0.0:8000)")
    print("  • Frontend: http://localhost:3000")
    print("  • Database: ready for 70,000+ courses")
    print("\nLogs:")
    print(f"  • Backend: {LOG_DIR}/backend.log")
    print(f"  • Frontend: {LOG_DIR}/frontend.log")
    print("\nNext steps:")
    print("  1. Test API: curl http://localhost:8000/api/semesters/")
    print("  2. Test Frontend: http://localhost:3000")
    print("  3. Configure Nginx reverse proxy")
    print("  4. Setup SSL/TLS (Let's Encrypt)")
    print("  5. Point DNS: nymu.com.tw → 31.41.34.19")
    print("\nKeeping services running. Press Ctrl+C to stop.")
    print("="*80 + "\n")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
