#!/usr/bin/env python3
"""
Migrate time/classroom data from details JSON to dedicated fields
從 details JSON 中提取時間/教室資料到專用欄位
"""
import json
import sys
import asyncio
import re
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/home/thc1006/dev/nycu_course_platform')

from backend.app.database.session import async_session, engine, init_db
from backend.app.models.course import Course
from backend.app.models.semester import Semester  # Import Semester to fix relationship
from sqlalchemy import select


def parse_time_classroom(time_classroom_str: str) -> tuple[str, str]:
    """
    Parse time_classroom string to extract time and classroom

    Format examples:
    - "M34-" -> time: "星期一 3-4節", classroom: ""
    - "T56ED203" -> time: "星期二 5-6節", classroom: "ED203"
    - "W56R8-" -> time: "星期三 5-6節, 星期四 8節", classroom: ""
    - "F78EC022" -> time: "星期五 7-8節", classroom: "EC022"
    """
    if not time_classroom_str or time_classroom_str == "-":
        return "", ""

    # Day code mapping (NYCU uses MTWRF for weekdays)
    day_map = {
        'M': '星期一',
        'T': '星期二',
        'W': '星期三',
        'R': '星期四',
        'F': '星期五',
        'S': '星期六',
        'U': '星期日'
    }

    # Extract classroom (usually at the end, starts with letter or number)
    # Pattern: ends with building code + room number (e.g., ED203, EC022)
    classroom_match = re.search(r'([A-Z]{2}\d{3,4})$', time_classroom_str)
    classroom = classroom_match.group(1) if classroom_match else ""

    # Remove classroom part to get time part
    time_part = time_classroom_str
    if classroom:
        time_part = time_classroom_str[:-len(classroom)]

    # Remove trailing dash
    time_part = time_part.rstrip('-')

    if not time_part:
        return "", classroom

    # Parse time codes (e.g., "M34" = Monday periods 3-4, "W56R8" = Wed 5-6, Thu 8)
    time_segments = []
    current_day = None
    current_periods = []

    for char in time_part:
        if char in day_map:
            # Save previous day if exists
            if current_day and current_periods:
                periods_str = format_periods(current_periods)
                time_segments.append(f"{day_map[current_day]} {periods_str}")
            # Start new day
            current_day = char
            current_periods = []
        elif char.isdigit():
            if current_day:
                current_periods.append(char)

    # Add last day
    if current_day and current_periods:
        periods_str = format_periods(current_periods)
        time_segments.append(f"{day_map[current_day]} {periods_str}")

    time_str = ", ".join(time_segments) if time_segments else time_part

    return time_str, classroom


def format_periods(periods: list[str]) -> str:
    """Format period numbers into readable string"""
    if not periods:
        return ""

    # Convert to sorted integers
    sorted_periods = sorted([int(p) for p in periods])

    # Group consecutive periods
    groups = []
    start = sorted_periods[0]
    end = sorted_periods[0]

    for period in sorted_periods[1:]:
        if period == end + 1:
            end = period
        else:
            if start == end:
                groups.append(f"{start}節")
            else:
                groups.append(f"{start}-{end}節")
            start = period
            end = period

    # Add last group
    if start == end:
        groups.append(f"{start}節")
    else:
        groups.append(f"{start}-{end}節")

    return ", ".join(groups)


async def migrate_time_classroom():
    """Migrate time/classroom data from details JSON"""

    try:
        # Initialize database
        print("🗄️ Initializing database...")
        await init_db()
        print("✅ Database initialized")

        updated = 0
        skipped = 0
        errors = 0

        async with async_session() as db:
            # Get all courses with details
            print("\n📚 Loading courses from database...")
            result = await db.execute(
                select(Course).where(Course.details.isnot(None))
            )
            courses = result.scalars().all()
            print(f"✅ Loaded {len(courses)} courses with details")

            print("\n🔄 Processing courses...")
            for idx, course in enumerate(courses, 1):
                try:
                    # Parse details JSON (double-encoded, so parse twice)
                    details_str = course.details

                    # First parse: unwrap outer JSON string
                    if details_str.startswith('"') and details_str.endswith('"'):
                        details_str = json.loads(details_str)

                    # Second parse: get actual dict
                    details_dict = json.loads(details_str)
                    time_classroom = details_dict.get('time_classroom', '')

                    if time_classroom and time_classroom != '-':
                        # Parse and extract time/classroom
                        time_str, classroom_str = parse_time_classroom(time_classroom)

                        # Update course fields (use actual DB column names)
                        course.time_codes = time_str if time_str else None
                        course.classroom_codes = classroom_str if classroom_str else None

                        db.add(course)
                        updated += 1

                        if updated % 100 == 0:
                            print(f"  ✓ Processed {updated} courses...")
                            await db.commit()
                    else:
                        skipped += 1

                except json.JSONDecodeError as e:
                    errors += 1
                    if errors <= 5:
                        print(f"  ✗ JSON decode error for course {course.id}: {e}")
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"  ✗ Error processing course {course.id}: {str(e)}")

                # Periodic commit
                if idx % 500 == 0:
                    await db.commit()
                    print(f"  💾 Committed batch at {idx} courses")

            # Final commit
            await db.commit()
            print("\n💾 Final commit completed")

        print(f"\n✅ Migration completed!")
        print(f"  - Updated: {updated}")
        print(f"  - Skipped: {skipped}")
        print(f"  - Errors: {errors}")

        # Show some samples
        print("\n🔍 Sample results:")
        async with async_session() as db:
            result = await db.execute(
                select(Course)
                .where(Course.time_codes.isnot(None))
                .limit(5)
            )
            sample_courses = result.scalars().all()

            for course in sample_courses:
                print(f"  - {course.crs_no}: {course.name}")
                print(f"    Time: {course.time}")
                print(f"    Classroom: {course.classroom or '(無)'}")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == '__main__':
    print("=" * 80)
    print("🕐 NYCU Course Time/Classroom Migration Tool")
    print("=" * 80)

    asyncio.run(migrate_time_classroom())

    print("=" * 80)
