#!/usr/bin/env python3
"""
Monitor NYCU website network activity to find API endpoints
"""

import asyncio
import json
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://timetable.nycu.edu.tw/"

async def monitor():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Monitor all network responses
        responses = []
        requests_log = []
        
        def on_response(response):
            url = response.url
            status = response.status
            req_type = response.request.resource_type
            
            # Log XHR/API requests
            if req_type in ['xhr', 'fetch']:
                logger.info(f"📥 {status} {req_type.upper()}: {url}")
                responses.append({
                    'url': url,
                    'status': status,
                    'type': req_type
                })
        
        def on_request(request):
            url = request.url
            method = request.method
            req_type = request.resource_type
            
            # Log XHR/API requests
            if req_type in ['xhr', 'fetch']:
                logger.info(f"📡 {method} {req_type.upper()}: {url}")
                requests_log.append({
                    'url': url,
                    'method': method,
                    'type': req_type
                })
        
        page.on("response", on_response)
        page.on("request", on_request)
        
        logger.info("🚀 Loading NYCU timetable (with 5s timeout)...")
        try:
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=5000)
        except:
            logger.info("⏱️ Initial load timeout (expected)")
        
        await asyncio.sleep(2)
        
        logger.info("\n🔍 Interacting with form...")
        
        # Try to select different semesters to trigger requests
        try:
            sem_options = await page.query_selector_all("select[name='fAcySem'] option")
            logger.info(f"Found {len(sem_options)} semester options")
            
            if sem_options:
                # Try selecting first semester
                await page.select_option("select[name='fAcySem']", "1141")
                logger.info("Selected semester 1141")
                await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"Error selecting semester: {e}")
        
        logger.info(f"\n=== 📊 CAPTURED ACTIVITY ===")
        logger.info(f"Total requests: {len(requests_log)}")
        logger.info(f"Total responses: {len(responses)}")
        
        if requests_log:
            logger.info("\n📡 Requests:")
            for req in requests_log[:20]:
                logger.info(f"  {req['method']} {req['url']}")
        
        if responses:
            logger.info("\n📥 Responses:")
            for resp in responses[:20]:
                logger.info(f"  {resp['status']} {resp['url']}")
        
        # Save for analysis
        with open("data/network_log.json", "w") as f:
            json.dump({
                'requests': requests_log,
                'responses': responses
            }, f, indent=2)
        logger.info("\n✅ Saved to data/network_log.json")
        
        await browser.close()

asyncio.run(monitor())
