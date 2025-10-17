#!/usr/bin/env python3
"""
NYCU Real Course Data Scraper - Direct API Approach
Fetches real course data from https://timetable.nycu.edu.tw/ for years 110-114
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"
OUTPUT_FILE = Path("data/real_courses_scraped.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

class NYCURealCourseScraper:
    def __init__(self):
        self.all_courses = []
        self.semester_map = {
            '1141': 'Year 114, Fall',
            '113X': 'Year 113, Summer',
            '1132': 'Year 113, Spring',
            '1131': 'Year 113, Fall',
            '112X': 'Year 112, Summer',
            '1122': 'Year 112, Spring',
            '1121': 'Year 112, Fall',
            '111X': 'Year 111, Summer',
            '1112': 'Year 111, Spring',
            '1111': 'Year 111, Fall',
            '110X': 'Year 110, Summer',
            '1102': 'Year 110, Spring',
            '1101': 'Year 110, Fall',
        }

    def parse_course_from_row(self, cells, semester_code):
        """Parse a course row from HTML table"""
        try:
            # Typical NYCU course table has: number, name, credits, type, teacher, time, room, etc.
            if len(cells) < 4:
                return None

            course = {
                'semester_code': semester_code,
                'semester_name': self.semester_map.get(semester_code, semester_code),
            }

            # Extract based on common NYCU table structure
            cell_texts = [cell.strip() for cell in cells]
            
            # Try to identify course fields (order may vary)
            if len(cell_texts) >= 2:
                # Often: number, name, credits, type, teacher, time, room
                course['crs_no'] = cell_texts[0] if cell_texts[0] else 'N/A'
                course['name'] = cell_texts[1] if cell_texts[1] else 'N/A'
                
                # Additional fields if available
                if len(cell_texts) >= 3:
                    course['credits'] = cell_texts[2]
                if len(cell_texts) >= 4:
                    course['type'] = cell_texts[3]
                if len(cell_texts) >= 5:
                    course['teacher'] = cell_texts[4]
                if len(cell_texts) >= 6:
                    course['time'] = cell_texts[5]
                if len(cell_texts) >= 7:
                    course['classroom'] = cell_texts[6]

                return course
        except Exception as e:
            logger.warning(f"Error parsing course row: {e}")
            return None

    async def scrape_semester(self, page, semester_code):
        """Scrape course data for a specific semester"""
        logger.info(f"\n📍 Scraping semester: {semester_code} ({self.semester_map.get(semester_code, 'Unknown')})")
        
        try:
            # Select the semester in the dropdown
            await page.select_option("select[name='fAcySem']", semester_code)
            await asyncio.sleep(1)
            
            # Fetch the course data
            logger.info("  📥 Fetching course data...")
            html_response = await page.evaluate("""
                async () => {
                    try {
                        const resp = await fetch('?r=main/getViewHtmlContents', {method: 'POST'});
                        return await resp.text();
                    } catch (e) {
                        return '';
                    }
                }
            """)
            
            if not html_response:
                logger.warning("  ❌ No HTML response")
                return []
            
            # Parse HTML to extract courses
            soup = BeautifulSoup(html_response, 'html.parser')
            courses_found = []
            
            # Look for tables with course data
            tables = soup.find_all('table')
            logger.info(f"  Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                logger.info(f"  Table {table_idx + 1}: {len(rows)} rows")
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Skip header rows
                        if any(keyword in cell_texts[0].lower() for keyword in ['course', '課程', '課號']):
                            continue
                        
                        # Try to parse as course
                        course = self.parse_course_from_row(cell_texts, semester_code)
                        if course and course['crs_no'] != 'N/A':
                            courses_found.append(course)
            
            logger.info(f"  ✅ Found {len(courses_found)} courses")
            return courses_found
        
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            return []

    async def scrape_all(self):
        """Scrape all course data for years 110-114"""
        logger.info("=" * 80)
        logger.info("🚀 NYCU Real Course Data Scraper - Direct API Approach")
        logger.info("=" * 80)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            try:
                logger.info("\n📍 Loading NYCU timetable...")
                await page.goto(BASE_URL, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                
                # Get available semesters
                logger.info("\n📋 Fetching available semesters...")
                sem_response = await page.evaluate("""
                    async () => {
                        const resp = await fetch('?r=main/get_acysem', {method: 'POST'});
                        return await resp.text();
                    }
                """)
                
                try:
                    semesters = json.loads(sem_response)
                    available_sems = [s.get('T') for s in semesters if s.get('T')]
                    logger.info(f"✅ Available semesters: {len(available_sems)}")
                except:
                    available_sems = list(self.semester_map.keys())
                    logger.warning("Using predefined semester list")
                
                # Filter to target semesters
                target_sems = [s for s in available_sems if s in self.semester_map]
                logger.info(f"✅ Target semesters (110-114): {len(target_sems)}")
                for sem in target_sems:
                    logger.info(f"   - {sem}: {self.semester_map[sem]}")
                
                # Scrape each semester
                logger.info("\n🎯 Starting course scraping...")
                total_courses = 0
                
                for idx, semester_code in enumerate(target_sems, 1):
                    logger.info(f"\n[{idx}/{len(target_sems)}]")
                    courses = await self.scrape_semester(page, semester_code)
                    self.all_courses.extend(courses)
                    total_courses += len(courses)
                    
                    # Small delay between requests
                    await asyncio.sleep(1)
                
                logger.info(f"\n{'='*80}")
                logger.info(f"📊 Scraping Complete!")
                logger.info(f"{'='*80}")
                logger.info(f"Total courses scraped: {total_courses}")
                logger.info(f"Semesters processed: {len(target_sems)}")
                
                # Save results
                output_data = {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'NYCU Timetable System - Direct API Scraping',
                    'years': '110-114',
                    'semesters_count': len(target_sems),
                    'total_courses': len(self.all_courses),
                    'courses': self.all_courses[:100] if len(self.all_courses) > 100 else self.all_courses
                }
                
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"\n✅ Data saved to: {OUTPUT_FILE}")
                logger.info(f"📦 File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
                
                return self.all_courses
            
            finally:
                await browser.close()

async def main():
    scraper = NYCURealCourseScraper()
    courses = await scraper.scrape_all()
    return courses

if __name__ == "__main__":
    asyncio.run(main())
