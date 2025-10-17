"""
Data import script for importing courses from JSON files.

This script reads course data from JSON files (typically from the scraper)
and imports them into the database. It handles deduplication and provides
detailed statistics about the import process.

Usage:
    python -m backend.scripts.import_data [path/to/courses.json]

If no path is provided, it defaults to scraper/data/courses.json
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

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


def read_json_courses(filepath: str | Path) -> list[dict[str, Any]]:
    """
    Read courses from a JSON file.

    Args:
        filepath: Path to the JSON file containing course data

    Returns:
        List of course dictionaries

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
        ValueError: If the JSON structure is invalid

    Example:
        >>> courses = read_json_courses("scraper/data/courses.json")
        >>> print(f"Loaded {len(courses)} courses")
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    logger.info(f"Reading courses from {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both direct list and nested structure
    if isinstance(data, list):
        courses = data
    elif isinstance(data, dict) and "courses" in data:
        courses = data["courses"]
    else:
        raise ValueError(
            "Invalid JSON structure. Expected a list or dict with 'courses' key"
        )

    logger.info(f"Successfully loaded {len(courses)} courses from file")
    return courses


async def import_courses(
    session: AsyncSession,
    courses: list[dict[str, Any]],
) -> dict[str, int]:
    """
    Import courses into the database with deduplication.

    This function imports courses in bulk, creating necessary semesters
    and skipping duplicate courses based on (acy, sem, crs_no) combination.

    Args:
        session: Database session
        courses: List of course dictionaries

    Returns:
        Dictionary with statistics:
        - created: Number of courses created
        - skipped: Number of courses skipped (duplicates)
        - errors: Number of courses that failed to import

    Example:
        >>> async with async_session() as session:
        ...     stats = await import_courses(session, courses)
        ...     print(f"Created: {stats['created']}")
    """
    stats = {"created": 0, "skipped": 0, "errors": 0}

    # Track existing course identifiers to skip duplicates within the batch
    existing_courses: set[tuple[int, int, str]] = set()

    logger.info(f"Starting import of {len(courses)} courses")

    for idx, course_data in enumerate(courses, 1):
        try:
            # Extract required fields
            acy = course_data.get("acy")
            sem = course_data.get("sem")
            crs_no = course_data.get("crs_no")

            # Validate required fields
            if not all([acy is not None, sem is not None, crs_no]):
                logger.warning(
                    f"Course {idx}: Missing required fields (acy, sem, or crs_no). "
                    f"Data: {course_data}"
                )
                stats["errors"] += 1
                continue

            # Check for duplicates within the batch
            course_key = (acy, sem, crs_no)
            if course_key in existing_courses:
                logger.debug(
                    f"Course {idx}: Skipping duplicate within batch - "
                    f"acy={acy}, sem={sem}, crs_no={crs_no}"
                )
                stats["skipped"] += 1
                continue

            # Ensure semester exists
            semester, created = await get_or_create_semester(session, acy, sem)
            if created:
                logger.info(f"Created new semester: acy={acy}, sem={sem}")

            # Check if course already exists in database
            from sqlalchemy.future import select

            from backend.app.models.course import Course

            statement = select(Course).where(
                Course.acy == acy,
                Course.sem == sem,
                Course.crs_no == crs_no,
            )
            result = await session.execute(statement)
            existing_course = result.scalar_one_or_none()

            if existing_course:
                logger.debug(
                    f"Course {idx}: Already exists in database - "
                    f"acy={acy}, sem={sem}, crs_no={crs_no}"
                )
                stats["skipped"] += 1
                existing_courses.add(course_key)
                continue

            # Create the course
            course = await create_course(
                session=session,
                acy=acy,
                sem=sem,
                crs_no=crs_no,
                name=course_data.get("name"),
                teacher=course_data.get("teacher"),
                credits=course_data.get("credits"),
                dept=course_data.get("dept"),
                time=course_data.get("time"),
                classroom=course_data.get("classroom"),
                details=json.dumps(course_data.get("details"))
                if course_data.get("details")
                else None,
            )

            existing_courses.add(course_key)
            stats["created"] += 1

            if stats["created"] % 10 == 0:
                logger.info(
                    f"Progress: {stats['created']} created, "
                    f"{stats['skipped']} skipped, "
                    f"{stats['errors']} errors"
                )

        except DatabaseError as e:
            logger.error(
                f"Course {idx}: Database error - {e.message}. "
                f"Course data: {course_data}"
            )
            stats["errors"] += 1
        except Exception as e:
            logger.error(
                f"Course {idx}: Unexpected error - {e}. Course data: {course_data}"
            )
            stats["errors"] += 1

    logger.info(
        f"Import completed: {stats['created']} created, "
        f"{stats['skipped']} skipped, "
        f"{stats['errors']} errors"
    )
    return stats


async def main(json_path: Optional[str] = None) -> int:
    """
    CLI entry point for the import script.

    Args:
        json_path: Optional path to JSON file. If not provided, uses default path.

    Returns:
        Exit code (0 for success, 1 for error)

    Example:
        >>> # Use default path
        >>> await main()
        >>> # Use custom path
        >>> await main("data/courses.json")
    """
    # Determine the path to the JSON file
    if json_path is None:
        # Default path relative to project root
        project_root = Path(__file__).parent.parent.parent
        json_path = project_root / "scraper" / "data" / "courses.json"
    else:
        json_path = Path(json_path)

    logger.info("=" * 70)
    logger.info("NYCU Course Platform - Data Import Script")
    logger.info("=" * 70)

    try:
        # Read courses from JSON
        courses = read_json_courses(json_path)

        if not courses:
            logger.warning("No courses found in the file. Nothing to import.")
            return 0

        # Initialize database
        logger.info("Initializing database...")
        await init_db()

        # Import courses
        async with async_session() as session:
            stats = await import_courses(session, courses)

        # Print summary
        logger.info("=" * 70)
        logger.info("Import Summary")
        logger.info("=" * 70)
        logger.info(f"Total courses in file: {len(courses)}")
        logger.info(f"Successfully created: {stats['created']}")
        logger.info(f"Skipped (duplicates): {stats['skipped']}")
        logger.info(f"Failed (errors): {stats['errors']}")
        logger.info("=" * 70)

        if stats["errors"] > 0:
            logger.warning(
                f"{stats['errors']} courses failed to import. "
                "Check the logs above for details."
            )

        return 0

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    # Get optional JSON path from command line
    json_path = sys.argv[1] if len(sys.argv) > 1 else None

    # Run the async main function
    exit_code = asyncio.run(main(json_path))
    sys.exit(exit_code)
