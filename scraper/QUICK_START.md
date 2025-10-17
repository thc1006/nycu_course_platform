# Quick Start Guide - NYCU Course Scraper

## Installation

```bash
# Navigate to scraper directory
cd scraper

# Install dependencies
pip install -r requirements.txt
```

## Quick Test (Recommended First Step)

Test with a limited range to verify everything works:

```bash
python fetch_all_courses.py --test-mode
```

This will:
- Fetch only year 113, semester 1
- Take 5-15 minutes
- Output to `data/courses.json`
- Display statistics when complete

## Full Scrape

After testing, run the full scrape:

```bash
python fetch_all_courses.py
```

This will:
- Scrape years 99-114 (16 years)
- Scrape semesters 1 and 2 (32 total)
- Take 3-8 hours depending on settings
- Prompt for confirmation before starting

## Common Commands

```bash
# Test mode (year 113, semester 1 only)
python fetch_all_courses.py --test-mode

# Specific year range
python fetch_all_courses.py --start-year 110 --end-year 114

# Only fall semester
python fetch_all_courses.py --semesters 1

# Custom output location
python fetch_all_courses.py --output my_courses.json

# Faster scraping (higher concurrency)
python fetch_all_courses.py --concurrent 20 --delay 0.1

# Verbose logging
python fetch_all_courses.py --verbose

# Help
python fetch_all_courses.py --help
```

## Run Tests

```bash
# All tests
pytest tests/test_nycu_integration.py -v

# Specific test category
pytest tests/test_nycu_integration.py::TestYearRangeScraping -v
```

## Output

Results are saved to `data/courses.json` (or custom path) with format:

```json
{
  "metadata": {
    "export_date": "2025-10-16T12:00:00",
    "total_courses": 35482,
    "scraper_version": "1.0.0"
  },
  "courses": [
    {
      "acy": 113,
      "sem": 1,
      "crs_no": "DCP1234",
      "name": "資料結構",
      "teacher": "王教授",
      "credits": 3.0,
      "dept": "資訊工程學系",
      "time": "星期二 3,4",
      "classroom": "EC114",
      "details": { ... }
    }
  ]
}
```

## Logs

Logs are written to:
- Console (INFO level)
- `scraper.log` file (all levels)

## Troubleshooting

**No courses found?**
```bash
python fetch_all_courses.py --test-mode --verbose
```

**Slow performance?**
```bash
python fetch_all_courses.py --concurrent 20 --delay 0.1
```

**Need help?**
```bash
python fetch_all_courses.py --help
```

See `NYCU_SCRAPER_GUIDE.md` for complete documentation.
