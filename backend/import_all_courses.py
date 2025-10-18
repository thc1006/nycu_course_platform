#!/usr/bin/env python3
"""
FIXED Import Script - Handles nested raw data structure
修正版匯入腳本 - 處理嵌套的原始資料結構

Imports ALL courses from raw_data_all_semesters.json
從 raw_data_all_semesters.json 匯入所有課程
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


def flatten_raw_courses(raw_data):
    """
    Flatten the nested raw data structure into a flat list of courses

    Structure:
    {
        "114-1": {
            "dept_uuid_1": {
                "dep_id": "uuid",
                "dep_cname": "系所名稱",
                "1": {
                    "1141_course_id_1": {
                        "acy": "114",
                        "sem": "1",
                        "cos_id": "...",
                        ...
                    },
                    "1141_course_id_2": {...},
                    ...
                },
                "2": { another group },
                ...
            },
            "dept_uuid_2": {...},
            ...
        },
        "113-2": {...},
        ...
    }
    """
    all_courses = []
    total_depts = 0

    print("\n📊 Analyzing raw data structure...")

    for semester_key, semester_data in raw_data.items():
        if not isinstance(semester_data, dict):
            continue

        acy, sem = semester_key.split('-')
        print(f"\n  📚 Semester: {semester_key}")
        print(f"     Departments: {len(semester_data)}")

        semester_course_count = 0

        for dept_uuid, dept_wrapper in semester_data.items():
            if not isinstance(dept_wrapper, dict):
                continue

            # Handle extra UUID nesting level
            if dept_uuid in dept_wrapper:
                dept_data = dept_wrapper[dept_uuid]
            else:
                dept_data = dept_wrapper

            if not isinstance(dept_data, dict):
                continue

            total_depts += 1
            dept_name = dept_data.get('dep_cname', 'Unknown')

            # Iterate through all inner keys (could be "1", "2", "3", etc.)
            for inner_key, inner_data in dept_data.items():
                # Skip metadata fields
                if inner_key in ['dep_id', 'dep_cname', 'dep_ename']:
                    continue

                if not isinstance(inner_data, dict):
                    continue

                # Now we're at the course group level
                for course_key, course_data in inner_data.items():
                    if not isinstance(course_data, dict):
                        continue

                    # Extract course information with proper None handling
                    # Use cos_id as identifier (all courses have it)
                    # Use cos_code if available, otherwise use cos_id
                    cos_code = course_data.get('cos_code') or ''
                    cos_id = course_data.get('cos_id') or ''
                    crs_no = cos_code if cos_code else cos_id

                    # Handle None values properly - use (x or '') pattern
                    course = {
                        'acy': course_data.get('acy', acy),
                        'sem': course_data.get('sem', sem),
                        'crs_no': (crs_no or '').strip(),
                        'cos_id': (cos_id or '').strip(),
                        'name': (course_data.get('cos_cname') or '').strip(),
                        'credits': float(course_data.get('cos_credit', 0)) if course_data.get('cos_credit') else None,
                        'teacher': (course_data.get('teacher') or '').strip(),
                        'dept': dept_name,
                        'time': (course_data.get('cos_time') or '').strip(),
                        'classroom': None,  # Parse from cos_time if needed
                        'details': json.dumps(course_data, ensure_ascii=False)
                    }

                    all_courses.append(course)
                    semester_course_count += 1

        print(f"     Total courses: {semester_course_count:,}")

    print(f"\n  ✅ Total departments processed: {total_depts}")
    print(f"  ✅ Total courses extracted: {len(all_courses):,}")

    return all_courses


async def import_courses():
    """Import all courses from raw JSON to database"""

    try:
        # Initialize database tables
        print("🗄️  Initializing database tables...")
        from backend.app.database.session import init_db
        await init_db()
        print("✅ Database tables created/verified")

        # Load RAW scraped data
        raw_file = Path('/home/thc1006/dev/nycu_course_platform/scraper/data/real_courses_nycu/raw_data_all_semesters.json')

        if not raw_file.exists():
            print(f"❌ Raw data file not found: {raw_file}")
            return

        print(f"\n📂 Loading raw data from {raw_file.name}...")
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        print(f"✅ Loaded raw data with {len(raw_data)} semesters")

        # Flatten the nested structure
        print("\n🔄 Flattening nested course data...")
        all_courses = flatten_raw_courses(raw_data)
        total_courses = len(all_courses)
        print(f"✅ Flattened to {total_courses:,} courses")

        # Group courses by semester
        print("\n📊 Grouping courses by semester...")
        courses_by_semester = defaultdict(list)
        for course in all_courses:
            acy = course.get('acy')
            sem = course.get('sem')
            if acy and sem:
                semester_key = (str(acy), str(sem))
                courses_by_semester[semester_key].append(course)

        print(f"✅ Found {len(courses_by_semester)} unique semesters")

        # Import statistics
        imported = 0
        skipped = 0
        errors = 0
        semesters_created = 0

        async with async_session() as db:
            # Clear existing courses first (optional - remove if you want to keep existing)
            from sqlalchemy import text
            print("\n⚠️  Clearing existing courses...")
            await db.execute(text("DELETE FROM courses"))
            await db.execute(text("DELETE FROM semester"))
            await db.commit()
            print("✅ Database cleared")

            # Process each semester
            for idx, (semester_key, semester_courses) in enumerate(sorted(courses_by_semester.items()), 1):
                acy, sem = semester_key
                print(f"\n[{idx}/{len(courses_by_semester)}] 📚 Processing semester: {acy}-{sem}")
                print(f"    Courses in this semester: {len(semester_courses):,}")

                # Create semester record
                print(f"    📝 Creating semester: {acy}-{sem}")
                semester = Semester(acy=int(acy), sem=int(sem))
                db.add(semester)
                await db.flush()  # Get the semester.id
                semesters_created += 1
                print(f"    ✅ Created semester ID: {semester.id}")

                # Batch insert courses for this semester
                batch_size = 1000
                for batch_idx in range(0, len(semester_courses), batch_size):
                    batch = semester_courses[batch_idx:batch_idx + batch_size]

                    for course_data in batch:
                        try:
                            # Get course identifier - crs_no should always have value (cos_code or cos_id)
                            crs_no = (course_data.get('crs_no') or '').strip()
                            name = (course_data.get('name') or '').strip()

                            # Skip if both identifier and name are missing
                            if not crs_no and not name:
                                skipped += 1
                                continue

                            # Create new course record with proper None handling
                            course = Course(
                                semester_id=semester.id,
                                crs_no=crs_no or None,
                                name=name or None,
                                teacher=(course_data.get('teacher') or '').strip() or None,
                                credits=course_data.get('credits'),
                                dept=(course_data.get('dept') or '').strip() or None,
                                time_codes=(course_data.get('time') or '').strip() or None,
                                classroom_codes=(course_data.get('classroom') or '').strip() or None,
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
                        print(f"      ✓ Batch {batch_idx//batch_size + 1}/{(len(semester_courses)-1)//batch_size + 1} " +
                              f"(Imported: {imported:,}, Skipped: {skipped}, Errors: {errors})")
                    except Exception as e:
                        await db.rollback()
                        print(f"      ✗ Batch commit failed: {str(e)}")
                        errors += len(batch)

                print(f"    ✅ Semester {acy}-{sem} complete")

        print(f"\n{'='*80}")
        print(f"✅ Course import completed!")
        print(f"{'='*80}")
        print(f"  📊 Statistics:")
        print(f"     - Total in raw data: {total_courses:,}")
        print(f"     - Semesters created: {semesters_created}")
        print(f"     - Courses imported: {imported:,}")
        print(f"     - Courses skipped: {skipped:,}")
        print(f"     - Errors: {errors}")
        print(f"  📈 Success rate: {(imported/total_courses*100):.1f}%")
        print(f"{'='*80}")

        # Verification
        print("\n🔍 Verification: Checking database...")
        async with async_session() as db:
            from sqlalchemy import func

            # Total courses
            result = await db.execute(select(func.count(Course.id)))
            total_in_db = result.scalar()
            print(f"  ✅ Total courses in database: {total_in_db:,}")

            # Total semesters
            result = await db.execute(select(func.count(Semester.id)))
            semesters_in_db = result.scalar()
            print(f"  ✅ Total semesters in database: {semesters_in_db}")

            # Courses per semester
            print(f"\n  📚 Courses per semester:")
            result = await db.execute(
                select(Semester).order_by(Semester.acy.desc(), Semester.sem.desc())
            )
            all_semesters = result.scalars().all()

            for semester in all_semesters:
                result = await db.execute(
                    select(func.count(Course.id)).where(Course.semester_id == semester.id)
                )
                count = result.scalar()
                print(f"    {semester.acy}-{semester.sem}: {count:,} courses")

    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == '__main__':
    print("=" * 80)
    print("🎓 NYCU Complete Course Import - Raw Data Parser")
    print("=" * 80)
    start_time = datetime.now()

    asyncio.run(import_courses())

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print("=" * 80)
