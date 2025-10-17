#!/usr/bin/env python3
"""
Real NYCU Course Scraper v2 - Using Exact API Format

Based on network analysis, this scraper uses the precise parameters
captured from NYCU's browser JavaScript.
"""

import asyncio
import json
import logging
import aiohttp
import ssl
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

# Academic years to scrape (110-114)
ACADEMIC_YEARS = list(range(110, 115))  # 110 to 114
SEMESTERS = [1, 2]  # 1 = Fall, 2 = Spring, X = Summer (optional)


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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
    )
    return session


async def fetch_acysem(session: aiohttp.ClientSession) -> List[str]:
    """Fetch available semesters from NYCU."""
    logger.info("📚 Fetching available semesters...")
    try:
        url = f"{BASE_URL}/?r=main/get_acysem"
        async with session.post(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200 and resp.content_type == "application/json":
                data = await resp.json()
                semesters = [item.get("T") for item in data if "T" in item]
                logger.info(f"✅ Found {len(semesters)} available semesters")
                return semesters
            else:
                logger.warning(f"⚠️ Unexpected response: {resp.status}, {resp.content_type}")
                return []
    except Exception as e:
        logger.error(f"❌ Error fetching acysem: {e}")
        return []


async def fetch_departments(
    session: aiohttp.ClientSession,
    acysem: str,
    acysemend: str,
) -> Dict[str, str]:
    """Fetch department list for a specific semester."""
    try:
        url = f"{BASE_URL}/?r=main/get_dep"
        payload = {
            "acysem": acysem,
            "acysemend": acysemend,
            "ftype": "870A5373-5B3A-415A-AF8F-BB01B733444F",  # Undergraduate courses
            "fcategory": "3*",
            "fcollege": "*",
            "flang": "en-us"
        }
        async with session.post(url, data=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200 and resp.content_type == "application/json":
                data = await resp.json()
                return data if isinstance(data, dict) else {}
            else:
                logger.warning(f"⚠️ get_dep: HTTP {resp.status}, {resp.content_type}")
                return {}
    except Exception as e:
        logger.error(f"❌ Error fetching departments: {e}")
        return {}


async def fetch_course_list(
    session: aiohttp.ClientSession,
    acy: str,
    sem: str,
    dep_uid: str = "*",
) -> List[Dict]:
    """Fetch course list using the exact API format."""
    try:
        url = f"{BASE_URL}/?r=main/get_cos_list"
        payload = {
            "m_acy": acy,
            "m_sem": sem,
            "m_acyend": acy,
            "m_semend": sem,
            "m_dep_uid": dep_uid,
            "m_group": "**",
            "m_grade": "**",
            "m_class": "**",
            "m_option": "111111111111",  # Show all columns
            "m_crsname": "",
            "m_teaname": "",
            "m_cos_id": "",
            "m_cos_code": "",
            "m_crstime": "",
            "m_crsoutline": "",
            "m_costype": "",
            "m_selcampus": ""
        }

        async with session.post(url, data=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                # Check if it's JSON
                if "application/json" in resp.headers.get("Content-Type", ""):
                    data = await resp.json()
                    if isinstance(data, list):
                        logger.debug(f"✅ Fetched {len(data)} courses for {acy}/{sem}/{dep_uid}")
                        return data
                else:
                    # Try to parse as JSON anyway
                    text = await resp.text()
                    try:
                        data = json.loads(text)
                        if isinstance(data, list):
                            logger.debug(f"✅ Fetched {len(data)} courses for {acy}/{sem}/{dep_uid}")
                            return data
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ Invalid JSON response for {acy}/{sem}/{dep_uid}")
                        return []
            else:
                logger.warning(f"⚠️ HTTP {resp.status} for {acy}/{sem}/{dep_uid}")
                return []
    except asyncio.TimeoutError:
        logger.warning(f"⏱️ Timeout for {acy}/{sem}/{dep_uid}")
        return []
    except Exception as e:
        logger.error(f"❌ Error fetching courses for {acy}/{sem}/{dep_uid}: {e}")
        return []


async def scrape_semester(
    session: aiohttp.ClientSession,
    acy: str,
    sem: str,
) -> List[Dict]:
    """Scrape all courses for a specific semester."""
    logger.info(f"🎯 Processing year {acy}, semester {sem}...")

    # Format semester for API (acysem = "YYYS")
    acysem = f"{acy}{sem}"

    # Try fetching with all departments
    logger.info(f"  📋 Fetching courses for {acysem}...")
    courses = await fetch_course_list(session, acy, sem, "*")

    if not courses:
        logger.info(f"  ℹ️ No courses found for {acy}/{sem}")
    else:
        logger.info(f"  ✅ Found {len(courses)} courses for {acy}/{sem}")

    return courses


async def scrape_all_years(years: List[int] = None, semesters: List[int] = None):
    """Scrape all courses for the specified years and semesters."""
    if years is None:
        years = ACADEMIC_YEARS
    if semesters is None:
        semesters = SEMESTERS

    logger.info("=" * 80)
    logger.info("🚀 NYCU Real Course Scraper v2 - Exact API Format")
    logger.info(f"📅 Target years: {min(years)}-{max(years)}")
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
                logger.info(f"\n[{current_semester}/{total_semesters}] {acy}/{sem}")
                logger.info("-" * 80)

                courses = await scrape_semester(session, str(acy), str(sem))

                if courses:
                    all_courses.extend(courses)
                    logger.info(f"📊 Running total: {len(all_courses)} courses")
                else:
                    logger.info(f"📊 Running total: {len(all_courses)} courses (no data for this semester)")

                # Rate limiting
                await asyncio.sleep(0.5)

    finally:
        await session.close()
        logger.info("🔌 Session closed")

    return all_courses


async def save_results(courses: List[Dict], filename: str = "/tmp/nycu_courses_real_v2.json"):
    """Save scraped courses to JSON file."""
    logger.info(f"\n💾 Saving {len(courses)} courses to {filename}...")

    # Create directory if needed
    import os
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Successfully saved to {filename}")

    # Print statistics
    logger.info("\n" + "=" * 80)
    logger.info("📊 SCRAPING STATISTICS")
    logger.info("=" * 80)
    logger.info(f"Total courses scraped: {len(courses)}")

    if courses:
        # Sample course
        sample = courses[0]
        logger.info(f"\nSample course data:")
        logger.info(f"  Keys: {list(sample.keys())}")
        if isinstance(sample, dict):
            for key, value in list(sample.items())[:5]:
                logger.info(f"  {key}: {value}")

    logger.info("=" * 80)


async def main():
    """Main entry point."""
    try:
        # Scrape real data for years 110-114
        courses = await scrape_all_years(ACADEMIC_YEARS, SEMESTERS)

        # Save results
        await save_results(courses)

        logger.info("\n✅ Scraping completed!")
        return 0

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
