"""
Database seeding script for creating sample test data.

This script populates the database with sample semesters and courses
for development and testing purposes. It creates diverse course data
across multiple departments to facilitate testing of search and filtering.

Usage:
    python -m backend.scripts.seed_db
"""

import asyncio
import logging
import random
import sys
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.course import create_course
from backend.app.database.semester import get_or_create_semester
from backend.app.database.session import async_session, init_db
from backend.app.utils.exceptions import DatabaseError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Sample data for generating realistic courses
DEPARTMENTS = {
    "CS": "Computer Science",
    "MATH": "Mathematics",
    "PHY": "Physics",
    "EE": "Electrical Engineering",
    "CHEM": "Chemistry",
}

COURSE_NAMES = {
    "CS": [
        "Introduction to Computer Science",
        "Data Structures and Algorithms",
        "Database Systems",
        "Computer Networks",
        "Operating Systems",
        "Software Engineering",
        "Machine Learning",
        "Artificial Intelligence",
        "Computer Architecture",
        "Web Development",
    ],
    "MATH": [
        "Calculus I",
        "Calculus II",
        "Linear Algebra",
        "Differential Equations",
        "Discrete Mathematics",
        "Probability Theory",
        "Statistics",
        "Real Analysis",
        "Abstract Algebra",
        "Numerical Analysis",
    ],
    "PHY": [
        "General Physics I",
        "General Physics II",
        "Classical Mechanics",
        "Electromagnetism",
        "Quantum Mechanics",
        "Thermodynamics",
        "Optics",
        "Modern Physics",
        "Solid State Physics",
        "Nuclear Physics",
    ],
    "EE": [
        "Circuit Analysis",
        "Digital Logic Design",
        "Signals and Systems",
        "Electromagnetic Fields",
        "Electronic Circuits",
        "Control Systems",
        "Communication Systems",
        "Digital Signal Processing",
        "VLSI Design",
        "Power Systems",
    ],
    "CHEM": [
        "General Chemistry I",
        "General Chemistry II",
        "Organic Chemistry I",
        "Organic Chemistry II",
        "Physical Chemistry",
        "Analytical Chemistry",
        "Inorganic Chemistry",
        "Biochemistry",
        "Chemical Engineering",
        "Environmental Chemistry",
    ],
}

TEACHERS = [
    "Dr. Alice Chen",
    "Prof. Bob Wang",
    "Dr. Carol Liu",
    "Prof. David Lee",
    "Dr. Emma Zhang",
    "Prof. Frank Lin",
    "Dr. Grace Wu",
    "Prof. Henry Huang",
    "Dr. Iris Yang",
    "Prof. Jack Tsai",
]

TIMES = [
    "Mon 09:00-12:00",
    "Mon 13:00-16:00",
    "Tue 09:00-12:00",
    "Tue 13:00-16:00",
    "Wed 09:00-12:00",
    "Wed 13:00-16:00",
    "Thu 09:00-12:00",
    "Thu 13:00-16:00",
    "Fri 09:00-12:00",
    "Fri 13:00-16:00",
]

CLASSROOMS = [
    "EC015", "EC016", "EC114", "EC212", "EC213",
    "ED117", "ED202", "ED203", "ED304", "ED305",
    "EE101", "EE201", "EE202", "EE303", "EE304",
]


async def create_sample_courses(
    session: AsyncSession,
    acy: int,
    sem: int,
    num_courses: int = 25,
) -> int:
    """
    Create sample courses for a given semester.

    Args:
        session: Database session
        acy: Academic year
        sem: Semester number
        num_courses: Number of courses to create (default: 25)

    Returns:
        Number of courses successfully created

    Example:
        >>> async with async_session() as session:
        ...     count = await create_sample_courses(session, 113, 1, 25)
        ...     print(f"Created {count} courses")
    """
    # Ensure semester exists
    semester, created = await get_or_create_semester(session, acy, sem)
    if created:
        logger.info(f"Created semester: acy={acy}, sem={sem}, id={semester.id}")
    else:
        logger.info(f"Using existing semester: acy={acy}, sem={sem}, id={semester.id}")

    created_count = 0
    courses_per_dept = num_courses // len(DEPARTMENTS)
    remainder = num_courses % len(DEPARTMENTS)

    for dept_idx, (dept_code, dept_name) in enumerate(DEPARTMENTS.items()):
        # Distribute remainder courses among first departments
        dept_course_count = courses_per_dept + (1 if dept_idx < remainder else 0)

        course_names = COURSE_NAMES[dept_code]
        random.shuffle(course_names)

        for i in range(min(dept_course_count, len(course_names))):
            try:
                # Generate course number (dept code + number)
                course_number = f"{dept_code}{(i + 1) * 100 + random.randint(1, 99):04d}"

                # Select random attributes
                course_name = course_names[i]
                teacher = random.choice(TEACHERS)
                credits = random.choice([1.0, 2.0, 3.0, 3.0, 3.0, 4.0])  # Weighted toward 3.0
                time = random.choice(TIMES)
                classroom = random.choice(CLASSROOMS)

                # Create course
                course = await create_course(
                    session=session,
                    acy=acy,
                    sem=sem,
                    crs_no=course_number,
                    name=course_name,
                    teacher=teacher,
                    credits=credits,
                    dept=dept_code,
                    time=time,
                    classroom=classroom,
                    details=None,
                )

                created_count += 1
                logger.debug(
                    f"Created course: {course.crs_no} - {course.name} "
                    f"(Teacher: {teacher}, Credits: {credits})"
                )

            except DatabaseError as e:
                logger.error(f"Failed to create course: {e.message}")
            except Exception as e:
                logger.error(f"Unexpected error creating course: {e}")

    logger.info(
        f"Created {created_count} courses for semester acy={acy}, sem={sem}"
    )
    return created_count


async def main() -> int:
    """
    CLI entry point for the seed script.

    Creates sample data:
    - All semesters from year 99 to 114 (both semesters 1 and 2)
    - 30 sample courses per semester
    - Diverse departments: CS, MATH, PHY, EE, CHEM
    - Total: 32 semesters × 30 courses = 960 courses

    Returns:
        Exit code (0 for success, 1 for error)

    Example:
        >>> await main()
        0
    """
    logger.info("=" * 70)
    logger.info("NYCU Course Platform - Database Seeding Script")
    logger.info("Creating complete dataset for years 99-114")
    logger.info("=" * 70)

    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()

        # Define all semesters to create (years 99-114, both semesters 1 and 2)
        semesters = []
        for year in range(99, 115):  # 99 to 114 inclusive
            semesters.append((year, 1, 30))   # Fall semester, 30 courses
            semesters.append((year, 2, 30))   # Spring semester, 30 courses

        total_created = 0
        semesters_created = 0

        # Create courses for each semester
        logger.info(f"\nCreating courses for {len(semesters)} semesters...")
        logger.info("-" * 70)

        async with async_session() as session:
            for idx, (acy, sem, num_courses) in enumerate(semesters, 1):
                logger.info(f"[{idx}/{len(semesters)}] Seeding semester acy={acy}, sem={sem}")

                count = await create_sample_courses(session, acy, sem, num_courses)
                total_created += count
                if count > 0:
                    semesters_created += 1

        # Print summary
        logger.info("=" * 70)
        logger.info("Seeding Summary")
        logger.info("=" * 70)
        logger.info(f"Academic years covered: 99-114 (16 years)")
        logger.info(f"Semesters created: {semesters_created}")
        logger.info(f"Total courses created: {total_created}")
        logger.info(f"Departments: {', '.join(DEPARTMENTS.keys())}")
        logger.info(f"Average courses per semester: {total_created // semesters_created if semesters_created > 0 else 0}")
        logger.info("=" * 70)
        logger.info("Database seeding completed successfully!")

        return 0

    except Exception as e:
        logger.error(f"Unexpected error during seeding: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
