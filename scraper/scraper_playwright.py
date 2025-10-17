#!/usr/bin/env python3
"""
NYCU Course Scraper using Playwright for JavaScript rendering.

This approach navigates through the NYCU website with a browser
and scrapes the actual rendered course data from the HTML.
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Academic years to scrape
ACADEMIC_YEARS = list(range(110, 115))  # 110 to 114
SEMESTERS = [1, 2]  # 1 = Fall, 2 = Spring

BASE_URL = "https://timetable.nycu.edu.tw"


async def scrape_semester_with_browser(
    browser: Browser,
    acy: int,
    sem: int,
) -> List[Dict]:
    """Scrape courses for a specific semester using browser automation."""
    logger.info(f"🌐 Scraping {acy}/{sem} with browser...")

    # Create new context for each semester to avoid state issues
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Navigate to NYCU timetable
        url = f"{BASE_URL}/?Acy={acy}&Sem={sem}"
        logger.info(f"  📍 Navigating to {url}...")
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait for the page to load JavaScript
        await page.wait_for_timeout(2000)

        # Try to find the search button and click it
        search_button = page.locator("#crstime_search")
        if await search_button.count() > 0:
            logger.info("  🔍 Found search button, clicking...")
            await search_button.click()
            await page.wait_for_timeout(2000)
        else:
            logger.warning("  ⚠️ Search button not found")

        # Wait for table to appear
        table = page.locator("table")
        if await table.count() > 0:
            logger.info("  📊 Found course table")
        else:
            logger.warning("  ⚠️ Table not found")

        # Extract courses from the page
        courses = await extract_courses_from_page(page, acy, sem)

        await context.close()
        return courses

    except Exception as e:
        logger.error(f"❌ Error scraping {acy}/{sem}: {e}")
        await context.close()
        return []


async def extract_courses_from_page(page: Page, acy: int, sem: int) -> List[Dict]:
    """Extract course data from rendered HTML page."""
    courses = []

    try:
        # Get all table rows (skip header)
        rows = await page.locator("table tr:not(:first-child)").all()
        logger.info(f"  📈 Found {len(rows)} course rows")

        for idx, row in enumerate(rows[:20]):  # Limit to first 20 for testing
            try:
                # Get all cells in this row
                cells = await row.locator("td").all_text_contents()

                if len(cells) >= 5:
                    course = {
                        "acy": acy,
                        "sem": sem,
                        "crs_no": cells[1].strip() if len(cells) > 1 else "",
                        "name": cells[4].strip() if len(cells) > 4 else "",
                        "teacher": cells[10].strip() if len(cells) > 10 else "",
                        "credits": cells[8].strip() if len(cells) > 8 else "",
                        "time": cells[7].strip() if len(cells) > 7 else "",
                        "raw_cells": cells
                    }
                    courses.append(course)
                    logger.debug(f"    ✓ Extracted: {course['crs_no']} - {course['name'][:30]}")

            except Exception as e:
                logger.debug(f"    ⚠️ Error extracting row {idx}: {e}")

    except Exception as e:
        logger.error(f"  ❌ Error extracting courses: {e}")

    return courses


async def main():
    """Main scraper using Playwright."""
    logger.info("=" * 80)
    logger.info("🚀 NYCU Course Scraper - Playwright Edition")
    logger.info(f"📅 Target years: {min(ACADEMIC_YEARS)}-{max(ACADEMIC_YEARS)}")
    logger.info("=" * 80)

    async with async_playwright() as p:
        # Launch browser
        logger.info("🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)

        all_courses = []
        total_semesters = len(ACADEMIC_YEARS) * len(SEMESTERS)
        current_semester = 0

        try:
            for acy in ACADEMIC_YEARS:
                for sem in SEMESTERS:
                    current_semester += 1
                    logger.info(f"\n[{current_semester}/{total_semesters}] {acy}/{sem}")
                    logger.info("-" * 80)

                    courses = await scrape_semester_with_browser(browser, acy, sem)

                    if courses:
                        all_courses.extend(courses)
                        logger.info(f"✅ Found {len(courses)} courses")
                        logger.info(f"📊 Running total: {len(all_courses)} courses")
                    else:
                        logger.info("📊 Running total: {len(all_courses)} courses (no data for this semester)")

                    # Rate limiting
                    await asyncio.sleep(1)

        finally:
            await browser.close()
            logger.info("\n🔌 Browser closed")

        # Save results
        logger.info(f"\n💾 Saving {len(all_courses)} courses...")
        with open("/tmp/nycu_courses_browser.json", 'w', encoding='utf-8') as f:
            json.dump(all_courses, f, ensure_ascii=False, indent=2)

        logger.info("\n" + "=" * 80)
        logger.info("📊 SCRAPING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total courses: {len(all_courses)}")

        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
