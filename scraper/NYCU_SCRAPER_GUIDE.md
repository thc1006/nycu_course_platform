# NYCU Course Scraper - Complete Guide

## Overview

This scraper fetches **ALL** course data from the NYCU Timetable system (https://timetable.nycu.edu.tw/) for academic years 99-114 and semesters 1-2.

## Features

- **Complete Coverage**: Scrapes all academic years (99-114) and both semesters (1-2)
- **Proper URL Construction**: Uses correct NYCU timetable URLs with proper parameter encoding
- **Robust Parsing**: Multiple parsing strategies to handle different HTML structures
- **Concurrent Fetching**: Parallel requests with configurable concurrency limits
- **Error Handling**: Retry logic, timeout handling, and graceful error recovery
- **Progress Tracking**: Detailed logging and progress updates during scraping
- **Data Export**: Exports to structured JSON format with metadata
- **Comprehensive Tests**: Full integration test suite

## Architecture

### Key Files

1. **nycu_config.py** - Configuration for NYCU timetable system
   - Base URLs and paths
   - Academic year ranges (99-114)
   - Semester definitions (1-2)
   - Request parameters

2. **app/scraper.py** - Main scraping logic
   - `discover_course_numbers()` - Fetch all course numbers for a semester
   - `fetch_course_data()` - Fetch detailed course information
   - `scrape_semester()` - Scrape all courses in a semester
   - `scrape_all()` - Orchestrate scraping across multiple years/semesters

3. **app/parsers/course_parser.py** - HTML parsing
   - `parse_course_number_list()` - Extract course numbers from search results
   - `parse_course_html()` - Extract course details from detail pages
   - Multiple parsing strategies for robustness

4. **fetch_all_courses.py** - Main execution script
   - Command-line interface
   - Progress tracking and statistics
   - JSON export with metadata

5. **tests/test_nycu_integration.py** - Integration tests
   - Course discovery tests
   - Detail fetching tests
   - Full semester/year range tests
   - Error handling tests

## Installation

```bash
cd scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (if needed)
playwright install chromium
```

## Usage

### Basic Usage

Fetch all courses (years 99-114, semesters 1-2):

```bash
python fetch_all_courses.py
```

**Note**: This will prompt for confirmation before starting the full scrape.

### Test Mode

Test the scraper with a limited range (year 113, semester 1 only):

```bash
python fetch_all_courses.py --test-mode
```

### Custom Range

Fetch specific year range:

```bash
# Fetch years 110-114
python fetch_all_courses.py --start-year 110 --end-year 114

# Fetch only fall semester (semester 1)
python fetch_all_courses.py --semesters 1

# Fetch only spring semester (semester 2)
python fetch_all_courses.py --semesters 2
```

### Advanced Options

```bash
python fetch_all_courses.py \
  --start-year 99 \
  --end-year 114 \
  --semesters 1,2 \
  --output data/all_courses.json \
  --concurrent 20 \
  --delay 0.1 \
  --verbose
```

### Options Reference

- `--start-year` - Starting academic year (default: 99)
- `--end-year` - Ending academic year (default: 114)
- `--semesters` - Comma-separated semesters (default: 1,2)
- `--output` - Output JSON file path (default: data/courses.json)
- `--concurrent` - Max concurrent requests (default: 10)
- `--delay` - Delay between requests in seconds (default: 0.2)
- `--verbose` - Enable debug logging
- `--test-mode` - Test with limited range

## URL Structure

### Search URL
```
https://timetable.nycu.edu.tw/?r=main%2Fcrsearch&Acy={acy}&Sem={sem}
```

Example: `https://timetable.nycu.edu.tw/?r=main%2Fcrsearch&Acy=113&Sem=1`

### Course Detail URL
```
https://timetable.nycu.edu.tw/?r=main%2Fcrsoutline&Acy={acy}&Sem={sem}&CrsNo={crs_no}
```

Example: `https://timetable.nycu.edu.tw/?r=main%2Fcrsoutline&Acy=113&Sem=1&CrsNo=DCP1234`

## Scraping Process

### 1. Course Discovery

For each academic year/semester:
1. Fetch search results page with `Acy` and `Sem` parameters
2. Parse HTML to extract all course numbers
3. Return unique list of course numbers

### 2. Course Detail Fetching

For each discovered course number:
1. Construct detail URL with `Acy`, `Sem`, and `CrsNo`
2. Fetch course detail page
3. Parse HTML to extract course information:
   - Course name (課程名稱)
   - Teacher (授課教師)
   - Credits (學分)
   - Department (系所)
   - Time (上課時間)
   - Classroom (教室)
   - Other metadata

### 3. Data Aggregation

1. Collect all courses across all semesters
2. Remove duplicates
3. Export to JSON with metadata

## Parsing Strategies

The parser uses multiple strategies to handle different HTML structures:

### Strategy 1: Link Parsing (Most Reliable)
- Finds all links with `CrsNo=` parameter
- Extracts course numbers from URL parameters
- Works well with NYCU's link-based navigation

### Strategy 2: Table Parsing
- Identifies course tables by ID/class
- Extracts course numbers from table cells
- Validates format (4-7 alphanumeric characters)

### Strategy 3: Div/Element Parsing
- Searches for course items in div structures
- Pattern matching for course number format
- Fallback for non-table layouts

### Strategy 4: JSON Parsing
- Looks for embedded JSON in script tags
- Extracts course data from JSON structures
- Handles dynamic JavaScript-based pages

## Data Format

### Course Object

Each course has the following fields:

```python
{
  "acy": 113,              # Academic year
  "sem": 1,                # Semester (1=Fall, 2=Spring)
  "crs_no": "DCP1234",     # Course number
  "name": "資料結構",       # Course name
  "teacher": "王教授",      # Teacher name
  "credits": 3.0,          # Number of credits
  "dept": "資訊工程學系",   # Department
  "time": "星期二 3,4",     # Class time
  "classroom": "EC114",    # Classroom
  "details": {             # Additional metadata
    "description": "...",
    "required": true,
    "evaluation": "...",
    ...
  }
}
```

### Export Format

```json
{
  "metadata": {
    "export_date": "2025-10-16T12:00:00",
    "total_courses": 25000,
    "scraper_version": "1.0.0"
  },
  "courses": [
    { ... },
    { ... }
  ]
}
```

## Testing

### Run All Tests

```bash
cd scraper
pytest tests/test_nycu_integration.py -v
```

### Run Specific Test Categories

```bash
# Test course number parsing
pytest tests/test_nycu_integration.py::TestCourseNumberParsing -v

# Test course detail parsing
pytest tests/test_nycu_integration.py::TestCourseDetailParsing -v

# Test course discovery
pytest tests/test_nycu_integration.py::TestCourseDiscovery -v

# Test year range scraping
pytest tests/test_nycu_integration.py::TestYearRangeScraping -v
```

### Test Coverage

```bash
pytest tests/test_nycu_integration.py --cov=app --cov-report=html
```

## Expected Results

### Total Coverage

- **Academic Years**: 99-114 (16 years)
- **Semesters per Year**: 2 (Fall and Spring)
- **Total Semesters**: 32
- **Expected Courses**: 15,000-50,000+ (depending on NYCU catalog)

### Statistics Example

```
================================================================================
SCRAPING STATISTICS
================================================================================

Total courses scraped: 35,482

Courses by academic year:
  Year 99:   1,234 courses
  Year 100:  1,345 courses
  ...
  Year 114:  2,567 courses

Courses by semester:
  Semester 1 (Fall):   17,891 courses
  Semester 2 (Spring): 17,591 courses

Data completeness:
  Name         : 35,482 / 35,482 (100.0%)
  Teacher      : 34,123 / 35,482 (96.2%)
  Credits      : 35,201 / 35,482 (99.2%)
  Dept         : 33,987 / 35,482 (95.8%)
  Time         : 32,456 / 35,482 (91.5%)
  Classroom    : 31,234 / 35,482 (88.0%)
```

## Performance

### Timing Estimates

With default settings (10 concurrent, 0.2s delay):

- **Per Course**: ~0.3-0.5 seconds
- **Per Semester**: 5-15 minutes (depending on course count)
- **Full Scrape (32 semesters)**: 3-8 hours

### Optimization

To speed up scraping:

```bash
# Increase concurrency and reduce delay
python fetch_all_courses.py --concurrent 20 --delay 0.1
```

**Note**: Be respectful of server resources. Excessive requests may cause issues.

## Error Handling

The scraper includes robust error handling:

1. **Network Errors**: Automatic retry with exponential backoff
2. **Timeouts**: Configurable timeout with retry logic
3. **Parse Errors**: Graceful handling, course marked as failed
4. **Invalid Data**: Validation and logging of data issues

## Logging

Logs are written to:
- **Console**: INFO level (or DEBUG with `--verbose`)
- **File**: `scraper.log` (all messages, append mode)

## Troubleshooting

### No Courses Found

If the scraper finds no courses:

1. Check network connectivity
2. Verify NYCU timetable URL is accessible
3. Check if HTML structure has changed (update parsers)
4. Enable verbose logging: `--verbose`

### Low Success Rate

If many courses fail to fetch:

1. Reduce concurrency: `--concurrent 5`
2. Increase delay: `--delay 0.5`
3. Check for rate limiting
4. Verify course URLs are correct

### Parse Errors

If course details are not extracted:

1. Manually inspect HTML structure
2. Update parsing patterns in `course_parser.py`
3. Add new parsing strategies if needed

## Future Enhancements

- [ ] Add support for specific department filtering
- [ ] Implement incremental updates (only fetch new/changed courses)
- [ ] Add database export (PostgreSQL, MongoDB)
- [ ] Create web dashboard for monitoring scraping progress
- [ ] Add support for course prerequisites and relationships
- [ ] Implement caching for previously scraped courses

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check the integration tests for usage examples
- Review the inline documentation in source files
- Open an issue on the project repository
