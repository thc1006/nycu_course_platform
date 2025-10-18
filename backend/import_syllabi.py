#!/usr/bin/env python3
"""
Import course syllabi/outlines to database
從爬蟲結果導入課程綱要到資料庫
"""
import json
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/home/thc1006/dev/nycu_course_platform')

from backend.app.database.session import async_session, engine
from backend.app.models.course import Course
from backend.app.models.semester import Semester
from sqlalchemy import and_, select


async def import_syllabi():
    """Import course syllabi from scraper JSON to database"""

    try:
        # Initialize database tables
        print("🗄️ Initializing database tables...")
        from backend.app.database.session import init_db
        await init_db()
        print("✅ Database tables created/verified")

        # Load scraped outlines
        outlines_file = Path('/home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/outlines_all.json')

        if not outlines_file.exists():
            print("❌ Outlines file not found!")
            print(f"   Expected: {outlines_file}")
            return

        print(f"📂 Loading outlines from {outlines_file}...")
        with open(outlines_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_outlines = data.get('outlines', {})
        print(f"✅ Loaded {len(all_outlines)} semester(s) of outlines")

        # Import statistics
        updated = 0
        skipped = 0
        errors = 0

        # Process each semester
        async with async_session() as db:
            for semester_key, course_outlines in all_outlines.items():
                print(f"\n📚 Processing semester: {semester_key}")

                # Parse semester key (e.g., "110-1" -> acy=110, sem=1)
                try:
                    acy, sem = map(int, semester_key.split('-'))
                except ValueError:
                    print(f"  ⚠️  Invalid semester key: {semester_key}")
                    continue

                # Get semester record
                result = await db.execute(
                    select(Semester).where(
                        and_(Semester.acy == acy, Semester.sem == sem)
                    )
                )
                semester = result.scalars().first()

                if not semester:
                    print(f"  ⚠️  Semester {semester_key} not found in database, skipping")
                    continue

                print(f"  Processing {len(course_outlines)} courses...")

                # Batch update courses with syllabi
                for idx, (crs_no, outline_data) in enumerate(course_outlines.items()):
                    try:
                        # Find course
                        result = await db.execute(
                            select(Course).where(
                                and_(
                                    Course.semester_id == semester.id,
                                    Course.crs_no == str(crs_no)
                                )
                            )
                        )
                        course = result.scalars().first()

                        if course:
                            # Update with syllabi
                            course.syllabus = outline_data.get('en')
                            course.syllabus_zh = outline_data.get('zh_TW')
                            db.add(course)
                            updated += 1

                            if updated % 100 == 0:
                                print(f"    ✓ Updated {updated} courses so far...")
                        else:
                            skipped += 1

                    except Exception as e:
                        errors += 1
                        if errors <= 5:  # Print first 5 errors
                            print(f"    ✗ Error with course {crs_no}: {str(e)}")

                    # Commit every 200 records
                    if (idx + 1) % 200 == 0:
                        await db.commit()
                        print(f"    ✓ Committed batch")

                # Final commit for semester
                await db.commit()
                print(f"  ✅ Semester {semester_key} complete")

        print(f"\n✅ Syllabus import completed!")
        print(f"  - Updated: {updated}")
        print(f"  - Skipped: {skipped}")
        print(f"  - Errors: {errors}")
        print(f"  - Total processed: {updated + skipped}")

        # Verify a sample of courses have syllabi
        print("\n🔍 Verification: Checking sample courses with syllabi...")
        async with async_session() as db:
            result = await db.execute(
                select(Course).where(
                    Course.syllabus.isnot(None)
                ).limit(5)
            )
            sample_courses = result.scalars().all()
            if sample_courses:
                print(f"  ✅ Found {len(sample_courses)} courses with English syllabi (sample):")
                for course in sample_courses:
                    syllabus_preview = (course.syllabus[:50] + "...") if course.syllabus else None
                    print(f"    - {course.crs_no}: {syllabus_preview}")
            else:
                print("  ⚠️  No courses with syllabi found - scraper may not have collected data yet")

    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == '__main__':
    print("=" * 80)
    print("📖 NYCU Course Syllabus Import Tool")
    print("=" * 80)
    start_time = datetime.now()

    asyncio.run(import_syllabi())

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print("=" * 80)
