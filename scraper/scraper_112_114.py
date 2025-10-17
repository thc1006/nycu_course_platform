#!/usr/bin/env python3
"""
Quick scraper for years 112-114 only
"""

import json
import re
import requests
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/real_courses_nycu")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
COURSES_FILE = OUTPUT_DIR / "courses_112_114.json"

SEMESTERS = [
    (112, 1),  (112, 2),
    (113, 1),  (113, 2),
    (114, 1),
]

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

BASE_URL = "https://timetable.nycu.edu.tw"


def parse_time(tc: str) -> str:
    """Extract and join time slots"""
    pattern = '[MTWRFSU][1-9yznabcd]+'
    times = []
    for item in tc.split(','):
        found = re.findall(pattern, item.split('-')[0])
        for t in found:
            for i in range(len(t) - 1):
                times.append(t[0] + t[i + 1])
    return ",".join(times)


def parse_classroom(tc: str) -> str:
    """Extract and join classrooms"""
    rooms = []
    for item in tc.split(','):
        try:
            room = item.split('-')[1]
            if room:
                rooms.append(room)
        except IndexError:
            pass
    return ",".join(rooms)


def get_cos(year: int, sem: int, dep: str) -> dict:
    """Fetch courses for department"""
    try:
        r = requests.post(
            f"{BASE_URL}/?r=main/get_cos_list",
            headers=HEADERS,
            verify=False,
            data={
                "m_acy": year,
                "m_sem": sem,
                "m_acyend": year,
                "m_semend": sem,
                "m_dep_uid": dep,
                "m_group": "**",
                "m_grade": "**",
                "m_class": "**",
                "m_option": "**",
                "m_crsname": "**",
                "m_teaname": "**",
                "m_cos_id": "**",
                "m_cos_code": "**",
                "m_crstime": "**",
                "m_crsoutline": "**",
                "m_costype": "**",
                "m_selcampus": "**"
            },
            timeout=15
        )
        return json.loads(r.text) if r.status_code == 200 else {}
    except Exception as e:
        logger.debug(f"Error fetching {dep}: {e}")
        return {}


def scrape_semester(year: int, sem: int) -> list:
    """Scrape all courses for a semester"""
    courses = []
    acysem = str(year) + str(sem)
    logger.info(f"\n{'='*60}")
    logger.info(f"📚 Scraping Year {year}, Semester {sem}")
    logger.info(f"{'='*60}")

    try:
        # Get types
        types_resp = requests.get(f'{BASE_URL}/?r=main/get_type', headers=HEADERS, verify=False, timeout=15)
        types = types_resp.json()
        logger.info(f"Found {len(types)} types")

        dept_count = 0
        for type_item in types:
            ftype = type_item["uid"]

            # Get categories
            try:
                cat_resp = requests.post(
                    f'{BASE_URL}/?r=main/get_category',
                    data={'ftype': ftype, 'flang': 'zh-tw', 'acysem': acysem, 'acysemend': acysem},
                    headers=HEADERS, verify=False, timeout=15
                )
                categories = cat_resp.json()
            except:
                continue

            for fcategory in categories.keys():
                try:
                    col_resp = requests.post(
                        f'{BASE_URL}/?r=main/get_college',
                        data={'fcategory': fcategory, 'ftype': ftype, 'flang': 'zh-tw', 'acysem': acysem, 'acysemend': acysem},
                        headers=HEADERS, verify=False, timeout=15
                    )
                    colleges = col_resp.json()
                except:
                    colleges = {}

                if colleges:
                    for fcollege in colleges.keys():
                        try:
                            dep_resp = requests.post(
                                f'{BASE_URL}/?r=main/get_dep',
                                data={'fcollege': fcollege, 'fcategory': fcategory, 'ftype': ftype, 'flang': 'zh-tw', 'acysem': acysem, 'acysemend': acysem},
                                headers=HEADERS, verify=False, timeout=15
                            )
                            deps = dep_resp.json()
                        except:
                            deps = {}

                        for fdep in deps.keys():
                            dept_count += 1
                            raw_data = get_cos(year, sem, fdep)

                            # Extract courses
                            for dep_val in raw_data:
                                lang_data = raw_data[dep_val].get("language", {})

                                for dep_key in raw_data[dep_val]:
                                    if not re.match("^[1-2]+$", dep_key):
                                        continue

                                    for cos_id in raw_data[dep_val][dep_key]:
                                        try:
                                            cos = raw_data[dep_val][dep_key][cos_id]
                                            name = cos.get("cos_cname", "").replace("(英文授課)", "").replace("(英文班)", "")

                                            course = {
                                                "acy": year,
                                                "sem": sem,
                                                "crs_no": cos.get("cos_id", ""),
                                                "name": name,
                                                "teacher": cos.get("teacher", ""),
                                                "credits": float(cos.get("cos_credit", 0)),
                                                "time": parse_time(cos.get("cos_time", "")),
                                                "classroom": parse_classroom(cos.get("cos_time", "")),
                                            }

                                            if course["crs_no"]:  # Only add if has course number
                                                courses.append(course)
                                        except Exception as e:
                                            logger.debug(f"Error: {e}")

            logger.info(f"  Processed {dept_count} departments - {len(courses)} courses")

    except Exception as e:
        logger.error(f"Error: {e}")

    logger.info(f"✅ Found {len(courses)} courses")
    return courses


def main():
    all_courses = []

    logger.info("🚀 NYCU Scraper - Years 112-114 (5 semesters)")

    for year, sem in SEMESTERS:
        courses = scrape_semester(year, sem)
        all_courses.extend(courses)

    # Save
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "years": "112-114",
        "semesters_count": len(SEMESTERS),
        "total_courses": len(all_courses),
        "courses": all_courses
    }

    with open(COURSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ COMPLETE!")
    logger.info(f"Total: {len(all_courses)} courses")
    logger.info(f"Saved to: {COURSES_FILE}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
