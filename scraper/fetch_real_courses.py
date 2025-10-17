#!/usr/bin/env python3
"""
Real NYCU Course Scraper using correct API endpoints.

This scraper uses the actual NYCU timetable API endpoints discovered through
JavaScript analysis. It fetches real course data for academic years 110-114.
"""

import asyncio
import json
import logging
import aiohttp
import ssl
import certifi
from typing import List, Dict, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NYCU API Configuration
BASE_URL = "https://timetable.nycu.edu.tw"
GET_ACYSEM_URL = f"{BASE_URL}/?r=main/get_acysem"
GET_DEP_URL = f"{BASE_URL}/?r=main/get_dep"
GET_COS_LIST_URL = f"{BASE_URL}/?r=main/get_cos_list"

# Academic years to scrape (110-114)
ACADEMIC_YEARS = list(range(110, 115))  # 110 to 114
SEMESTERS = [1, 2]  # 1 = Fall, 2 = Spring


async def get_session():
    """Create an aiohttp session with SSL verification disabled for NYCU."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(
        limit=50,
        limit_per_host=10,
        ttl_dns_cache=300,
        ssl=ssl_context,
    )

    session = aiohttp.ClientSession(
        connector=connector,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    )
    return session


async def fetch_available_semesters(session: aiohttp.ClientSession) -> Dict:
    """Fetch available academic years and semesters from NYCU."""
    logger.info("📚 Fetching available semesters from NYCU...")
    try:
        async with session.post(GET_ACYSEM_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                logger.info(f"✅ Successfully fetched {len(data)} available semesters")
                return data
            else:
                logger.warning(f"⚠️ Failed to fetch semesters: HTTP {resp.status}")
                return {}
    except Exception as e:
        logger.error(f"❌ Error fetching semesters: {e}")
        return {}


async def fetch_departments(session: aiohttp.ClientSession, acy: int, sem: int) -> List[Dict]:
    """Fetch department list for a specific semester."""
    try:
        payload = {
            "acy": str(acy),
            "sem": str(sem),
        }
        async with session.post(GET_DEP_URL, data=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data if isinstance(data, list) else []
            else:
                logger.warning(f"⚠️ Failed to fetch departments for {acy}/{sem}: HTTP {resp.status}")
                return []
    except Exception as e:
        logger.error(f"❌ Error fetching departments for {acy}/{sem}: {e}")
        return []


async def fetch_course_list(
    session: aiohttp.ClientSession,
    acy: int,
    sem: int,
    dep_uid: str = "**",
) -> List[Dict]:
    """Fetch course list for a specific semester and department."""
    try:
        payload = {
            "m_acy": str(acy),
            "m_sem": str(sem),
            "m_acyend": str(acy),
            "m_semend": str(sem),
            "m_dep_uid": dep_uid,
            "m_group": "**",
            "m_grade": "**",
            "m_class": "**",
            "m_option": "**",
        }

        async with session.post(GET_COS_LIST_URL, data=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                data = await resp.json()
                if isinstance(data, list):
                    logger.debug(f"✅ Fetched {len(data)} courses for {acy}/{sem}/{dep_uid}")
                    return data
                else:
                    logger.warning(f"⚠️ Unexpected response format for {acy}/{sem}/{dep_uid}")
                    return []
            else:
                logger.warning(f"⚠️ HTTP {resp.status} when fetching courses for {acy}/{sem}/{dep_uid}")
                return []
    except asyncio.TimeoutError:
        logger.warning(f"⏱️ Timeout fetching courses for {acy}/{sem}/{dep_uid}")
        return []
    except Exception as e:
        logger.error(f"❌ Error fetching courses for {acy}/{sem}/{dep_uid}: {e}")
        return []


async def scrape_semester(
    session: aiohttp.ClientSession,
    acy: int,
    sem: int,
) -> List[Dict]:
    """Scrape all courses for a specific semester."""
    logger.info(f"🎯 Starting scrape for {acy}/{sem}...")

    # Fetch departments
    departments = await fetch_departments(session, acy, sem)
    logger.info(f"📍 Found {len(departments)} departments for {acy}/{sem}")

    if not departments:
        # Try fetching all courses without department filter
        logger.info(f"⚠️ No departments found, trying all courses for {acy}/{sem}...")
        courses = await fetch_course_list(session, acy, sem, "**")
        return courses

    # Fetch courses for each department
    all_courses = []
    for idx, dept in enumerate(departments, 1):
        dept_uid = dept.get("uid", "**")
        dept_name = dept.get("name", "Unknown")

        logger.info(f"  [{idx}/{len(departments)}] 📚 Fetching {dept_name} ({dept_uid})...")
        courses = await fetch_course_list(session, acy, sem, dept_uid)

        if courses:
            logger.info(f"      ✅ Found {len(courses)} courses")
            all_courses.extend(courses)
        else:
            logger.info(f"      ℹ️ No courses found")

        # Rate limiting - be respectful to NYCU servers
        await asyncio.sleep(0.5)

    logger.info(f"✅ Completed scrape for {acy}/{sem}: {len(all_courses)} total courses")
    return all_courses


async def scrape_all_years(years: List[int] = None, semesters: List[int] = None):
    """Scrape all courses for the specified years and semesters."""
    if years is None:
        years = ACADEMIC_YEARS
    if semesters is None:
        semesters = SEMESTERS

    logger.info("=" * 80)
    logger.info("🚀 NYCU Real Course Scraper - Starting Real-Time Debug Mode")
    logger.info(f"📅 Scraping years: {min(years)}-{max(years)}")
    logger.info(f"📋 Semesters: {semesters}")
    logger.info("=" * 80)

    session = await get_session()
    all_courses = []

    try:
        total_semesters = len(years) * len(semesters)
        current_semester = 0

        for acy in years:
            for sem in semesters:
                current_semester += 1
                logger.info(f"\n[{current_semester}/{total_semesters}] Processing {acy}/{sem}")
                logger.info("-" * 80)

                courses = await scrape_semester(session, acy, sem)

                if courses:
                    all_courses.extend(courses)
                    logger.info(f"📊 Running total: {len(all_courses)} courses")

                # Rate limiting
                await asyncio.sleep(1)

    finally:
        await session.close()
        logger.info("🔌 Session closed")

    return all_courses


async def save_results(courses: List[Dict], filename: str = "nycu_courses.json"):
    """Save scraped courses to JSON file."""
    logger.info(f"\n💾 Saving {len(courses)} courses to {filename}...")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Successfully saved to {filename}")

    # Print statistics
    logger.info("\n" + "=" * 80)
    logger.info("📊 SCRAPING STATISTICS")
    logger.info("=" * 80)
    logger.info(f"Total courses scraped: {len(courses)}")

    # Group by semester
    by_semester = {}
    for course in courses:
        semester_key = course.get("semester", "Unknown")
        by_semester[semester_key] = by_semester.get(semester_key, 0) + 1

    logger.info(f"Semesters with data: {len(by_semester)}")
    for sem, count in sorted(by_semester.items()):
        logger.info(f"  {sem}: {count} courses")

    logger.info("=" * 80)


async def main():
    """Main entry point."""
    try:
        # Scrape real data for years 110-114
        courses = await scrape_all_years(ACADEMIC_YEARS, SEMESTERS)

        # Save results
        await save_results(courses, "/tmp/nycu_courses_real.json")

        return 0

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
