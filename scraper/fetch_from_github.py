#!/usr/bin/env python3
"""
Fetch Real NYCU Course Data from Public GitHub Sources
Uses: https://github.com/Sea-n/nctu-timetable (historical NCTU/NYCU data)
      https://github.com/Huskyee/NYCU_Timetable (current NYCU data)
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

OUTPUT_FILE = Path("data/courses_from_github.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

async def fetch_nctu_timetable_data():
    """Fetch historical NCTU/NYCU course data from GitHub"""
    logger.info("=" * 80)
    logger.info("🚀 Fetching Real NYCU/NCTU Course Data from GitHub")
    logger.info("=" * 80)
    
    base_url = "https://raw.githubusercontent.com/Sea-n/nctu-timetable/master/pretty"
    
    all_courses = []
    errors = []
    
    # Years 110-114 (2021-2025)
    # Note: Year 110 = 2021, which is the merger year
    # NCTU data available for 87-110, so we can get 110 but may not have 111-114
    
    years = [110, 111, 112, 113, 114]
    semesters = [1, 2]  # Fall (1), Spring (2)
    
    async with aiohttp.ClientSession() as session:
        for year in years:
            for sem in semesters:
                sem_name = "Fall" if sem == 1 else "Spring"
                file_name = f"{year}-{sem}.json"
                url = f"{base_url}/{file_name}"
                
                logger.info(f"\n📥 Fetching: {year}/{sem} ({sem_name} Semester)")
                logger.info(f"   URL: {url}")
                
                try:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            if isinstance(data, list):
                                course_count = len(data)
                                logger.info(f"   ✅ Success! Found {course_count} courses")
                                
                                # Add semester info to each course
                                for course in data:
                                    course['semester_year'] = year
                                    course['semester_num'] = sem
                                    all_courses.append(course)
                            else:
                                logger.warning(f"   ⚠️  Response is not a list: {type(data)}")
                        else:
                            logger.warning(f"   ⚠️  HTTP {resp.status}")
                            errors.append((year, sem, resp.status))
                            
                except asyncio.TimeoutError:
                    logger.warning(f"   ⏱️  Timeout")
                    errors.append((year, sem, "timeout"))
                except json.JSONDecodeError:
                    logger.warning(f"   ❌ Invalid JSON")
                    errors.append((year, sem, "json_error"))
                except Exception as e:
                    logger.warning(f"   ❌ Error: {e}")
                    errors.append((year, sem, str(e)))
    
    logger.info(f"\n{'='*80}")
    logger.info(f"📊 Results Summary")
    logger.info(f"{'='*80}")
    logger.info(f"✅ Total courses fetched: {len(all_courses)}")
    logger.info(f"❌ Failed fetches: {len(errors)}")
    
    if errors:
        logger.info("\nFailed semester fetches:")
        for year, sem, error in errors:
            sem_name = "Fall" if sem == 1 else "Spring"
            logger.info(f"   {year}/{sem_name} - {error}")
    
    # Show sample course data
    if all_courses:
        logger.info(f"\n📋 Sample Course (First Course):")
        sample = all_courses[0]
        for key, value in list(sample.items())[:10]:
            logger.info(f"   {key}: {value}")
    
    # Save to file
    output_data = {
        'source': 'GitHub: https://github.com/Sea-n/nctu-timetable',
        'timestamp': datetime.now().isoformat(),
        'years': '110-114',
        'total_courses': len(all_courses),
        'fetched_successfully': len(all_courses) > 0,
        'errors_count': len(errors),
        'courses': all_courses
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ Data saved to: {OUTPUT_FILE}")
    logger.info(f"📦 Total file size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    return all_courses

async def main():
    courses = await fetch_nctu_timetable_data()
    return courses

if __name__ == "__main__":
    asyncio.run(main())
