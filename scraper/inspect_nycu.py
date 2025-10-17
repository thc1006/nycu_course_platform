#!/usr/bin/env python3
"""Inspect NYCU timetable HTML structure"""

import asyncio
from playwright.async_api import async_playwright

async def inspect_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to NYCU timetable
        url = "https://timetable.nycu.edu.tw/?r=main/crsearch&Acy=114&Sem=1"
        print(f"🔍 Navigating to: {url}")
        
        await page.goto(url, wait_until="networkidle", timeout=15000)
        
        # Wait a bit for JS to render
        await asyncio.sleep(2)
        
        # Get the full HTML
        html = await page.content()
        
        # Save to file for inspection
        with open("/tmp/nycu_page.html", "w") as f:
            f.write(html)
        
        print("✅ Saved HTML to /tmp/nycu_page.html")
        
        # Print first 5000 chars
        print("\n=== HTML CONTENT (first 5000 chars) ===")
        print(html[:5000])
        
        # Look for specific elements
        print("\n=== LOOKING FOR ELEMENTS ===")
        
        # Try to find all links
        links = await page.query_selector_all("a")
        print(f"Total <a> tags: {len(links)}")
        
        if links:
            print("\nFirst 5 links:")
            for i, link in enumerate(links[:5]):
                href = await link.get_attribute("href")
                text = await link.text_content()
                print(f"  {i}: href='{href}' text='{text}'")
        
        # Look for course-related elements
        tables = await page.query_selector_all("table")
        print(f"\nTotal <table> tags: {len(tables)}")
        
        # Look for divs with specific classes
        divs = await page.query_selector_all("div[class*='course']")
        print(f"Divs with 'course' in class: {len(divs)}")
        
        # Get body content
        body = await page.query_selector("body")
        if body:
            body_text = await body.text_content()
            print(f"\n=== BODY TEXT (first 2000 chars) ===")
            print(body_text[:2000])
        
        await browser.close()

asyncio.run(inspect_page())
