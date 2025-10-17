#!/usr/bin/env python3
"""
NYCU Real Course Scraper using Playwright for Dynamic Content
Handles JavaScript-rendered pages and complex course listings
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import re
from typing import List, Dict, Any, Optional

from playwright.async_api import async_playwright, Page, Browser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"
OUTPUT_FILE = Path("data/courses_real.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


class NYCUCoursesScraper:
    """Scraper for NYCU courses using Playwright"""

    def __init__(self):
        self.courses: List[Dict[str, Any]] = []
        self.browser: Optional[Browser] = None

    async def init_browser(self):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)

    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def scrape_semester(self, year: int, semester: int) -> List[Dict[str, Any]]:
        """
        Scrape courses for a specific semester

        Args:
            year: Academic year (e.g., 113)
            semester: Semester number (1 or 2)

        Returns:
            List of course dictionaries
        """
        logger.info(f"🎯 Scraping {year}/{semester}...")
        courses_found = []

        try:
            page = await self.browser.new_page()
            page.set_default_timeout(30000)  # 30 second timeout

            # Navigate to timetable
            url = f"{BASE_URL}?r=main/crsearch&Acy={year}&Sem={semester}"
            logger.info(f"  📍 Navigating to: {url}")

            await page.goto(url, wait_until="networkidle")

            # Wait for course list to load
            await page.wait_for_load_state("networkidle")

            # Check if there are any course links
            course_links = await page.query_selector_all("a[href*='CrsNo=']")
            logger.info(f"  ✓ Found {len(course_links)} course links")

            # Extract course numbers and names
            for link in course_links:
                try:
                    # Get href to extract course number
                    href = await link.get_attribute("href")
                    if not href:
                        continue

                    # Extract CrsNo parameter
                    match = re.search(r'CrsNo=([^&]+)', href)
                    if not match:
                        continue

                    crs_no = match.group(1)
                    course_name = await link.text_content()
                    course_name = course_name.strip() if course_name else "Unknown"

                    # Try to find teacher and other details in the row
                    row = await link.locator("xpath=ancestor::tr").element_handle()
                    if row:
                        cells = await page.eval_on_selector_all("tr", "rows => rows.map(r => Array.from(r.querySelectorAll('td')).map(c => c.textContent.trim()))")

                    courses_found.append({
                        "acy": year,
                        "sem": semester,
                        "crs_no": crs_no,
                        "name": course_name,
                        "teacher": "TBD",
                        "credits": 3.0,
                        "dept": "Unknown",
                        "time": "TBD",
                        "classroom": "TBD",
                        "details": None
                    })

                except Exception as e:
                    logger.warning(f"  ⚠️ Error extracting course: {e}")
                    continue

            await page.close()

        except Exception as e:
            logger.error(f"  ❌ Error scraping {year}/{semester}: {e}")

        logger.info(f"  📊 Scraped {len(courses_found)} courses for {year}/{semester}")
        return courses_found

    async def scrape_all(self, start_year: int = 110, end_year: int = 114) -> List[Dict[str, Any]]:
        """
        Scrape all courses for all semesters in the range

        Args:
            start_year: Starting year
            end_year: Ending year

        Returns:
            List of all courses
        """
        await self.init_browser()

        try:
            total_courses = []

            for year in range(start_year, end_year + 1):
                for sem in [1, 2]:
                    courses = await self.scrape_semester(year, sem)
                    total_courses.extend(courses)

                    # Small delay between requests
                    await asyncio.sleep(1)

            return total_courses

        finally:
            await self.close_browser()


async def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("🚀 NYCU Course Scraper - Playwright Version")
    logger.info("=" * 80)

    scraper = NYCUCoursesScraper()

    try:
        logger.info("📥 Scraping courses for years 110-114...")
        courses = await scraper.scrape_all(start_year=110, end_year=114)

        logger.info("=" * 80)
        logger.info(f"✅ Completed! Total courses scraped: {len(courses)}")
        logger.info("=" * 80)

        # Save to JSON
        if courses:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(courses, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Courses saved to {OUTPUT_FILE}")
        else:
            logger.warning("⚠️ No courses were scraped!")

        return courses

    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    courses = asyncio.run(main())
