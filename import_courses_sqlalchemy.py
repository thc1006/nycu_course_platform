#!/usr/bin/env python3
"""
NYCU Course Platform - SQLAlchemy-based Course Data Importer
Imports 70,000+ courses using proper SQLAlchemy models and schema
"""

import json
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, '/home/thc1006/dev/nycu_course_platform')

from backend.app.database.session import async_session, init_db, engine
from backend.app.models.course import Course
from backend.app.models.semester import Semester
from sqlalchemy import select

DATA_FILE = Path("/home/thc1006/dev/nycu_course_platform/data/real_courses_nycu/courses_all_semesters.json")
BATCH_SIZE = 500

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

async def import_courses():
    """Import courses using SQLAlchemy"""

    try:
        # Step 1: Initialize database with proper schema
        log_info("Initializing database with SQLAlchemy schema...")
        await init_db()
        log_success("Database schema created")

        # Step 2: Load course data
        log_info(f"Loading course data from: {DATA_FILE}")
        if not DATA_FILE.exists():
            log_error(f"Data file not found: {DATA_FILE}")
            return False

        with open(DATA_FILE) as f:
            data = json.load(f)

        courses_data = data.get('courses', [])
        total_courses = len(courses_data)
        log_success(f"Loaded {total_courses} courses from JSON")

        # Step 3: Create semester map
        log_info("Creating semesters...")
        semester_map = {}

        # Get unique semesters
        semesters_set = set()
        for course in courses_data:
            acy = course.get('acy')
            sem = course.get('sem')
            if acy and sem:
                semesters_set.add((acy, sem))

        async with async_session() as db:
            for acy, sem in sorted(semesters_set):
                # Check if semester exists
                result = await db.execute(
                    select(Semester).where(
                        (Semester.acy == acy) & (Semester.sem == sem)
                    )
                )
                semester = result.scalars().first()

                if not semester:
                    semester = Semester(acy=acy, sem=sem)
                    db.add(semester)
                    await db.flush()

                semester_map[(acy, sem)] = semester.id
                print(f"  {Colors.BLUE}•{Colors.END} Semester {acy}-{sem}: ID {semester.id}")

            await db.commit()

        log_success(f"Created {len(semester_map)} semesters")

        # Step 4: Import courses in batches
        log_info(f"Importing {total_courses} courses in batches of {BATCH_SIZE}...")

        imported = 0
        skipped = 0
        errors = []

        for i in range(0, total_courses, BATCH_SIZE):
            batch = courses_data[i:i+BATCH_SIZE]

            async with async_session() as db:
                for course_data in batch:
                    try:
                        acy = course_data.get('acy')
                        sem = course_data.get('sem')
                        semester_id = semester_map.get((acy, sem))

                        if not semester_id:
                            skipped += 1
                            continue

                        # Create course instance
                        course = Course(
                            semester_id=semester_id,
                            crs_no=course_data.get('crs_no', ''),
                            name=course_data.get('name', ''),
                            credits=course_data.get('credits'),
                            teacher=course_data.get('teacher'),
                            dept=course_data.get('dept'),
                            day_codes='',  # Not in NYCU data
                            time_codes=course_data.get('time', ''),
                            classroom_codes=course_data.get('classroom', ''),
                            details=course_data.get('details', ''),
                            syllabus=None,  # Will be populated later by import_syllabi.py
                            syllabus_zh=None,  # Will be populated later
                        )

                        db.add(course)
                        imported += 1

                    except Exception as e:
                        skipped += 1
                        if len(errors) < 5:
                            errors.append(str(e))

                await db.commit()

            # Progress indicator
            progress = min(i + BATCH_SIZE, total_courses)
            percent = (progress / total_courses) * 100
            print(f"  {Colors.BLUE}Progress:{Colors.END} {progress}/{total_courses} ({percent:.1f}%)")

        log_success(f"Import complete: {imported} imported, {skipped} skipped")

        if errors:
            log_error(f"Sample errors: {errors[:3]}")

        # Step 5: Verify import
        log_info("Verifying imported data...")

        async with async_session() as db:
            # Count semesters
            result = await db.execute(select(Semester))
            sem_count = len(result.scalars().all())

            # Count courses
            result = await db.execute(select(Course))
            course_count = len(result.scalars().all())

            # Get breakdown by semester
            result = await db.execute(
                select(Semester).order_by(Semester.acy.desc(), Semester.sem.desc())
            )
            semesters = result.scalars().all()

            print(f"\n{Colors.BOLD}Import Summary:{Colors.END}")
            print(f"  {Colors.GREEN}✓{Colors.END} Total semesters: {sem_count}")
            print(f"  {Colors.GREEN}✓{Colors.END} Total courses: {course_count}")
            print(f"\n{Colors.BOLD}Semester Breakdown:{Colors.END}")

            for semester in semesters:
                result = await db.execute(
                    select(Course).where(Course.semester_id == semester.id)
                )
                count = len(result.scalars().all())
                print(f"  {Colors.BLUE}•{Colors.END} {semester.acy}-{semester.sem}: {count} courses")

        return course_count > 0

    except Exception as e:
        log_error(f"Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


async def main():
    print("\n" + "=" * 80)
    print("NYCU COURSE PLATFORM - SQLALCHEMY COURSE IMPORTER".center(80))
    print("=" * 80 + "\n")

    start_time = datetime.now()

    success = await import_courses()

    elapsed = (datetime.now() - start_time).total_seconds()

    if success:
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}✅ IMPORT COMPLETE{Colors.END}".center(90))
        print("=" * 80)
        print(f"\n⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print("\n🌐 Platform ready! Restart Docker backend to use new data.")
    else:
        print("\n" + "=" * 80)
        print(f"{Colors.RED}❌ IMPORT FAILED{Colors.END}".center(90))
        print("=" * 80)

    return success


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
