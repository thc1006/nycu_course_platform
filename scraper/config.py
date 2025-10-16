"""
Configuration for the NYCU timetable scraper.

You can customize the start and end years, concurrency limits, and
throttling settings here.  These values are imported by `scraper.py`.
"""

from dataclasses import dataclass


@dataclass
class ScraperConfig:
    # Earliest academic year to scrape (inclusive).  NYCU timetable
    # data appears to go back to at least year 99 (circa 2010).
    start_year: int = 99
    # Latest academic year to scrape (inclusive).  Update this as
    # new years become available.
    end_year: int = 114
    # List of semester identifiers.  Typically 1 = fall term, 2 = spring.
    semesters: list[int] = (1, 2)
    # Concurrency controls for HTTP requests.  Lower values reduce load
    # on the university server.
    max_concurrent_requests: int = 5
    # Seconds to wait between requests.  Adjust upward if you
    # encounter throttling or CAPTCHA.
    request_delay: float = 0.5


DEFAULT_CONFIG = ScraperConfig()