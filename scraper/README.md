# NYCU Course Scraper

A comprehensive, production-ready web scraper for extracting course data from the NYCU timetable system. Built with async/await for high performance and includes extensive testing and error handling.

## Features

- **Asynchronous Architecture**: Built with `asyncio` and `aiohttp` for efficient concurrent scraping
- **Robust HTTP Client**: Automatic retries with exponential backoff, timeout handling, and connection pooling
- **Intelligent Parsing**: BeautifulSoup-based HTML parser with support for multiple field formats
- **Flexible Export**: Export to JSON or CSV formats, with options for grouping by semester
- **Comprehensive Testing**: 100+ unit and integration tests with mocking
- **Command-Line Interface**: Easy-to-use CLI with extensive options
- **Production-Ready**: Extensive logging, error handling, and progress tracking

## Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Setup

1. Install dependencies:
```bash
cd scraper
pip install -r requirements.txt
```

2. For Playwright (optional, if using browser automation):
```bash
playwright install chromium
```

## Usage

### Command Line Interface

#### Scrape All Courses (Default Range)

```bash
python -m app
```

This will scrape courses from academic years 99-114, both fall and spring semesters.

#### Scrape Specific Year Range

```bash
python -m app --start-year 110 --end-year 113
```

#### Scrape Specific Semester

```bash
python -m app --semester 113 1
```

This scrapes fall semester (semester 1) of academic year 113.

#### Scrape Only Fall Semesters

```bash
python -m app --semesters 1
```

#### Export to CSV

```bash
python -m app --format csv
```

#### Export to Both JSON and CSV

```bash
python -m app --format both
```

#### Group Output by Semester

```bash
python -m app --group-by-semester
```

This creates separate files for each semester (e.g., `courses_113_1.json`, `courses_113_2.json`).

#### Control Concurrency

```bash
python -m app --max-concurrent 10 --request-delay 0.2
```

#### Verbose Logging

```bash
python -m app --verbose
```

### Programmatic Usage

#### Basic Example

```python
import asyncio
from app.scraper import scrape_semester
from app.utils.file_handler import export_json

async def main():
    # Scrape a single semester
    courses = await scrape_semester(acy=113, sem=1, max_concurrent=5)

    # Export to JSON
    export_json(courses, "data/courses_113_1.json")

    print(f"Scraped {len(courses)} courses")

asyncio.run(main())
```

#### Scrape All Courses

```python
import asyncio
from app.scraper import scrape_all
from app.utils.file_handler import export_json

async def main():
    courses = await scrape_all(
        start_year=110,
        end_year=113,
        semesters=[1, 2],
        max_concurrent=5,
        request_delay=0.1
    )

    export_json(courses, "data/all_courses.json")
    print(f"Total: {len(courses)} courses")

asyncio.run(main())
```

#### Scrape Specific Courses

```python
import asyncio
from app.scraper import scrape_specific_courses

async def main():
    course_ids = [
        (113, 1, "3101"),
        (113, 1, "3102"),
        (113, 2, "5001"),
    ]

    courses = await scrape_specific_courses(course_ids, max_concurrent=5)

    for course in courses:
        print(f"{course.crs_no}: {course.name}")

asyncio.run(main())
```

#### Working with Files

```python
from app.utils.file_handler import (
    load_json,
    load_csv,
    export_by_semester,
    merge_json_files
)

# Load courses from JSON
courses = load_json("data/courses.json")

# Export grouped by semester
export_by_semester(courses, "data/semesters", format="json")

# Merge multiple JSON files
merge_json_files(
    ["data/113_1.json", "data/113_2.json"],
    "data/merged.json"
)
```

## Project Structure

```
scraper/
├── app/
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── course.py         # Course data model
│   ├── clients/
│   │   ├── __init__.py
│   │   └── http_client.py    # Async HTTP client
│   ├── parsers/
│   │   ├── __init__.py
│   │   └── course_parser.py  # HTML parser
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_handler.py   # File I/O utilities
│   └── scraper.py            # Main scraper logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── test_scraper/
│   │   ├── __init__.py
│   │   └── test_scraper_integration.py
│   ├── test_parsers/
│   │   ├── __init__.py
│   │   └── test_course_parser.py
│   ├── test_clients/
│   │   ├── __init__.py
│   │   └── test_http_client.py
│   └── test_utils/
│       ├── __init__.py
│       └── test_file_handler.py
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
└── README.md                # This file
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Fast tests only (exclude slow tests)
pytest -m "not slow"
```

### Run Specific Test File

```bash
pytest tests/test_parsers/test_course_parser.py
```

### Run Specific Test Function

```bash
pytest tests/test_parsers/test_course_parser.py::TestParseCourseHtml::test_parse_valid_course_html
```

### Verbose Output

```bash
pytest -v
```

## API Reference

### Course Model

```python
@dataclass
class Course:
    acy: int                    # Academic year (e.g., 113)
    sem: int                    # Semester (1 or 2)
    crs_no: str                 # Course number (e.g., "3101")
    name: Optional[str]         # Course name
    teacher: Optional[str]      # Instructor name
    credits: Optional[float]    # Number of credits
    dept: Optional[str]         # Department code
    time: Optional[str]         # Schedule/time
    classroom: Optional[str]    # Classroom location
    details: Dict[str, Any]     # Additional metadata
```

### Main Functions

#### `scrape_all(start_year, end_year, semesters, max_concurrent, request_delay)`
Scrape all courses across multiple years and semesters.

**Parameters:**
- `start_year` (int): Starting academic year (inclusive)
- `end_year` (int): Ending academic year (inclusive)
- `semesters` (List[int]): List of semesters to scrape (e.g., [1, 2])
- `max_concurrent` (int): Maximum concurrent requests
- `request_delay` (float): Delay between requests in seconds

**Returns:** `List[Course]`

#### `scrape_semester(acy, sem, max_concurrent, session, request_delay)`
Scrape all courses for a specific semester.

**Parameters:**
- `acy` (int): Academic year
- `sem` (int): Semester
- `max_concurrent` (int): Maximum concurrent requests
- `session` (Optional[ClientSession]): Reusable aiohttp session
- `request_delay` (float): Delay between requests

**Returns:** `List[Course]`

#### `fetch_course_data(acy, sem, crs_no, session)`
Fetch detailed data for a single course.

**Parameters:**
- `acy` (int): Academic year
- `sem` (int): Semester
- `crs_no` (str): Course number
- `session` (Optional[ClientSession]): Reusable aiohttp session

**Returns:** `Optional[Course]`

### File Handler Functions

#### `export_json(courses, filepath, pretty=True, ensure_ascii=False)`
Export courses to JSON file.

#### `export_csv(courses, filepath, include_details=False)`
Export courses to CSV file.

#### `load_json(filepath)`
Load courses from JSON file.

#### `load_csv(filepath)`
Load courses from CSV file.

#### `export_by_semester(courses, output_dir, format="json")`
Export courses grouped by semester.

## Configuration

### Environment Variables

Create a `.env` file in the scraper directory:

```env
# Request settings
MAX_CONCURRENT_REQUESTS=5
REQUEST_DELAY=0.1
REQUEST_TIMEOUT=5.0

# Retry settings
MAX_RETRIES=3
RETRY_DELAY=1.0

# Output settings
OUTPUT_DIR=data
DEFAULT_FORMAT=json
```

### Logging Configuration

Adjust logging level in your code:

```python
import logging

# Set to DEBUG for verbose output
logging.basicConfig(level=logging.DEBUG)

# Set to WARNING for minimal output
logging.basicConfig(level=logging.WARNING)
```

## Performance Considerations

### Concurrency

The scraper uses semaphores to limit concurrent requests:

- **Low concurrency (1-5)**: Safer, less likely to trigger rate limiting
- **Medium concurrency (5-10)**: Good balance of speed and safety
- **High concurrency (10+)**: Faster but may trigger server defenses

### Request Delays

Add delays between requests to be respectful to the server:

- **0.1s**: Fast scraping, use for testing
- **0.5s**: Moderate speed, recommended for production
- **1.0s+**: Very safe, use if experiencing issues

### Memory Usage

For large scrapes (10,000+ courses):

- Consider using `export_by_semester()` to split output
- Process courses in batches
- Use CSV format for smaller file sizes

## Troubleshooting

### Connection Errors

If you encounter frequent connection errors:

1. Reduce `max_concurrent` (try 2-3)
2. Increase `request_delay` (try 1.0s)
3. Increase `timeout` in HTTP client

### Parsing Errors

If courses are missing data:

1. Check the HTML structure hasn't changed
2. Review parser logs with `--verbose`
3. Update parser patterns in `course_parser.py`

### Memory Issues

For very large scrapes:

1. Use `--group-by-semester` to split output
2. Scrape in smaller year ranges
3. Process one semester at a time

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest`
2. Code is formatted: `black app/ tests/`
3. Type hints are included
4. Docstrings follow Google style
5. New features include tests

## License

This project is part of the NYCU Course Platform and follows the same license.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review test files for usage examples
3. Check logs with `--verbose` flag
4. Open an issue in the project repository
