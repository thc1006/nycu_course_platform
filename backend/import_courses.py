#!/usr/bin/env python3
"""
Import all 70,266 NYCU courses from scraped JSON data to database
從爬蟲資料匯入 70,266 門交大課程到資料庫
"""
import json
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add backend to path
sys.path.insert(0, '/home/thc1006/dev/nycu_course_platform')

from backend.app.database.session import async_session, engine
from backend.app.models.course import Course
from backend.app.models.semester import Semester
from sqlalchemy import and_, select


async def import_courses():
    """Import all courses from scraped JSON to database"""

    try:
        # Initialize database tables
        print("🗄️  Initializing database tables...")
        from backend.app.database.session import init_db
        await init_db()
        print("✅ Database tables created/verified")

        # Load scraped courses
        courses_file = Path('/home/thc1006/dev/nycu_course_platform/data/real_courses_nycu/courses_all_semesters.json')

        if not courses_file.exists():
            print("❌ Courses file not found!")
            print(f"   Expected: {courses_file}")
            return

        print(f"📂 Loading courses from {courses_file}...")
        with open(courses_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_courses = data.get('courses', [])
        total_courses = len(all_courses)
        print(f"✅ Loaded {total_courses:,} courses")

        # Group courses by semester for efficient processing
        print("\n📊 Grouping courses by semester...")
        courses_by_semester = defaultdict(list)
        for course in all_courses:
            acy = course.get('acy')
            sem = course.get('sem')
            if acy and sem:
                semester_key = (acy, sem)
                courses_by_semester[semester_key].append(course)

        print(f"✅ Found {len(courses_by_semester)} unique semesters")

        # Import statistics
        imported = 0
        skipped = 0
        errors = 0
        semesters_created = 0

        async with async_session() as db:
            # Process each semester
            for idx, (semester_key, semester_courses) in enumerate(courses_by_semester.items(), 1):
                acy, sem = semester_key
                print(f"\n[{idx}/{len(courses_by_semester)}] 📚 Processing semester: {acy}-{sem}")
                print(f"    Courses in this semester: {len(semester_courses):,}")

                # Get or create semester record
                result = await db.execute(
                    select(Semester).where(
                        and_(Semester.acy == acy, Semester.sem == sem)
                    )
                )
                semester = result.scalars().first()

                if not semester:
                    print(f"    📝 Creating new semester: {acy}-{sem}")
                    semester = Semester(acy=acy, sem=sem)
                    db.add(semester)
                    await db.flush()  # Get the semester.id
                    semesters_created += 1
                    print(f"    ✅ Created semester ID: {semester.id}")
                else:
                    print(f"    ✓ Using existing semester ID: {semester.id}")

                # Batch insert courses for this semester
                batch_size = 500
                for batch_idx in range(0, len(semester_courses), batch_size):
                    batch = semester_courses[batch_idx:batch_idx + batch_size]

                    for course_data in batch:
                        try:
                            # Check if course already exists
                            crs_no = course_data.get('crs_no', '').strip()
                            if not crs_no:
                                skipped += 1
                                continue

                            result = await db.execute(
                                select(Course).where(
                                    and_(
                                        Course.semester_id == semester.id,
                                        Course.crs_no == crs_no
                                    )
                                )
                            )
                            existing = result.scalars().first()

                            if existing:
                                skipped += 1
                                continue

                            # Create new course record
                            course = Course(
                                semester_id=semester.id,
                                crs_no=crs_no,
                                name=course_data.get('name', '').strip(),
                                teacher=course_data.get('teacher', '').strip() or None,
                                credits=course_data.get('credits'),
                                dept=course_data.get('dept', '').strip() or None,
                                time_codes=course_data.get('time', '').strip() or None,
                                classroom_codes=course_data.get('classroom', '').strip() or None,
                                details=course_data.get('details')
                            )

                            db.add(course)
                            imported += 1

                        except Exception as e:
                            errors += 1
                            if errors <= 10:  # Print first 10 errors
                                print(f"      ✗ Error with course {course_data.get('crs_no', 'UNKNOWN')}: {str(e)}")

                    # Commit each batch
                    try:
                        await db.commit()
                        print(f"      ✓ Committed batch {batch_idx//batch_size + 1}/{(len(semester_courses)-1)//batch_size + 1} " +
                              f"(Imported: {imported:,}, Skipped: {skipped:,}, Errors: {errors})")
                    except Exception as e:
                        await db.rollback()
                        print(f"      ✗ Batch commit failed: {str(e)}")
                        errors += len(batch)

                print(f"    ✅ Semester {acy}-{sem} complete")

        print(f"\n{'='*80}")
        print(f"✅ Course import completed!")
        print(f"{'='*80}")
        print(f"  📊 Statistics:")
        print(f"     - Total in JSON: {total_courses:,}")
        print(f"     - Semesters created: {semesters_created}")
        print(f"     - Courses imported: {imported:,}")
        print(f"     - Courses skipped: {skipped:,}")
        print(f"     - Errors: {errors}")
        print(f"{'='*80}")

        # Verify import
        print("\n🔍 Verification: Checking database...")
        async with async_session() as db:
            # Count total courses
            from sqlalchemy import func
            result = await db.execute(select(func.count(Course.id)))
            total_in_db = result.scalar()
            print(f"  ✅ Total courses in database: {total_in_db:,}")

            # Count semesters
            result = await db.execute(select(func.count(Semester.id)))
            semesters_in_db = result.scalar()
            print(f"  ✅ Total semesters in database: {semesters_in_db}")

            # Sample courses from each semester
            result = await db.execute(
                select(Semester).order_by(Semester.acy.desc(), Semester.sem.desc()).limit(3)
            )
            recent_semesters = result.scalars().all()

            print(f"\n  📚 Sample courses from recent semesters:")
            for semester in recent_semesters:
                result = await db.execute(
                    select(Course).where(Course.semester_id == semester.id).limit(3)
                )
                courses = result.scalars().all()
                print(f"\n    {semester.acy}-{semester.sem}:")
                for course in courses:
                    print(f"      • {course.crs_no}: {course.name} ({course.teacher}) - {course.credits}學分")

    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == '__main__':
    print("=" * 80)
    print("🎓 NYCU Course Import Tool - 70,266 Courses")
    print("=" * 80)
    start_time = datetime.now()

    asyncio.run(import_courses())

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print("=" * 80)
