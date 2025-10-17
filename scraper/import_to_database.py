#!/usr/bin/env python3
"""
Import scraped course data into the backend database
"""

import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend path to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.models.course import Course
from sqlmodel import Session, create_engine, select


def import_courses(json_file: str, db_url: str = None):
    """Import courses from JSON file to database"""

    # Load course data
    logger.info(f"Loading courses from: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    courses = data.get('courses', [])
    logger.info(f"Found {len(courses)} courses to import")

    # Setup database connection
    if not db_url:
        # Use SQLite by default
        db_path = Path(__file__).parent.parent / "backend" / "course_platform.db"
        db_url = f"sqlite:///{db_path}"
        logger.info(f"Using database: {db_url}")

    engine = create_engine(db_url, echo=False)

    # Create tables if they don't exist
    from backend.app.models.course import Course
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    # Import courses
    imported = 0
    skipped = 0
    duplicates = 0

    with Session(engine) as session:
        for course_data in courses:
            try:
                # Check if course already exists
                existing = session.exec(
                    select(Course).where(
                        (Course.acy == course_data.get('acy')) &
                        (Course.sem == course_data.get('sem')) &
                        (Course.crs_no == course_data.get('crs_no'))
                    )
                ).first()

                if existing:
                    duplicates += 1
                    continue

                # Create course record
                course = Course(
                    acy=course_data.get('acy'),
                    sem=course_data.get('sem'),
                    crs_no=course_data.get('crs_no'),
                    name=course_data.get('name'),
                    teacher=course_data.get('teacher'),
                    credits=course_data.get('credits'),
                    dept=course_data.get('dept'),
                    time=course_data.get('time'),
                    classroom=course_data.get('classroom'),
                    details=course_data.get('details'),
                )

                session.add(course)
                imported += 1

                # Log progress
                if imported % 100 == 0:
                    logger.info(f"  Imported {imported} courses...")

            except Exception as e:
                logger.warning(f"Error importing course: {e}")
                skipped += 1

        # Commit all changes
        session.commit()

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ IMPORT COMPLETE!")
    logger.info(f"{'='*60}")
    logger.info(f"Imported: {imported} courses")
    logger.info(f"Duplicates: {duplicates} courses")
    logger.info(f"Skipped: {skipped} courses")
    logger.info(f"Total: {imported + duplicates + skipped} courses")

    return imported


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Import course data to database')
    parser.add_argument('--file', '-f', default='data/real_courses_nycu/courses_112_114.json',
                       help='JSON file to import')
    parser.add_argument('--db', '-d', help='Database URL')
    parser.add_argument('--delete-existing', action='store_true',
                       help='Delete existing courses first')

    args = parser.parse_args()

    json_file = Path(args.file)
    if not json_file.exists():
        logger.error(f"File not found: {json_file}")
        return

    # If delete-existing flag is set, clear the database first
    if args.delete_existing:
        logger.warning("Deleting existing courses...")
        from sqlmodel import Session, delete
        engine = create_engine(args.db or f"sqlite:///{Path(__file__).parent.parent / 'backend' / 'course_platform.db'}")
        with Session(engine) as session:
            session.exec(delete(Course))
            session.commit()
        logger.info("Existing courses deleted")

    # Import courses
    imported = import_courses(str(json_file), args.db)

    return imported


if __name__ == "__main__":
    main()
