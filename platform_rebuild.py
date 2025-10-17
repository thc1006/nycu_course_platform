#!/usr/bin/env python3
"""
NYCU Course Platform - Complete System Rebuild & Data Integration
This script will:
1. Check current database status
2. Import scraper data into database
3. Verify data integrity
4. Generate production configuration
"""

import json
import sqlite3
import os
import sys
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "nycu_course_platform.db"
SCRAPER_DATA_DIR = PROJECT_ROOT / "scraper" / "data" / "real_courses_nycu"
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

def check_database_status():
    """Check current database status"""
    print("\n" + "="*80)
    print("📊 DATABASE STATUS CHECK")
    print("="*80)

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Check courses count
        cursor.execute("SELECT COUNT(*) FROM courses")
        courses_count = cursor.fetchone()[0]

        # Check semesters count
        cursor.execute("SELECT COUNT(*) FROM semesters")
        semesters_count = cursor.fetchone()[0]

        # Check sample data
        cursor.execute("SELECT crs_no, name, dept FROM courses LIMIT 3")
        sample_courses = cursor.fetchall()

        print(f"\n✓ Database file exists: {DB_PATH}")
        print(f"  • Total courses: {courses_count}")
        print(f"  • Total semesters: {semesters_count}")
        print(f"\n  Sample courses in database:")
        for crs_no, name, dept in sample_courses:
            print(f"    - [{dept}] {crs_no}: {name}")

        conn.close()
        return courses_count, semesters_count

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return 0, 0

def find_scraper_data_files():
    """Find all scraper data files"""
    print("\n" + "="*80)
    print("🔍 SCRAPER DATA FILES")
    print("="*80)

    data_files = []

    # Check real_courses_nycu directory
    if SCRAPER_DATA_DIR.exists():
        print(f"\n✓ Found scraper data directory: {SCRAPER_DATA_DIR}")
        for file in SCRAPER_DATA_DIR.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        data_files.append((file, len(data)))
                        print(f"  • {file.name}: {len(data)} records")
            except Exception as e:
                print(f"  ✗ {file.name}: Error reading - {e}")

    # Check parent scraper/data directory
    parent_data_dir = PROJECT_ROOT / "scraper" / "data"
    if parent_data_dir.exists():
        for file in parent_data_dir.glob("*.json"):
            if file.suffix == ".json":
                try:
                    with open(file) as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            data_files.append((file, len(data)))
                            print(f"  • {file.name}: {len(data)} records")
                except:
                    pass

    return data_files

def import_scraper_data():
    """Import scraper data into database"""
    print("\n" + "="*80)
    print("📥 DATA IMPORT")
    print("="*80)

    data_files = find_scraper_data_files()

    if not data_files:
        print("\n⚠️  No scraper data files found!")
        return False

    # Sort by file size (largest first)
    data_files.sort(key=lambda x: x[1], reverse=True)
    largest_file = data_files[0]

    print(f"\n📌 Using largest data file: {largest_file[0].name} ({largest_file[1]} courses)")

    try:
        with open(largest_file[0]) as f:
            courses_data = json.load(f)

        if not isinstance(courses_data, list):
            print("❌ Data format error: expected list of courses")
            return False

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Clear existing courses (keep semesters)
        cursor.execute("DELETE FROM courses")

        # Insert courses
        imported_count = 0
        for course in courses_data:
            try:
                cursor.execute("""
                    INSERT INTO courses
                    (acy, sem, crs_no, name, teacher, credits, dept, time, classroom, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    course.get('acy'),
                    course.get('sem'),
                    course.get('crs_no'),
                    course.get('name'),
                    course.get('teacher'),
                    course.get('credits'),
                    course.get('dept'),
                    course.get('time'),
                    course.get('classroom'),
                    course.get('details')
                ))
                imported_count += 1
            except Exception as e:
                print(f"  ⚠️  Error importing course {course.get('crs_no')}: {e}")

        conn.commit()

        # Verify import
        cursor.execute("SELECT COUNT(*) FROM courses")
        final_count = cursor.fetchone()[0]

        print(f"\n✅ Import successful!")
        print(f"  • Imported: {imported_count} courses")
        print(f"  • Total in database: {final_count}")

        # Show sample
        cursor.execute("SELECT crs_no, name, dept FROM courses LIMIT 5")
        samples = cursor.fetchall()
        print(f"\n  Sample imported courses:")
        for crs_no, name, dept in samples:
            print(f"    - [{dept}] {crs_no}: {name}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def generate_production_config():
    """Generate production configuration"""
    print("\n" + "="*80)
    print("⚙️  PRODUCTION CONFIGURATION")
    print("="*80)

    config = {
        "server": {
            "ip": "31.41.34.19",
            "domain": "nymu.com.tw",
            "ports": {
                "backend": 8000,
                "frontend": 3000,
                "nginx": [80, 443]
            }
        },
        "services": {
            "backend": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "environment": "production"
            },
            "frontend": {
                "port": 3000,
                "environment": "production"
            },
            "nginx": {
                "domain": "nymu.com.tw",
                "ssl": True,
                "http2": True
            }
        }
    }

    print("\n✓ Production config:")
    print(f"  • Server IP: {config['server']['ip']}")
    print(f"  • Domain: {config['server']['domain']}")
    print(f"  • Backend port: {config['services']['backend']['port']}")
    print(f"  • Frontend port: {config['services']['frontend']['port']}")
    print(f"  • Backend workers: {config['services']['backend']['workers']}")

    return config

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "NYCU COURSE PLATFORM - SYSTEM REBUILD & DATA INTEGRATION".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Step 1: Check database
    courses, semesters = check_database_status()

    # Step 2: Find scraper data
    data_files = find_scraper_data_files()

    if not data_files:
        print("\n❌ CRITICAL: No scraper data found!")
        return False

    # Step 3: Import data
    import_success = import_scraper_data()

    if not import_success:
        print("\n❌ Data import failed!")
        return False

    # Step 4: Generate config
    config = generate_production_config()

    print("\n" + "="*80)
    print("✅ SYSTEM REBUILD COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Start backend service: PYTHONPATH=. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4")
    print("  2. Start frontend service: npm run build && npm run start")
    print("  3. Configure Nginx with domain: nymu.com.tw")
    print("  4. Point DNS to: 31.41.34.19")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
