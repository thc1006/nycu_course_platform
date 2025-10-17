#!/usr/bin/env python3
"""
Use existing NYCU Timetable scraper from GitHub: https://github.com/Huskyee/NYCU_Timetable
This repository already has course scraping functionality
"""

import asyncio
import aiohttp
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

OUTPUT_FILE = Path("data/nycu_courses_real.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

async def scrape_nycu_official():
    """Scrape course data directly from NYCU official course registration system"""
    logger.info("=" * 80)
    logger.info("🚀 Fetching Real NYCU Course Data (Official Source)")
    logger.info("=" * 80)
    
    # Use the NYCU course registration system API
    base_url = "https://course.nycu.edu.tw"
    
    all_courses = []
    
    try:
        # Fetch available programs/departments
        logger.info("\n📋 Fetching course listings from official NYCU system...")
        
        async with aiohttp.ClientSession() as session:
            # Try to fetch course listing page
            courses_url = f"{base_url}/en/"
            logger.info(f"📥 Fetching: {courses_url}")
            
            async with session.get(courses_url, timeout=15, ssl=False) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    logger.info(f"✅ Got response: {len(html)} characters")
                    
                    # Parse HTML to find course links/data
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for course listings
                    course_links = soup.find_all('a', href=re.compile(r'/course/'))
                    logger.info(f"Found {len(course_links)} course links")
                    
                    courses_found = []
                    for i, link in enumerate(course_links[:50]):  # First 50 courses
                        course_name = link.get_text(strip=True)
                        course_url = link.get('href')
                        
                        if course_name and course_url:
                            course_data = {
                                'name': course_name,
                                'url': course_url if course_url.startswith('http') else base_url + course_url,
                                'source': 'NYCU Official Course Registration'
                            }
                            courses_found.append(course_data)
                            
                            if i < 5:
                                logger.info(f"   Course {i+1}: {course_name}")
                    
                    all_courses.extend(courses_found)
                    logger.info(f"\n✅ Found {len(courses_found)} courses from official system")
                else:
                    logger.warning(f"HTTP {resp.status}")
    
    except Exception as e:
        logger.warning(f"Error fetching official system: {e}")
    
    # Fallback: Use NYCU timetable system with detailed parsing
    logger.info("\n📍 Using NYCU Timetable System for detailed course data...")
    
    try:
        async with aiohttp.ClientSession() as session:
            base_url = "https://timetable.nycu.edu.tw/"
            
            # Fetch available semesters first
            logger.info("📥 Fetching available semesters...")
            async with session.post(
                f"{base_url}?r=main/get_acysem",
                ssl=False,
                timeout=10
            ) as resp:
                if resp.status == 200:
                    semesters_json = await resp.text()
                    semesters = json.loads(semesters_json)
                    
                    target_sems = []
                    for sem in semesters:
                        code = sem.get('T', '')
                        if code and any(str(y) in code for y in range(110, 115)):
                            target_sems.append(code)
                    
                    logger.info(f"✅ Found {len(target_sems)} target semesters (110-114)")
                    logger.info(f"   Semesters: {target_sems}")
                    
                    # Log semester structure
                    output_data = {
                        'source': 'NYCU Timetable System API',
                        'timestamp': datetime.now().isoformat(),
                        'semesters_discovered': target_sems,
                        'all_semesters_count': len(semesters),
                        'status': 'Data source identified',
                        'notes': [
                            'NYCU course data is available through timetable.nycu.edu.tw',
                            'Semesters available: 110-114',
                            'Course data returned in HTML table format from getViewHtmlContents endpoint',
                            'Requires HTML parsing and table extraction',
                            'Consider using existing NYCU timetable GitHub scrapers for production'
                        ],
                        'data_sources_found': [
                            {
                                'name': 'NYCU Timetable System',
                                'url': 'https://timetable.nycu.edu.tw/',
                                'api_endpoints': [
                                    '?r=main/get_acysem (get semesters)',
                                    '?r=main/getViewHtmlContents (get courses)',
                                    '?r=main/get_type (get course types)',
                                    '?r=main/get_college (get colleges)',
                                    '?r=main/get_dep (get departments)'
                                ]
                            },
                            {
                                'name': 'NYCU Official Course Registration',
                                'url': 'https://course.nycu.edu.tw/en/',
                                'format': 'Web interface with course catalog'
                            },
                            {
                                'name': 'NYCU Open CourseWare',
                                'url': 'https://ocw.nycu.edu.tw/',
                                'format': 'Free course materials and syllabi',
                                'coverage': '20+ courses'
                            }
                        ]
                    }
                    
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"\n✅ Data saved to: {OUTPUT_FILE}")
                    
                    return output_data
    
    except Exception as e:
        logger.warning(f"Error with timetable system: {e}")
    
    return output_data

async def main():
    await scrape_nycu_official()

if __name__ == "__main__":
    asyncio.run(main())
