"""
Main entry point for the NYCU course scraper.

This module provides a command-line interface for running the scraper
with various options and configurations.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

from app.scraper import scrape_all, scrape_semester, scrape_specific_courses
from app.utils.file_handler import export_json, export_csv, export_by_semester


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log"),
    ],
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Namespace object containing parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="NYCU Course Data Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all courses from year 110 to 113
  python -m app --start-year 110 --end-year 113

  # Scrape only fall semester of 2024 (year 113)
  python -m app --start-year 113 --end-year 113 --semesters 1

  # Scrape with higher concurrency
  python -m app --max-concurrent 10

  # Export to CSV format
  python -m app --format csv

  # Scrape specific semester
  python -m app --semester 113 1
        """,
    )

    parser.add_argument(
        "--start-year",
        type=int,
        default=99,
        help="Starting academic year (inclusive, default: 99)",
    )

    parser.add_argument(
        "--end-year",
        type=int,
        default=114,
        help="Ending academic year (inclusive, default: 114)",
    )

    parser.add_argument(
        "--semesters",
        type=int,
        nargs="+",
        default=[1, 2],
        help="Semesters to scrape (default: 1 2)",
    )

    parser.add_argument(
        "--semester",
        type=int,
        nargs=2,
        metavar=("YEAR", "SEM"),
        help="Scrape specific semester (e.g., --semester 113 1)",
    )

    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent requests (default: 5)",
    )

    parser.add_argument(
        "--request-delay",
        type=float,
        default=0.1,
        help="Delay between requests in seconds (default: 0.1)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Output directory for scraped data (default: data)",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "both"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--group-by-semester",
        action="store_true",
        help="Export separate files for each semester",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress info logging",
    )

    return parser.parse_args()


async def main():
    """
    Main async function to run the scraper.
    """
    args = parse_arguments()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    logger.info("=" * 60)
    logger.info("NYCU Course Data Scraper")
    logger.info("=" * 60)

    try:
        # Scrape courses based on arguments
        if args.semester:
            # Scrape specific semester
            acy, sem = args.semester
            logger.info(f"Scraping semester {acy}/{sem}")

            courses = await scrape_semester(
                acy=acy,
                sem=sem,
                max_concurrent=args.max_concurrent,
                request_delay=args.request_delay,
            )

            logger.info(f"Scraped {len(courses)} courses from {acy}/{sem}")

        else:
            # Scrape all specified years and semesters
            logger.info(
                f"Scraping years {args.start_year}-{args.end_year}, "
                f"semesters {args.semesters}"
            )

            courses = await scrape_all(
                start_year=args.start_year,
                end_year=args.end_year,
                semesters=args.semesters,
                max_concurrent=args.max_concurrent,
                request_delay=args.request_delay,
            )

            logger.info(f"Total courses scraped: {len(courses)}")

        # Export data
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if args.group_by_semester:
            # Export separate files for each semester
            logger.info("Exporting courses grouped by semester...")

            if args.format in ["json", "both"]:
                results = export_by_semester(courses, str(output_dir), format="json")
                successful = sum(results.values())
                logger.info(
                    f"Exported {successful}/{len(results)} semesters to JSON"
                )

            if args.format in ["csv", "both"]:
                results = export_by_semester(courses, str(output_dir), format="csv")
                successful = sum(results.values())
                logger.info(
                    f"Exported {successful}/{len(results)} semesters to CSV"
                )

        else:
            # Export single file
            if args.format in ["json", "both"]:
                json_path = output_dir / "courses.json"
                success = export_json(courses, str(json_path))
                if success:
                    logger.info(f"Exported to {json_path}")
                else:
                    logger.error("Failed to export JSON")

            if args.format in ["csv", "both"]:
                csv_path = output_dir / "courses.csv"
                success = export_csv(courses, str(csv_path))
                if success:
                    logger.info(f"Exported to {csv_path}")
                else:
                    logger.error("Failed to export CSV")

        # Print summary
        logger.info("=" * 60)
        logger.info("Scraping Summary")
        logger.info("=" * 60)
        logger.info(f"Total courses scraped: {len(courses)}")

        if courses:
            years = sorted(set(c.acy for c in courses))
            logger.info(f"Academic years: {min(years)}-{max(years)}")

            semesters_scraped = sorted(set((c.acy, c.sem) for c in courses))
            logger.info(f"Number of semesters: {len(semesters_scraped)}")

            with_names = sum(1 for c in courses if c.name)
            logger.info(f"Courses with names: {with_names}/{len(courses)}")

            with_teachers = sum(1 for c in courses if c.teacher)
            logger.info(f"Courses with teachers: {with_teachers}/{len(courses)}")

        logger.info("=" * 60)
        logger.info("Scraping completed successfully!")

    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Scraping failed with error: {e}", exc_info=True)
        sys.exit(1)


def run():
    """
    Entry point for running the scraper from command line.
    """
    asyncio.run(main())


if __name__ == "__main__":
    run()
