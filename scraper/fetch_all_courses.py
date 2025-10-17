#!/usr/bin/env python3
"""
Fetch all NYCU courses across all academic years and semesters.

This script orchestrates the complete scraping process for NYCU course data
from academic years 99-114, semesters 1-2. It provides progress tracking,
statistics, and exports all courses to JSON format.

Usage:
    python fetch_all_courses.py [options]

Options:
    --start-year    Starting academic year (default: 99)
    --end-year      Ending academic year (default: 114)
    --semesters     Comma-separated semesters to fetch (default: 1,2)
    --output        Output JSON file path (default: data/courses.json)
    --concurrent    Max concurrent requests (default: 10)
    --delay         Delay between requests in seconds (default: 0.2)
    --verbose       Enable verbose logging
    --test-mode     Test with limited range (year 113 only)
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scraper import scrape_all
from app.models.course import Course
from nycu_config import (
    ACADEMIC_YEAR_START,
    ACADEMIC_YEAR_END,
    SEMESTERS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_OUTPUT_FILE,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_REQUEST_DELAY,
    LOG_FORMAT,
)


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the scraper.

    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("scraper.log", mode="a"),
        ],
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Fetch all NYCU courses from timetable system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--start-year",
        type=int,
        default=ACADEMIC_YEAR_START,
        help="Starting academic year (inclusive)",
    )

    parser.add_argument(
        "--end-year",
        type=int,
        default=ACADEMIC_YEAR_END,
        help="Ending academic year (inclusive)",
    )

    parser.add_argument(
        "--semesters",
        type=str,
        default=",".join(map(str, SEMESTERS)),
        help="Comma-separated semesters to fetch (e.g., '1,2')",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(DEFAULT_OUTPUT_DIR, DEFAULT_OUTPUT_FILE),
        help="Output JSON file path",
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=DEFAULT_MAX_CONCURRENT,
        help="Maximum concurrent requests",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY,
        help="Delay between requests in seconds",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Test mode: fetch only year 113, semester 1 (for testing)",
    )

    return parser.parse_args()


def export_courses_to_json(
    courses: List[Course], output_path: str
) -> None:
    """
    Export courses to JSON file.

    Args:
        courses: List of Course objects to export
        output_path: Path to output JSON file
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Convert courses to dictionaries
    courses_data = [course.to_dict() for course in courses]

    # Add metadata
    export_data = {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "total_courses": len(courses),
            "scraper_version": "1.0.0",
        },
        "courses": courses_data,
    }

    # Write to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    logging.info(f"Exported {len(courses)} courses to {output_path}")


def print_statistics(courses: List[Course]) -> None:
    """
    Print detailed statistics about scraped courses.

    Args:
        courses: List of scraped Course objects
    """
    if not courses:
        print("\nNo courses were scraped.")
        return

    print("\n" + "=" * 80)
    print("SCRAPING STATISTICS")
    print("=" * 80)

    # Total courses
    print(f"\nTotal courses scraped: {len(courses)}")

    # Courses by year
    courses_by_year: Dict[int, int] = {}
    for course in courses:
        courses_by_year[course.acy] = courses_by_year.get(course.acy, 0) + 1

    print("\nCourses by academic year:")
    for year in sorted(courses_by_year.keys()):
        count = courses_by_year[year]
        print(f"  Year {year}: {count:>5} courses")

    # Courses by semester
    courses_by_semester: Dict[int, int] = {}
    for course in courses:
        courses_by_semester[course.sem] = courses_by_semester.get(course.sem, 0) + 1

    print("\nCourses by semester:")
    for sem in sorted(courses_by_semester.keys()):
        count = courses_by_semester[sem]
        sem_name = "Fall" if sem == 1 else "Spring"
        print(f"  Semester {sem} ({sem_name}): {count:>5} courses")

    # Courses by year and semester
    print("\nCourses by year and semester:")
    year_sem_counts: Dict[tuple[int, int], int] = {}
    for course in courses:
        key = (course.acy, course.sem)
        year_sem_counts[key] = year_sem_counts.get(key, 0) + 1

    for (year, sem) in sorted(year_sem_counts.keys()):
        count = year_sem_counts[(year, sem)]
        print(f"  {year}/{sem}: {count:>5} courses")

    # Data completeness
    print("\nData completeness:")
    total = len(courses)

    fields = ["name", "teacher", "credits", "dept", "time", "classroom"]
    for field in fields:
        count = sum(1 for c in courses if getattr(c, field) is not None)
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {field.capitalize():12} : {count:>5} / {total} ({percentage:.1f}%)")

    # Unique course numbers
    unique_course_numbers = len(set((c.acy, c.sem, c.crs_no) for c in courses))
    duplicates = len(courses) - unique_course_numbers
    print(f"\nUnique courses (acy, sem, crs_no): {unique_course_numbers}")
    if duplicates > 0:
        print(f"Duplicate entries: {duplicates}")

    # Top departments (if dept field is populated)
    depts: Dict[str, int] = {}
    for course in courses:
        if course.dept:
            depts[course.dept] = depts.get(course.dept, 0) + 1

    if depts:
        print("\nTop 10 departments by course count:")
        for dept, count in sorted(depts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {dept:20} : {count:>5} courses")

    print("\n" + "=" * 80)


async def main() -> int:
    """
    Main entry point for the scraper.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(verbose=args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("NYCU Course Scraper - Starting")
    logger.info("=" * 80)

    # Parse semesters
    try:
        semesters = [int(s.strip()) for s in args.semesters.split(",")]
    except ValueError:
        logger.error(f"Invalid semester format: {args.semesters}")
        return 1

    # Validate semesters
    if not all(s in [1, 2] for s in semesters):
        logger.error("Semesters must be 1 or 2")
        return 1

    # Test mode overrides
    if args.test_mode:
        logger.info("Running in TEST MODE - fetching only year 113, semester 1")
        start_year = 113
        end_year = 113
        semesters = [1]
    else:
        start_year = args.start_year
        end_year = args.end_year

    # Validate year range
    if start_year > end_year:
        logger.error(f"Start year ({start_year}) must be <= end year ({end_year})")
        return 1

    # Log configuration
    total_semesters = (end_year - start_year + 1) * len(semesters)
    logger.info(f"Configuration:")
    logger.info(f"  Academic years: {start_year} to {end_year}")
    logger.info(f"  Semesters: {', '.join(map(str, semesters))}")
    logger.info(f"  Total semesters to scrape: {total_semesters}")
    logger.info(f"  Max concurrent requests: {args.concurrent}")
    logger.info(f"  Request delay: {args.delay}s")
    logger.info(f"  Output file: {args.output}")
    logger.info("")

    # Confirm if not in test mode
    if not args.test_mode:
        print(f"\nAbout to scrape {total_semesters} semesters from NYCU timetable.")
        print(f"This may take a significant amount of time and network bandwidth.")
        response = input("\nDo you want to continue? (y/N): ")
        if response.lower() not in ["y", "yes"]:
            logger.info("Scraping cancelled by user")
            return 0

    # Start scraping
    start_time = datetime.now()
    logger.info(f"Starting scrape at {start_time.isoformat()}")

    try:
        courses = await scrape_all(
            start_year=start_year,
            end_year=end_year,
            semesters=semesters,
            max_concurrent=args.concurrent,
            request_delay=args.delay,
        )

        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"Scraping completed at {end_time.isoformat()}")
        logger.info(f"Duration: {duration}")
        logger.info(f"Scraped {len(courses)} courses")
        logger.info("=" * 80)

        # Export to JSON
        if courses:
            export_courses_to_json(courses, args.output)

            # Print statistics
            print_statistics(courses)

            # Success summary
            print(f"\n{'='*80}")
            print(f"SUCCESS: Scraped {len(courses)} courses in {duration}")
            print(f"Data exported to: {args.output}")
            print(f"{'='*80}\n")

            return 0
        else:
            logger.warning("No courses were scraped!")
            return 1

    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user (Ctrl+C)")
        return 1

    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    # Run async main
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
