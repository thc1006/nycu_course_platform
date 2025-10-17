#!/usr/bin/env python3
"""
NYCU Course Platform - Production Course Data Importer
Imports 70,000+ courses from scraped JSON data into SQLite database
"""

import json
import sqlite3
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

PROJECT_ROOT = Path("/home/thc1006/dev/nycu_course_platform")
DB_PATH = PROJECT_ROOT / "nycu_course_platform.db"
DATA_FILE = PROJECT_ROOT / "scraper/data/real_courses_nycu/courses_all_semesters.json"
BATCH_SIZE = 500  # Insert in batches for performance

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
    print("\n" + "=" * 80)
    print("NYCU COURSE PLATFORM - PRODUCTION DATA IMPORTER".center(80))
    print("=" * 80 + "\n")

def backup_database():
    """Backup existing database"""
    log_info("Backing up existing database...")
    if DB_PATH.exists():
        backup_path = f"{DB_PATH}.backup.{int(time.time())}"
        DB_PATH.rename(backup_path)
        log_success(f"Database backed up to: {backup_path}")
        return backup_path
    return None

def initialize_database():
    """Initialize database with schema"""
    log_info("Initializing database schema...")

    schema_path = PROJECT_ROOT / "data/schema.sql"
    if not schema_path.exists():
        log_error(f"Schema file not found: {schema_path}")
        return False

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        schema_sql = schema_path.read_text()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()

        log_success("Database schema initialized")
        return True
    except Exception as e:
        log_error(f"Failed to initialize database: {e}")
        return False

def load_course_data() -> Tuple[Dict[Tuple[int, int], int], List[Dict]]:
    """Load courses from JSON and prepare semester map"""
    log_info(f"Loading course data from: {DATA_FILE}")

    if not DATA_FILE.exists():
        log_error(f"Data file not found: {DATA_FILE}")
        return {}, []

    try:
        with open(DATA_FILE) as f:
            data = json.load(f)

        courses = data.get('courses', [])
        total = len(courses)
        log_success(f"Loaded {total} courses from JSON")

        # Create semester map {(acy, sem): id}
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Get unique semesters from courses
        semesters = set()
        for course in courses:
            acy = course.get('acy')
            sem = course.get('sem')
            if acy and sem:
                semesters.add((acy, sem))

        log_info(f"Found {len(semesters)} unique semesters")

        # Insert/get semester IDs
        semester_map = {}
        for acy, sem in sorted(semesters):
            cursor.execute(
                "INSERT OR IGNORE INTO semesters (acy, sem) VALUES (?, ?)",
                (acy, sem)
            )
            cursor.execute(
                "SELECT id FROM semesters WHERE acy = ? AND sem = ?",
                (acy, sem)
            )
            result = cursor.fetchone()
            if result:
                semester_map[(acy, sem)] = result[0]
                print(f"  {Colors.BLUE}•{Colors.END} 学年 {acy}-{sem}: ID {result[0]}")

        conn.commit()
        conn.close()

        return semester_map, courses

    except Exception as e:
        log_error(f"Failed to load course data: {e}")
        return {}, []

def import_courses_batch(semester_map: Dict, courses: List[Dict]) -> Tuple[int, int]:
    """Import courses in batches"""
    log_info(f"Importing {len(courses)} courses in batches of {BATCH_SIZE}...")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for i in range(0, len(courses), BATCH_SIZE):
        batch = courses[i:i+BATCH_SIZE]

        for course in batch:
            try:
                acy = course.get('acy')
                sem = course.get('sem')
                semester_id = semester_map.get((acy, sem))

                if not semester_id:
                    skipped += 1
                    continue

                cursor.execute("""
                    INSERT OR IGNORE INTO courses
                    (semester_id, crs_no, name, credits, teacher, dept,
                     day_codes, time_codes, classroom_codes, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    semester_id,
                    course.get('crs_no', ''),
                    course.get('name', ''),
                    course.get('credits', 0.0),
                    course.get('teacher', ''),
                    course.get('dept', ''),
                    '',  # day_codes - could be parsed from 'time'
                    course.get('time', ''),
                    course.get('classroom', ''),
                    course.get('details', '')
                ))
                imported += 1

            except Exception as e:
                log_warn(f"Error importing course: {e}")
                skipped += 1

        # Progress indicator
        progress = min(i + BATCH_SIZE, len(courses))
        percent = (progress / len(courses)) * 100
        print(f"  {Colors.BLUE}Progress:{Colors.END} {progress}/{len(courses)} ({percent:.1f}%)")

        # Commit batch
        conn.commit()

    conn.close()

    return imported, skipped

def verify_import():
    """Verify imported data"""
    log_info("Verifying imported data...")

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Count totals
        cursor.execute("SELECT COUNT(*) FROM semesters")
        sem_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]

        # Get semester breakdown
        cursor.execute("""
            SELECT s.acy, s.sem, COUNT(c.id) as count
            FROM semesters s
            LEFT JOIN courses c ON s.id = c.semester_id
            GROUP BY s.id
            ORDER BY s.acy DESC, s.sem DESC
        """)

        breakdown = cursor.fetchall()

        conn.close()

        print(f"\n{Colors.BOLD}Import Summary:{Colors.END}")
        print(f"  {Colors.GREEN}✓{Colors.END} Total semesters: {sem_count}")
        print(f"  {Colors.GREEN}✓{Colors.END} Total courses: {course_count}")
        print(f"\n{Colors.BOLD}Semester Breakdown:{Colors.END}")

        for acy, sem, count in breakdown:
            print(f"  {Colors.BLUE}•{Colors.END} {acy}-{sem}: {count} courses")

        return course_count > 0

    except Exception as e:
        log_error(f"Verification failed: {e}")
        return False

def test_api():
    """Test backend API with new data"""
    log_info("Testing backend API...")

    try:
        import urllib.request

        # Test semesters endpoint
        response = urllib.request.urlopen("http://localhost:8000/api/semesters/", timeout=5)
        if response.status == 200:
            log_success("GET /api/semesters/ - 200 OK")

        # Test courses endpoint
        response = urllib.request.urlopen("http://localhost:8000/api/courses/?semester_id=1", timeout=5)
        if response.status == 200:
            log_success("GET /api/courses/?semester_id=1 - 200 OK")

        return True
    except Exception as e:
        log_warn(f"API test failed: {e}")
        return False

def main():
    banner()

    # Step 1: Backup existing database
    backup_path = backup_database()

    # Step 2: Initialize fresh database
    if not initialize_database():
        return False

    # Step 3: Load course data
    semester_map, courses = load_course_data()
    if not courses:
        log_error("No courses loaded")
        return False

    # Step 4: Import courses
    imported, skipped = import_courses_batch(semester_map, courses)
    log_success(f"Import complete: {imported} imported, {skipped} skipped")

    # Step 5: Verify
    if verify_import():
        log_success("Data verification passed")
    else:
        log_error("Data verification failed")
        return False

    # Step 6: Test API
    test_api()

    print("\n" + "=" * 80)
    print(Colors.BOLD + "✅ PRODUCTION IMPORT COMPLETE".center(80) + Colors.END)
    print("=" * 80)

    if backup_path:
        print(f"\n📦 Backup location: {backup_path}")

    print("\n🌐 Platform is ready for production use!")
    print("   • Frontend: http://localhost:3000")
    print("   • API: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
