"""
NYCU Timetable System Configuration.

This module contains configuration constants for the NYCU timetable system
including base URLs, API endpoints, academic year ranges, and semester
definitions.
"""

# NYCU Timetable Base URL
NYCU_TIMETABLE_BASE_URL = "https://timetable.nycu.edu.tw/"

# URL Paths
NYCU_SEARCH_PATH = "?r=main%2Fcrsearch"
NYCU_DETAIL_PATH = "?r=main%2Fcrsoutline"

# Full URLs
NYCU_SEARCH_URL = f"{NYCU_TIMETABLE_BASE_URL}{NYCU_SEARCH_PATH}"
NYCU_DETAIL_URL = f"{NYCU_TIMETABLE_BASE_URL}{NYCU_DETAIL_PATH}"

# Academic Years to scrape
# Range from academic year 99 (2010-2011) to 114 (2025-2026)
ACADEMIC_YEAR_START = 99
ACADEMIC_YEAR_END = 114
ACADEMIC_YEARS = range(ACADEMIC_YEAR_START, ACADEMIC_YEAR_END + 1)

# Semesters
# 1 = Fall semester
# 2 = Spring semester
SEMESTERS = [1, 2]

# Request configuration
DEFAULT_REQUEST_DELAY = 0.2  # seconds between requests
DEFAULT_MAX_CONCURRENT = 10  # maximum concurrent requests
DEFAULT_TIMEOUT = 15.0  # request timeout in seconds
DEFAULT_MAX_RETRIES = 3  # maximum retry attempts

# Data export configuration
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_OUTPUT_FILE = "courses.json"

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Course number validation
# NYCU course numbers are typically 4-7 characters (alphanumeric)
COURSE_NUMBER_PATTERN = r"^[A-Z0-9]{4,7}$"

# Statistics tracking
STATS_PRINT_INTERVAL = 100  # Print progress every N courses
SEMESTER_PROGRESS_UPDATE = True  # Print progress for each semester
