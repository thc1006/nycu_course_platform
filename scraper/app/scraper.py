"""
Main scraper logic for NYCU course data.

This module provides the core scraping functionality including course
discovery, data fetching, and orchestration of the scraping process
across multiple semesters.
"""

import asyncio
import logging
from typing import List, Optional, Set

import aiohttp

from app.models.course import Course
from app.clients.http_client import fetch_html, get_session
from app.parsers.course_parser import parse_course_html, parse_course_number_list


logger = logging.getLogger(__name__)


# NYCU timetable URLs
BASE_URL = "https://timetable.nycu.edu.tw"
SEARCH_URL = f"{BASE_URL}/?r=main%2Fcrsearch"
COURSE_DETAIL_URL = f"{BASE_URL}/?r=main%2Fcrsoutline&Acy={{acy}}&Sem={{sem}}&CrsNo={{crs_no}}"


async def discover_course_numbers(
    acy: int,
    sem: int,
    session: Optional[aiohttp.ClientSession] = None,
) -> List[str]:
    """
    Discover all course numbers for a specific academic year and semester.

    This function fetches the search results page from NYCU timetable
    and parses all available course numbers for the given academic year
    and semester.

    Args:
        acy: Academic year (e.g., 113 for 2024-2025)
        sem: Semester (1 for fall, 2 for spring)
        session: Optional aiohttp ClientSession for HTTP requests

    Returns:
        List of course numbers as strings (e.g., ["3101", "3102", ...])

    Example:
        >>> numbers = await discover_course_numbers(113, 1)
        >>> print(f"Found {len(numbers)} courses")
        Found 1500 courses
    """
    logger.info(f"Discovering course numbers for {acy}/{sem}")

    # Construct search URL with parameters
    # The NYCU search URL accepts Acy and Sem parameters
    search_url = f"{SEARCH_URL}&Acy={acy}&Sem={sem}"

    logger.debug(f"Fetching course list from: {search_url}")

    # Fetch the search results HTML
    html = await fetch_html(search_url, session=session)

    if not html:
        logger.warning(f"Failed to fetch course list for {acy}/{sem}")
        return []

    # Parse the HTML to extract course numbers
    course_numbers = parse_course_number_list(html)

    if not course_numbers:
        logger.warning(
            f"No course numbers found in search results for {acy}/{sem}. "
            f"The page might not have courses or the HTML structure may have changed."
        )
        return []

    # Remove duplicates while preserving order
    seen: Set[str] = set()
    unique_course_numbers: List[str] = []
    for crs_no in course_numbers:
        if crs_no not in seen:
            seen.add(crs_no)
            unique_course_numbers.append(crs_no)

    logger.info(
        f"Discovered {len(unique_course_numbers)} unique course numbers "
        f"for {acy}/{sem}"
    )

    return unique_course_numbers


async def fetch_course_data(
    acy: int,
    sem: int,
    crs_no: str,
    session: Optional[aiohttp.ClientSession] = None,
) -> Optional[Course]:
    """
    Fetch detailed data for a single course.

    This function fetches the course detail page from the NYCU timetable
    website and parses the HTML to extract structured course information.

    Args:
        acy: Academic year
        sem: Semester
        crs_no: Course number
        session: Optional aiohttp ClientSession for reusing connections

    Returns:
        Course object with parsed data, or None if fetch/parse fails

    Example:
        >>> course = await fetch_course_data(113, 1, "3101")
        >>> if course:
        ...     print(f"Fetched: {course.name}")
        ... else:
        ...     print("Failed to fetch course")
    """
    url = COURSE_DETAIL_URL.format(acy=acy, sem=sem, crs_no=crs_no)

    logger.debug(f"Fetching course data: {acy}/{sem}/{crs_no}")

    # Fetch HTML content
    html = await fetch_html(url, session=session)

    if not html:
        logger.warning(f"Failed to fetch HTML for course {acy}/{sem}/{crs_no}")
        return None

    # Parse the HTML
    course_data = parse_course_html(html)

    if not course_data:
        logger.warning(f"Failed to parse course data for {acy}/{sem}/{crs_no}")
        return None

    # Create Course object
    course = Course(
        acy=acy,
        sem=sem,
        crs_no=crs_no,
        name=course_data.get("name"),
        teacher=course_data.get("teacher"),
        credits=course_data.get("credits"),
        dept=course_data.get("dept"),
        time=course_data.get("time"),
        classroom=course_data.get("classroom"),
        details=course_data,  # Store all parsed data in details
    )

    logger.debug(f"Successfully created Course object for {acy}/{sem}/{crs_no}")
    return course


async def scrape_semester(
    acy: int,
    sem: int,
    max_concurrent: int = 5,
    session: Optional[aiohttp.ClientSession] = None,
    request_delay: float = 0.1,
) -> List[Course]:
    """
    Scrape all courses for a specific semester.

    This function coordinates the scraping of all courses in a semester,
    including course discovery and parallel fetching with concurrency limits.

    Args:
        acy: Academic year
        sem: Semester
        max_concurrent: Maximum number of concurrent requests (default: 5)
        session: Optional shared aiohttp ClientSession
        request_delay: Delay in seconds between requests (default: 0.1)

    Returns:
        List of successfully scraped Course objects

    Example:
        >>> courses = await scrape_semester(113, 1, max_concurrent=10)
        >>> print(f"Scraped {len(courses)} courses for 113/1")
    """
    logger.info(
        f"Starting scrape for semester {acy}/{sem} "
        f"(max_concurrent={max_concurrent})"
    )

    # Discover course numbers for this semester
    course_numbers = await discover_course_numbers(acy, sem, session=session)

    if not course_numbers:
        logger.warning(f"No course numbers found for {acy}/{sem}")
        return []

    logger.info(
        f"Found {len(course_numbers)} courses to scrape for {acy}/{sem}"
    )

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    # Track successful scrapes
    courses: List[Course] = []
    successful_count = 0
    failed_count = 0

    async def fetch_with_semaphore(crs_no: str) -> Optional[Course]:
        """Fetch a single course with semaphore control."""
        nonlocal successful_count, failed_count

        async with semaphore:
            course = await fetch_course_data(acy, sem, crs_no, session=session)

            if course:
                successful_count += 1
                if successful_count % 100 == 0:
                    logger.info(
                        f"Progress: {successful_count}/{len(course_numbers)} "
                        f"courses scraped successfully"
                    )
            else:
                failed_count += 1

            # Add delay between requests to avoid overwhelming server
            if request_delay > 0:
                await asyncio.sleep(request_delay)

            return course

    # Create tasks for all course numbers
    tasks = [fetch_with_semaphore(crs_no) for crs_no in course_numbers]

    # Execute all tasks and collect results
    logger.info(f"Fetching {len(tasks)} courses concurrently...")

    # Use asyncio.gather with return_exceptions to continue on errors
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out None and exception results
    for result in results:
        if isinstance(result, Course):
            courses.append(result)
        elif isinstance(result, Exception):
            logger.error(f"Task failed with exception: {result}")

    logger.info(
        f"Completed scrape for {acy}/{sem}: "
        f"{successful_count} successful, {failed_count} failed"
    )

    return courses


async def scrape_all(
    start_year: int = 99,
    end_year: int = 114,
    semesters: List[int] = None,
    max_concurrent: int = 5,
    request_delay: float = 0.1,
) -> List[Course]:
    """
    Scrape all courses across multiple academic years and semesters.

    This is the main orchestrator function that coordinates scraping
    across all specified years and semesters. It manages a shared HTTP
    session for efficiency and provides comprehensive logging.

    Args:
        start_year: Starting academic year (inclusive, default: 99)
        end_year: Ending academic year (inclusive, default: 114)
        semesters: List of semesters to scrape (default: [1, 2])
        max_concurrent: Maximum concurrent requests per semester (default: 5)
        request_delay: Delay between requests in seconds (default: 0.1)

    Returns:
        List of all successfully scraped Course objects across all semesters

    Example:
        >>> # Scrape recent years only
        >>> courses = await scrape_all(start_year=110, end_year=113)
        >>> print(f"Total courses scraped: {len(courses)}")
        >>>
        >>> # Scrape only fall semester
        >>> fall_courses = await scrape_all(
        ...     start_year=113,
        ...     end_year=113,
        ...     semesters=[1]
        ... )
    """
    if semesters is None:
        semesters = [1, 2]  # Default: fall and spring

    logger.info(
        f"Starting full scrape: years {start_year}-{end_year}, "
        f"semesters {semesters}"
    )

    all_courses: List[Course] = []
    total_semesters = (end_year - start_year + 1) * len(semesters)
    completed_semesters = 0

    # Create a shared HTTP session for all requests
    # Disable SSL verification for NYCU website
    session = await get_session(
        connector_limit=max_concurrent * 2,
        connector_limit_per_host=max_concurrent,
        ssl_verify=False,  # Disable SSL verification for NYCU timetable
    )

    try:
        # Iterate through all years and semesters
        for year in range(start_year, end_year + 1):
            for sem in semesters:
                logger.info(
                    f"Processing semester {year}/{sem} "
                    f"({completed_semesters + 1}/{total_semesters})"
                )

                # Scrape this semester
                semester_courses = await scrape_semester(
                    acy=year,
                    sem=sem,
                    max_concurrent=max_concurrent,
                    session=session,
                    request_delay=request_delay,
                )

                all_courses.extend(semester_courses)
                completed_semesters += 1

                logger.info(
                    f"Semester {year}/{sem} complete: "
                    f"{len(semester_courses)} courses scraped. "
                    f"Total so far: {len(all_courses)}"
                )

    finally:
        # Always close the session
        await session.close()
        logger.info("Closed HTTP session")

    logger.info(
        f"Scraping complete! Total courses scraped: {len(all_courses)} "
        f"across {completed_semesters} semesters"
    )

    # Log statistics
    unique_courses = len(set((c.acy, c.sem, c.crs_no) for c in all_courses))
    if unique_courses < len(all_courses):
        logger.warning(
            f"Found {len(all_courses) - unique_courses} duplicate courses"
        )

    return all_courses


async def scrape_specific_courses(
    course_ids: List[tuple[int, int, str]],
    max_concurrent: int = 5,
) -> List[Course]:
    """
    Scrape specific courses identified by (acy, sem, crs_no) tuples.

    This function is useful for updating or re-scraping specific courses
    without processing entire semesters.

    Args:
        course_ids: List of (acy, sem, crs_no) tuples identifying courses
        max_concurrent: Maximum number of concurrent requests (default: 5)

    Returns:
        List of successfully scraped Course objects

    Example:
        >>> course_ids = [(113, 1, "3101"), (113, 1, "3102"), (113, 2, "5001")]
        >>> courses = await scrape_specific_courses(course_ids)
        >>> print(f"Scraped {len(courses)} specific courses")
    """
    logger.info(f"Scraping {len(course_ids)} specific courses")

    session = await get_session(ssl_verify=False)  # Disable SSL verification
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_course(acy: int, sem: int, crs_no: str) -> Optional[Course]:
        async with semaphore:
            return await fetch_course_data(acy, sem, crs_no, session=session)

    try:
        tasks = [
            fetch_course(acy, sem, crs_no)
            for acy, sem, crs_no in course_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        courses = [r for r in results if isinstance(r, Course)]
        logger.info(
            f"Scraped {len(courses)}/{len(course_ids)} specific courses successfully"
        )
        return courses

    finally:
        await session.close()
