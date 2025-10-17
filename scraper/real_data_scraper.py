#!/usr/bin/env python3
"""
NYCU Real Course Scraper - Using discovered API endpoints
Fetches actual course data from 110-114 academic years
"""

import asyncio
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"
OUTPUT_FILE = Path("data/courses_real_data.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

class RealDataScraper:
    def __init__(self):
        self.courses = []
        self.semester_map = {}

    async def get_semesters(self, page):
        """Get available semesters"""
        logger.info("📋 Fetching available semesters...")
        
        try:
            # Get semester response
            sem_response = await page.evaluate("""
                async () => {
                    const response = await fetch('?r=main/get_acysem', {method: 'POST'});
                    return await response.text();
                }
            """)
            
            # Parse the semester data
            logger.info(f"Raw semester response (first 500 chars): {sem_response[:500]}")
            
            # Extract semester options from HTML
            soup = BeautifulSoup(sem_response, 'html.parser')
            options = soup.find_all('option')
            
            semesters = {}
            for opt in options:
                if opt.get('value'):
                    semesters[opt['value']] = opt.text.strip()
            
            logger.info(f"✅ Found {len(semesters)} semesters:")
            for key, val in list(semesters.items())[:20]:
                logger.info(f"   {key}: {val}")
            
            return semesters
            
        except Exception as e:
            logger.error(f"Error fetching semesters: {e}")
            return {}

    async def get_courses_for_semester(self, page, semester_code):
        """Fetch courses for a specific semester"""
        logger.info(f"\n🎯 Fetching courses for semester: {semester_code}")
        
        try:
            # Select the semester
            await page.select_option("select[name='fAcySem']", semester_code)
            await asyncio.sleep(1)
            
            # Get the HTML content (course table)
            html_response = await page.evaluate("""
                async () => {
                    const response = await fetch('?r=main/getViewHtmlContents', {method: 'POST'});
                    return await response.text();
                }
            """)
            
            logger.info(f"Got HTML response: {len(html_response)} characters")
            
            # Parse HTML to extract courses
            soup = BeautifulSoup(html_response, 'html.parser')
            
            # Look for course information in tables
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            courses_found = []
            
            # Try to find course rows
            for table in tables:
                rows = table.find_all('tr')
                logger.info(f"Table has {len(rows)} rows")
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        # Try to extract course info
                        cell_text = [c.text.strip() for c in cells]
                        if any(keyword in str(cell_text).lower() for keyword in ['course', 'class', '課']):
                            logger.info(f"Found potential course row: {cell_text[:3]}")
                            courses_found.append({
                                'cells': cell_text,
                                'semester': semester_code
                            })
            
            logger.info(f"✅ Found {len(courses_found)} potential course entries")
            return courses_found
            
        except Exception as e:
            logger.error(f"Error fetching courses for {semester_code}: {e}")
            return []

    async def scrape(self):
        """Main scraping function"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            logger.info("🚀 Loading NYCU timetable...")
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=5000)
            await asyncio.sleep(2)
            
            # Get semesters
            semesters = await self.get_semesters(page)
            
            if not semesters:
                logger.warning("No semesters found!")
                await browser.close()
                return
            
            # Target semesters: 110-114
            target_semesters = []
            for year in range(110, 115):
                for sem in ['1', '2']:  # Fall (1), Spring (2)
                    target_code = f"{year}{sem}"
                    # Find matching semester code
                    for code, name in semesters.items():
                        if str(year) in name and name.strip():
                            if 'Fall' in name and sem == '1':
                                target_semesters.append(code)
                            elif 'Spring' in name and sem == '2':
                                target_semesters.append(code)
            
            logger.info(f"\n📍 Target semesters to scrape: {target_semesters[:10]}")
            
            # Scrape each semester
            all_courses_data = []
            for sem_code in target_semesters[:5]:  # Start with first 5
                courses = await self.get_courses_for_semester(page, sem_code)
                all_courses_data.extend(courses)
            
            # Save results
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'total_entries': len(all_courses_data),
                'data': all_courses_data,
                'semesters_config': semesters
            }
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"\n✅ Saved {len(all_courses_data)} course entries to {OUTPUT_FILE}")
            
            await browser.close()

async def main():
    scraper = RealDataScraper()
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())
