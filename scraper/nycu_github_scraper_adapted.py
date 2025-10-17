#!/usr/bin/env python3
"""
NYCU Course Data Scraper - Adapted from GitHub Huskyee/NYCU_Timetable
Fetches real NYCU course data for years 110-114 (all 13 semesters)
Converts to platform schema for database import
"""

import json
import re
import requests
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Output paths
OUTPUT_DIR = Path("data/real_courses_nycu")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
COURSES_FILE = OUTPUT_DIR / "courses_all_semesters.json"
RAW_DATA_FILE = OUTPUT_DIR / "raw_data_all_semesters.json"

# Semesters to scrape (110-114 years, 13 total semesters)
SEMESTERS = [
    (110, 1),  # Year 110, Fall 2021
    (110, 2),  # Year 110, Spring 2021
    (111, 1),  # Year 111, Fall 2022
    (111, 2),  # Year 111, Spring 2022
    (112, 1),  # Year 112, Fall 2023
    (112, 2),  # Year 112, Spring 2023
    (113, 1),  # Year 113, Fall 2024
    (113, 2),  # Year 113, Spring 2024
    (114, 1),  # Year 114, Fall 2025
]

# HTTP Headers
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
}

BASE_URL = "https://timetable.nycu.edu.tw"


def parse_time(tc: str) -> List[str]:
    """Extract time portion from time-classroom string"""
    pattern = '[MTWRFSU][1-9yznabcd]+'
    tc_list = tc.split(',')
    time_list = []
    for item in tc_list:
        time = re.findall(pattern, item.split('-')[0])
        for t in time:
            for i in range(len(t) - 1):
                time_list.append(t[0] + t[i + 1])
    return time_list


def parse_classroom(tc: str) -> List[str]:
    """Extract classroom portion from time-classroom string"""
    tc_list = tc.split(',')
    classroom_list = []
    for item in tc_list:
        try:
            classroom = item.split('-')[1]
        except IndexError:
            classroom = ''
        classroom_list.append(classroom)
    return classroom_list


def get_type():
    """Fetch course types"""
    try:
        res = requests.get(f'{BASE_URL}/?r=main/get_type', headers=HEADERS, verify=False, timeout=15)
        return res.json()
    except Exception as e:
        logger.error(f"Error fetching types: {e}")
        return []


def get_category(ftype: str, flang: str, acysem: str) -> Dict:
    """Fetch categories for a type"""
    try:
        res = requests.post(f'{BASE_URL}/?r=main/get_category', data={
            'ftype': ftype,
            'flang': flang,
            'acysem': acysem,
            'acysemend': acysem
        }, headers=HEADERS, verify=False, timeout=15)
        return res.json()
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return {}


def get_college(fcategory: str, ftype: str, flang: str, acysem: str) -> Dict:
    """Fetch colleges for a category"""
    try:
        res = requests.post(f'{BASE_URL}/?r=main/get_college', data={
            'fcategory': fcategory,
            'ftype': ftype,
            'flang': flang,
            'acysem': acysem,
            'acysemend': acysem
        }, headers=HEADERS, verify=False, timeout=15)
        return res.json()
    except Exception as e:
        logger.error(f"Error fetching colleges: {e}")
        return {}


def get_dep(fcollege: str, fcategory: str, ftype: str, flang: str, acysem: str) -> Dict:
    """Fetch departments for a college"""
    try:
        res = requests.post(f'{BASE_URL}/?r=main/get_dep', data={
            'fcollege': fcollege,
            'fcategory': fcategory,
            'ftype': ftype,
            'flang': flang,
            'acysem': acysem,
            'acysemend': acysem
        }, headers=HEADERS, verify=False, timeout=15)
        return res.json()
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        return {}


def get_cos(year: int, semester: int, dep: str) -> Dict:
    """Fetch courses for a department"""
    url = f"{BASE_URL}/?r=main/get_cos_list"
    data = {
        "m_acy": year,
        "m_sem": semester,
        "m_acyend": year,
        "m_semend": semester,
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
    }

    try:
        r = requests.post(url, headers=HEADERS, verify=False, data=data, timeout=15)
        if r.status_code != 200:
            logger.warning(f"Status code {r.status_code} for department {dep}")
            return {}
        return json.loads(r.text)
    except Exception as e:
        logger.error(f"Error fetching courses for department {dep}: {e}")
        return {}


def extract_courses_from_raw(year: int, semester: int, raw_data: Dict) -> List[Dict]:
    """Extract courses from raw API response and convert to platform schema"""
    courses = []

    try:
        # raw_data structure: {dept_id: {dept_id: {dep_id, dep_cname, ..., "2": {cos_id: course_data, ...}, brief: ..., language: ...}}}
        for dept_id_outer in raw_data:
            dept_data = raw_data[dept_id_outer]

            # The inner structure has dept_id as a key
            for dept_id_inner in dept_data:
                if not isinstance(dept_data[dept_id_inner], dict):
                    continue

                inner_data = dept_data[dept_id_inner]
                language_map = inner_data.get("language", {})
                brief_map = inner_data.get("brief", {})

                # Course data is stored in keys "1" or "2" (course types)
                for course_type_key in inner_data:
                    if not re.match("^[1-2]$", course_type_key):  # Only "1" or "2"
                        continue

                    courses_dict = inner_data[course_type_key]
                    if not isinstance(courses_dict, dict):
                        continue

                    for cos_id in courses_dict:
                        try:
                            raw_cos_data = courses_dict[cos_id]

                            # Parse time and classroom
                            cos_time = raw_cos_data.get("cos_time", "")
                            time_list = parse_time(cos_time) if cos_time else []
                            classroom_list = parse_classroom(cos_time) if cos_time else []

                            # Get brief info if available
                            brief = []
                            if cos_id in brief_map and isinstance(brief_map[cos_id], dict):
                                brief_code = list(brief_map[cos_id].keys())[0] if brief_map[cos_id] else None
                                if brief_code:
                                    brief_text = brief_map[cos_id].get(brief_code, {}).get('brief', '')
                                    brief = brief_text.split(',') if brief_text else []

                            # Clean course name
                            name = raw_cos_data.get("cos_cname", "").replace("(英文授課)", '')
                            name = name.replace("(英文班)", '')

                            # Use department name from API data
                            dept = inner_data.get("dep_cname", dept_id_inner)

                            # Convert to platform schema
                            course = {
                                "acy": year,
                                "sem": semester,
                                "crs_no": str(raw_cos_data.get("cos_id", "")),
                                "name": name,
                                "teacher": raw_cos_data.get("teacher", ""),
                                "credits": float(raw_cos_data.get("cos_credit", 0)),
                                "dept": dept,
                                "time": ",".join(time_list),
                                "classroom": ",".join(classroom_list),
                                "details": json.dumps({
                                    "cos_id": cos_id,
                                    "cos_code": raw_cos_data.get("cos_code", ""),
                                    "hours": raw_cos_data.get("cos_hours", ""),
                                    "num_limit": raw_cos_data.get("num_limit", ""),
                                    "reg_num": raw_cos_data.get("reg_num", ""),
                                    "time_classroom": raw_cos_data.get("cos_time", ""),
                                    "type": raw_cos_data.get("cos_type", ""),
                                    "brief": brief
                                }, ensure_ascii=False)
                            }

                            courses.append(course)
                        except Exception as e:
                            logger.warning(f"Error processing course {cos_id}: {e}")
                            continue
    except Exception as e:
        logger.error(f"Error extracting courses: {e}")

    return courses


def scrape_semester(year: int, semester: int, flang: str = "zh-tw") -> Dict:
    """Scrape all courses for a specific semester"""
    acysem = str(year) + str(semester)
    logger.info(f"\n{'='*80}")
    logger.info(f"Scraping Year {year}, Semester {semester} (acysem={acysem})")
    logger.info(f"{'='*80}")

    dep_list = []
    all_raw_data = {}

    try:
        # Get course types
        types = get_type()
        logger.info(f"Found {len(types)} course types")

        for type_item in types:
            ftype = type_item["uid"]
            type_name = type_item.get("cname", "Unknown")
            logger.info(f"\n📋 Processing type: {type_name}")

            # Get categories
            categories = get_category(ftype, flang, acysem)

            if type_name == "其他課程":
                # Special handling for "Other Courses"
                for fcategory in categories.keys():
                    if fcategory not in dep_list:
                        dep_list.append(fcategory)
                        raw_data = get_cos(year, semester, fcategory)
                        if raw_data:
                            all_raw_data[fcategory] = raw_data
                            logger.info(f"   ✅ Fetched courses for dept: {fcategory}")
            else:
                # Standard category handling
                for fcategory in categories.keys():
                    category_name = categories.get(fcategory, "")

                    # Get colleges
                    colleges = get_college(fcategory, ftype, flang, acysem)

                    if colleges:
                        for fcollege in colleges.keys():
                            # Get departments
                            deps = get_dep(fcollege, fcategory, ftype, flang, acysem)
                            if deps:
                                for fdep in deps.keys():
                                    if fdep not in dep_list:
                                        dep_list.append(fdep)
                                        raw_data = get_cos(year, semester, fdep)
                                        if raw_data:
                                            all_raw_data[fdep] = raw_data
                                            logger.info(f"   ✅ Fetched courses for dept: {fdep}")
                    else:
                        # No colleges, try direct department access
                        fcollege = ""
                        deps = get_dep(fcollege, fcategory, ftype, flang, acysem)
                        if deps:
                            for fdep in deps.keys():
                                if fdep not in dep_list:
                                    dep_list.append(fdep)
                                    raw_data = get_cos(year, semester, fdep)
                                    if raw_data:
                                        all_raw_data[fdep] = raw_data
                                        logger.info(f"   ✅ Fetched courses for dept: {fdep}")

    except Exception as e:
        logger.error(f"Error scraping semester {year}-{semester}: {e}")

    return all_raw_data


def main():
    """Main scraping function"""
    logger.info("🚀 NYCU Course Data Scraper (Adapted from GitHub Huskyee/NYCU_Timetable)")
    logger.info(f"Target: Years 110-114 (13 semesters)")
    logger.info(f"Output: {COURSES_FILE}")

    all_courses = []
    all_raw_data = {}

    # Scrape each semester
    for year, semester in SEMESTERS:
        try:
            raw_data = scrape_semester(year, semester)
            all_raw_data[f"{year}-{semester}"] = raw_data

            # Extract and convert courses
            courses = extract_courses_from_raw(year, semester, raw_data)
            all_courses.extend(courses)

            logger.info(f"\n✅ Extracted {len(courses)} courses from {year}-{semester}")

        except Exception as e:
            logger.error(f"❌ Error processing semester {year}-{semester}: {e}")

    # Save raw data
    logger.info(f"\n\n{'='*80}")
    logger.info(f"Saving raw data...")
    with open(RAW_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_raw_data, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Raw data saved to: {RAW_DATA_FILE}")

    # Save converted courses
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "source": "NYCU Timetable - GitHub Scraper Adapted",
        "years": "110-114",
        "semesters_count": len(SEMESTERS),
        "total_courses": len(all_courses),
        "courses": all_courses
    }

    with open(COURSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"\n{'='*80}")
    logger.info(f"📊 SCRAPING COMPLETE!")
    logger.info(f"{'='*80}")
    logger.info(f"✅ Total courses scraped: {len(all_courses)}")
    logger.info(f"✅ Semesters processed: {len(SEMESTERS)}")
    logger.info(f"✅ Saved to: {COURSES_FILE}")
    logger.info(f"📦 File size: {COURSES_FILE.stat().st_size / (1024*1024):.2f} MB")

    return all_courses


if __name__ == "__main__":
    main()
