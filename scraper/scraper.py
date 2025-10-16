"""
Scraper for NYCU timetable course information.

This module uses Playwright to interact with the official timetable
search form and discover all course numbers for each semester.  It
then fetches each course's detailed syllabus page using aiohttp and
parses the HTML into structured data.  Parsed courses are written to
JSON and CSV files in the `data/` directory.

NOTE: The functions in this file are intentionally left incomplete in
places.  They provide a starting point for development and illustrate
how to structure asynchronous scraping.  See the comments marked
"TODO" for guidance on what needs to be implemented.
"""

import asyncio
import json
import os
import csv
from dataclasses import asdict
from pathlib import Path
from typing import List, Dict, Any, Optional

import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from config import DEFAULT_CONFIG, ScraperConfig


class Course:
    """Simple data model for a course."""

    def __init__(self, acy: int, sem: int, crs_no: str, data: Dict[str, Any]):
        self.acy = acy
        self.sem = sem
        self.crs_no = crs_no
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "acy": self.acy,
            "sem": self.sem,
            "crs_no": self.crs_no,
            **self.data,
        }


async def discover_course_numbers(config: ScraperConfig) -> Dict[tuple[int, int], List[str]]:
    """
    Use Playwright to iterate through each semester and discover all
    course numbers.  Returns a mapping from (acy, sem) to a list of
    course numbers (as strings).

    Playwright is required here because the search interface on
    timetable.nycu.edu.tw relies on dynamic form submission.  The
    implementation below sketches the steps but omits the details of
    interacting with select boxes and table elements.
    """
    course_map: Dict[tuple[int, int], List[str]] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for year in range(config.start_year, config.end_year + 1):
            for sem in config.semesters:
                semester_key = (year, sem)
                course_map[semester_key] = []
                # TODO: Navigate to the search page, select the year and
                # semester, and extract all course numbers from the
                # resulting table.  Append each course number string
                # to course_map[semester_key].
                # For example:
                # await page.goto("https://timetable.nycu.edu.tw/")
                # await page.select_option("select#Acy", str(year))
                # await page.select_option("select#Sem", str(sem))
                # await page.click("button#search")
                # await page.wait_for_selector("table#CourseList")
                # numbers = await page.eval_on_selector_all(
                #     "table#CourseList tr td:nth-child(1)", "els => els.map(el => el.textContent.trim())"
                # )
                # course_map[semester_key].extend(numbers)
                pass
        await browser.close()
    return course_map


async def fetch_course_page(session: aiohttp.ClientSession, acy: int, sem: int, crs_no: str, config: ScraperConfig) -> Optional[Course]:
    """
    Fetch a single course syllabus page and parse it into a Course.
    Returns None if the page cannot be fetched or parsed.
    """
    url = (
        "https://timetable.nycu.edu.tw/?r=main%2Fcrsoutline"
        f"&Acy={acy}&Sem={sem}&CrsNo={crs_no}"
    )
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
    except Exception:
        return None

    soup = BeautifulSoup(html, "html.parser")
    # TODO: Parse the HTML to extract course fields.  See the
    # timetable site for the exact structure.  Example fields might
    # include:
    #   title = soup.find("h2", class_="course-title").get_text(strip=True)
    #   teacher = soup.find(...)
    #   credits = ...
    #   description = ...
    data: Dict[str, Any] = {}
    try:
        title_elem = soup.find("h2")
        if title_elem:
            data["name"] = title_elem.get_text(strip=True)
        # Additional parsing should populate data with keys like
        # "permanent_crs_no", "credits", "required", "teacher",
        # "dept", "day_codes", "time_codes", "classroom_codes",
        # "description", "evaluation", etc.
    except Exception:
        pass
    return Course(acy, sem, crs_no, data)


async def scrape_all(config: ScraperConfig = DEFAULT_CONFIG) -> List[Course]:
    """
    Coordinate the discovery and downloading of all courses across
    semesters.  Returns a list of Course objects.
    """
    courses: List[Course] = []
    # Discover course numbers first
    course_map = await discover_course_numbers(config)

    connector = aiohttp.TCPConnector(limit=config.max_concurrent_requests)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for (acy, sem), numbers in course_map.items():
            for crs_no in numbers:
                tasks.append(
                    fetch_course_page(session, acy, sem, crs_no, config)
                )
        for coro in asyncio.as_completed(tasks):
            course = await coro
            if course is not None:
                courses.append(course)
            await asyncio.sleep(config.request_delay)
    return courses


def write_output(courses: List[Course], output_dir: str = "data") -> None:
    """
    Write the scraped courses to JSON and CSV files.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    json_path = Path(output_dir) / "courses.json"
    csv_path = Path(output_dir) / "courses.csv"
    # JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in courses], f, ensure_ascii=False, indent=2)
    # CSV
    if courses:
        keys = list(courses[0].to_dict().keys())
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for c in courses:
                writer.writerow(c.to_dict())


def main() -> None:
    """
    Entry point for the scraper when run from the command line.
    """
    config = DEFAULT_CONFIG
    courses: List[Course] = asyncio.run(scrape_all(config))
    write_output(courses)
    print(f"Scraped {len(courses)} courses.")


if __name__ == "__main__":
    main()