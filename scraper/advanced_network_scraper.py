#!/usr/bin/env python3
"""
Advanced NYCU Course Scraper with Network Request Monitoring
Captures actual API calls made by the NYCU website
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page, Route

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"
OUTPUT_FILE = Path("data/courses_real.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

class NetworkMonitoringScraper:
    def __init__(self):
        self.captured_requests = []
        self.captured_responses = []
        self.courses = []

    async def capture_request_handler(self, route: Route):
        """Intercept and log all requests"""
        request = route.request
        url = request.url
        method = request.method
        
        # Log all API/XHR requests
        if 'api' in url.lower() or 'ajax' in url.lower() or request.resource_type in ['xhr', 'fetch']:
            logger.info(f"📡 Request: {method} {url}")
            self.captured_requests.append({
                'method': method,
                'url': url,
                'headers': dict(request.headers)
            })
        
        await route.continue_()

    async def capture_response_handler(self, route: Route):
        """Intercept and log all responses"""
        response = await route.response()
        
        if response and response.request.resource_type in ['xhr', 'fetch']:
            url = response.url
            status = response.status
            try:
                text = await response.text()
                if text and len(text) < 10000:  # Only log smaller responses
                    logger.info(f"📥 Response: {status} {url} ({len(text)} bytes)")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(text)
                        self.captured_responses.append({
                            'url': url,
                            'status': status,
                            'data': data
                        })
                        logger.info(f"   Content: {json.dumps(data)[:200]}")
                    except:
                        pass
            except:
                pass
        
        await route.continue_()

    async def scrape(self):
        """Scrape NYCU timetable with network monitoring"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set up request/response handlers
            await page.route('**/*', self.capture_request_handler)
            await page.route('**/*', self.capture_response_handler)
            
            logger.info("🚀 Loading NYCU timetable...")
            await page.goto(BASE_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            logger.info("\n=== 🔍 ANALYZING PAGE STRUCTURE ===")
            
            # Get all form elements
            selects = await page.query_selector_all("select")
            logger.info(f"Found {len(selects)} select elements")
            
            # Look for the main search/query mechanism
            scripts = await page.query_selector_all("script")
            logger.info(f"Found {len(scripts)} scripts")
            
            # Try to find if there's a specific function to call
            try:
                # Look for window functions that might load courses
                js_functions = await page.evaluate("""
                    () => {
                        const functions = [];
                        for (let key in window) {
                            if (typeof window[key] === 'function') {
                                if (key.toLowerCase().includes('search') || 
                                    key.toLowerCase().includes('course') ||
                                    key.toLowerCase().includes('load') ||
                                    key.toLowerCase().includes('query')) {
                                    functions.push(key);
                                }
                            }
                        }
                        return functions;
                    }
                """)
                logger.info(f"Found JS functions: {js_functions}")
            except Exception as e:
                logger.warning(f"Could not enumerate window functions: {e}")
            
            # Try to find all event handlers on the page
            logger.info("\n=== 🎯 ATTEMPTING FORM SUBMISSION ===")
            
            # Get semester selector
            sem_select = await page.query_selector("select[name='fAcySem']")
            if sem_select:
                logger.info("Found semester selector")
                
                # Try each year-semester combination
                for year_sem in ['1141', '1132', '1131']:
                    logger.info(f"\n📍 Testing year/semester: {year_sem}")
                    
                    # Select the semester
                    await page.select_option("select[name='fAcySem']", year_sem)
                    await asyncio.sleep(1)
                    
                    # Look for any submit buttons or search triggers
                    # Try finding hidden buttons or calling search functions
                    try:
                        # Common patterns for triggering search
                        search_triggers = [
                            "doSearch()",
                            "search()",
                            "query()",
                            "loadCourses()",
                            "getCourses()",
                            "fetchCourses()"
                        ]
                        
                        for trigger in search_triggers:
                            try:
                                result = await page.evaluate(f"() => {{ if (typeof {trigger.split('(')[0]} === 'function') {{ {trigger}; return true; }} return false; }}")
                                if result:
                                    logger.info(f"✅ Triggered: {trigger}")
                                    await asyncio.sleep(1)
                                    break
                            except:
                                pass
                    except Exception as e:
                        logger.warning(f"Could not trigger functions: {e}")
                    
                    # Check for visible course data
                    table_rows = await page.query_selector_all("table tbody tr")
                    logger.info(f"   Found {len(table_rows)} table rows")
                    
                    if len(table_rows) > 5:
                        logger.info("   ✅ Courses appear to be loaded!")
            
            logger.info("\n=== 📊 CAPTURED NETWORK ACTIVITY ===")
            logger.info(f"Total captured requests: {len(self.captured_requests)}")
            logger.info(f"Total captured responses: {len(self.captured_responses)}")
            
            if self.captured_requests:
                logger.info("\nCaptured Requests:")
                for req in self.captured_requests[:10]:
                    logger.info(f"  {req['method']} {req['url']}")
            
            if self.captured_responses:
                logger.info("\nCaptured Responses:")
                for resp in self.captured_responses[:10]:
                    logger.info(f"  {resp['status']} {resp['url']}")
                    if isinstance(resp['data'], list):
                        logger.info(f"    Data type: Array with {len(resp['data'])} items")
                    elif isinstance(resp['data'], dict):
                        logger.info(f"    Data keys: {list(resp['data'].keys())}")
            
            # Save all captured data
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'requests': self.captured_requests,
                'responses': self.captured_responses
            }
            
            with open("data/network_capture.json", "w") as f:
                json.dump(output_data, f, indent=2)
            logger.info("\n✅ Network capture saved to data/network_capture.json")
            
            await browser.close()

async def main():
    scraper = NetworkMonitoringScraper()
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())
