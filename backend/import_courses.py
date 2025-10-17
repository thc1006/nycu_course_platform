"""
Import courses data from scraper JSON to database (Async Version)
"""
import json
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/home/thc1006/dev/nycu_course_platform')

from backend.app.database.session import async_session, engine
from backend.app.models.course import Course
from backend.app.models.semester import Semester
from sqlalchemy import and_, select

async def import_courses():
    """Import courses from courses_all_semesters.json"""

    try:
        # Initialize database tables
        print("🗄️ Initializing database tables...")
        from backend.app.database.session import init_db
        await init_db()
        print("✅ Database tables created/verified")

        # Load data
        json_path = '/home/thc1006/dev/nycu_course_platform/scraper/data/real_courses_nycu/courses_all_semesters.json'

        print(f"📂 Loading JSON from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        courses = data.get('courses', [])
        print(f"✅ Loaded {len(courses)} courses")

        # Import statistics
        imported = 0
        updated = 0
        skipped = 0
        errors = 0

        # Process each course
        async with async_session() as db:
            for idx, course_data in enumerate(courses):
                try:
                    acy = course_data.get('acy')
                    sem = course_data.get('sem')
                    crs_no = course_data.get('crs_no')

                    # Find semester
                    result = await db.execute(
                        select(Semester).where(
                            and_(Semester.acy == acy, Semester.sem == sem)
                        )
                    )
                    semester = result.scalars().first()

                    if not semester:
                        skipped += 1
                        continue

                    # Check if course exists
                    result = await db.execute(
                        select(Course).where(
                            and_(
                                Course.semester_id == semester.id,
                                Course.crs_no == str(crs_no)
                            )
                        )
                    )
                    existing = result.scalars().first()

                    if existing:
                        # Update existing course
                        existing.name = course_data.get('name', '')
                        existing.teacher = course_data.get('teacher')
                        existing.credits = course_data.get('credits')
                        existing.dept = course_data.get('dept')
                        existing.day_codes = course_data.get('day_codes')
                        existing.time_codes = course_data.get('time_codes')
                        existing.classroom_codes = course_data.get('classroom_codes')
                        existing.details = json.dumps(course_data.get('details', {}))
                        db.add(existing)
                        updated += 1
                    else:
                        # Create new course
                        new_course = Course(
                            semester_id=semester.id,
                            crs_no=str(crs_no),
                            name=course_data.get('name', ''),
                            teacher=course_data.get('teacher'),
                            credits=course_data.get('credits'),
                            dept=course_data.get('dept'),
                            day_codes=course_data.get('day_codes'),
                            time_codes=course_data.get('time_codes'),
                            classroom_codes=course_data.get('classroom_codes'),
                            details=json.dumps(course_data.get('details', {})),
                        )
                        db.add(new_course)
                        imported += 1

                    # Commit every 100 records
                    if (idx + 1) % 100 == 0:
                        await db.commit()
                        print(f"  ✓ Processed {idx + 1}/{len(courses)}")

                except Exception as e:
                    errors += 1
                    if errors <= 5:  # Print first 5 errors
                        print(f"  ✗ Error with course {course_data.get('crs_no')}: {str(e)}")

            # Final commit
            await db.commit()

        print(f"\n✅ Import completed!")
        print(f"  - Imported (new): {imported}")
        print(f"  - Updated: {updated}")
        print(f"  - Skipped: {skipped}")
        print(f"  - Errors: {errors}")
        print(f"  - Total processed: {imported + updated + skipped}")

    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(import_courses())
