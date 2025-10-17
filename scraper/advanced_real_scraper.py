#!/usr/bin/env python3
"""
Advanced NYCU Real Course Scraper - Using Form Data
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"
OUTPUT_FILE = Path("data/real_courses_final.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

class AdvancedNYCUScraper:
    def __init__(self):
        self.courses = []
        self.semesters_map = {
            '1141': ('114', '1', 'Fall 2025'),
            '1132': ('113', '2', 'Spring 2024'),
            '1131': ('113', '1', 'Fall 2024'),
            '1122': ('112', '2', 'Spring 2023'),
            '1121': ('112', '1', 'Fall 2023'),
            '1112': ('111', '2', 'Spring 2022'),
            '1111': ('111', '1', 'Fall 2022'),
            '1102': ('110', '2', 'Spring 2021'),
            '1101': ('110', '1', 'Fall 2021'),
        }

    async def scrape_with_http(self):
        """Use direct HTTP requests with form data"""
        logger.info("=" * 80)
        logger.info("🚀 Advanced NYCU Course Scraper - HTTP Form Data Approach")
        logger.info("=" * 80)

        async with aiohttp.ClientSession() as session:
            # First, get the page to establish session
            logger.info("\n📍 Fetching NYCU timetable main page...")
            try:
                async with session.get(BASE_URL, timeout=aiohttp.ClientTimeout(total=15), ssl=False) as resp:
                    if resp.status == 200:
                        logger.info(f"✅ Got response: {resp.status}")
                    else:
                        logger.warning(f"⚠️ Status: {resp.status}")
            except Exception as e:
                logger.warning(f"Connection issue: {e}")

            # Now try to get course data with form parameters
            logger.info("\n📥 Fetching courses with form parameters...")
            
            for sem_code, (year, sem, sem_name) in list(self.semesters_map.items())[:3]:  # Test first 3
                logger.info(f"\n🎯 Semester: {sem_code} ({sem_name})")
                
                # Form data to send
                form_data = {
                    'fAcySem': sem_code,
                    'fType': '',  # No type filter
                    'fCollege': '',  # No college filter
                    'fDep': '',  # No department filter
                }
                
                try:
                    # POST request with form data
                    endpoint = f"{BASE_URL}?r=main/getViewHtmlContents"
                    async with session.post(
                        endpoint,
                        data=form_data,
                        timeout=aiohttp.ClientTimeout(total=15),
                        ssl=False
                    ) as resp:
                        if resp.status == 200:
                            html_content = await resp.text()
                            logger.info(f"  ✅ Got HTML response: {len(html_content)} chars")
                            
                            if len(html_content) > 500:
                                # Parse and extract courses
                                soup = BeautifulSoup(html_content, 'html.parser')
                                tables = soup.find_all('table')
                                logger.info(f"  📊 Found {len(tables)} tables")
                                
                                # Extract courses from tables
                                course_count = 0
                                for table in tables:
                                    rows = table.find_all('tr')
                                    for row in rows:
                                        cells = row.find_all(['td', 'th'])
                                        if len(cells) >= 2:
                                            cell_texts = [cell.get_text(strip=True) for cell in cells]
                                            # Skip if looks like header
                                            if not any(kw in cell_texts[0].lower() for kw in ['course', '課程', '課號']):
                                                if cell_texts[0] and cell_texts[1]:
                                                    course = {
                                                        'year': year,
                                                        'semester': sem,
                                                        'semester_code': sem_code,
                                                        'crs_no': cell_texts[0],
                                                        'name': cell_texts[1] if len(cell_texts) > 1 else '',
                                                        'credits': cell_texts[2] if len(cell_texts) > 2 else '',
                                                        'teacher': cell_texts[4] if len(cell_texts) > 4 else '',
                                                    }
                                                    self.courses.append(course)
                                                    course_count += 1
                                
                                logger.info(f"  📚 Extracted {course_count} courses")
                            else:
                                logger.warning(f"  ⚠️ Response too short: {len(html_content)} chars")
                        else:
                            logger.warning(f"  ⚠️ Status: {resp.status}")
                            
                except asyncio.TimeoutError:
                    logger.warning(f"  ⏱️ Timeout")
                except Exception as e:
                    logger.warning(f"  ❌ Error: {e}")
                
                await asyncio.sleep(1)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"📊 Summary: {len(self.courses)} courses collected")
            
            # Save results
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'NYCU Timetable - HTTP Form Data',
                'courses_count': len(self.courses),
                'courses': self.courses
            }
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Data saved to: {OUTPUT_FILE}")
            return self.courses

async def main():
    scraper = AdvancedNYCUScraper()
    await scraper.scrape_with_http()

if __name__ == "__main__":
    asyncio.run(main())
