#!/usr/bin/env python3
"""
NYCU Real Course Data Scraper
Uses discovered JSON API endpoints to fetch actual course data
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"
OUTPUT_FILE = Path("data/courses_real_data.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

class NYCURealScraper:
    def __init__(self):
        self.courses = []

    async def fetch_json_api(self, page, endpoint):
        """Fetch data from NYCU API endpoint"""
        try:
            response = await page.evaluate(f"""
                async () => {{
                    try {{
                        const resp = await fetch('{endpoint}', {{method: 'POST'}});
                        return await resp.text();
                    }} catch (e) {{
                        return 'ERROR: ' + e.message;
                    }}
                }}
            """)
            return response
        except Exception as e:
            logger.warning(f"Error fetching {endpoint}: {e}")
            return None

    async def scrape(self):
        """Main scraping function"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            logger.info("=" * 80)
            logger.info("🚀 NYCU Real Course Data Scraper")
            logger.info("=" * 80)
            
            logger.info("\n📍 Loading NYCU timetable...")
            try:
                await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=5000)
            except:
                pass
            await asyncio.sleep(2)
            
            # Fetch available semesters
            logger.info("\n📋 Fetching available semesters...")
            sem_response = await self.fetch_json_api(page, "?r=main/get_acysem")
            
            if sem_response:
                try:
                    semesters = json.loads(sem_response)
                    logger.info(f"✅ Found {len(semesters)} semesters")
                    
                    # Extract 110-114 semesters
                    target_sems = []
                    for sem in semesters:
                        code = sem.get('T', '')
                        if code and any(str(y) in code for y in range(110, 115)):
                            target_sems.append(code)
                            logger.info(f"   Target: {code}")
                    
                    logger.info(f"\n🎯 Found {len(target_sems)} target semesters (110-114)")
                    
                    # Scrape each semester
                    all_courses = []
                    for idx, sem_code in enumerate(target_sems[:10], 1):
                        logger.info(f"\n[{idx}/{min(10, len(target_sems))}] Scraping semester: {sem_code}")
                        
                        # Select semester
                        try:
                            await page.select_option("select[name='fAcySem']", sem_code)
                            await asyncio.sleep(1)
                        except:
                            logger.warning(f"  ⚠️ Could not select semester {sem_code}")
                            continue
                        
                        # Fetch course data - try multiple endpoints
                        course_data = None
                        
                        # Try getViewHtmlContents
                        logger.info(f"  📥 Fetching course data...")
                        html_response = await self.fetch_json_api(page, "?r=main/getViewHtmlContents")
                        
                        if html_response and not html_response.startswith('ERROR'):
                            # Try to parse as JSON first
                            try:
                                course_data = json.loads(html_response)
                                if isinstance(course_data, dict):
                                    # Check if it has course data in any field
                                    for key, value in course_data.items():
                                        if isinstance(value, list) and len(value) > 0:
                                            logger.info(f"  ✅ Got data from key '{key}': {len(value)} items")
                                            all_courses.extend(value)
                                            break
                                elif isinstance(course_data, list):
                                    logger.info(f"  ✅ Got {len(course_data)} course records")
                                    all_courses.extend(course_data)
                            except json.JSONDecodeError:
                                # Not JSON, might be HTML table
                                if len(html_response) > 100:
                                    logger.info(f"  ✅ Got HTML response ({len(html_response)} chars)")
                                    all_courses.append({
                                        'semester': sem_code,
                                        'html_length': len(html_response),
                                        'preview': html_response[:200]
                                    })
                    
                    logger.info(f"\n{'='*80}")
                    logger.info(f"📊 Summary: Collected {len(all_courses)} course records")
                    logger.info(f"{'='*80}")
                    
                    # Save data
                    output_data = {
                        'timestamp': datetime.now().isoformat(),
                        'scraper': 'NYCU Real Data Scraper',
                        'years': '110-114',
                        'semesters_count': len(target_sems),
                        'courses_count': len(all_courses),
                        'data': all_courses[:100]  # Save first 100 for inspection
                    }
                    
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"\n✅ Data saved to: {OUTPUT_FILE}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse semester data: {e}")
                    logger.info(f"Raw response (first 1000 chars): {sem_response[:1000]}")
            else:
                logger.error("Failed to fetch semesters")
            
            await browser.close()

async def main():
    scraper = NYCURealScraper()
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())
