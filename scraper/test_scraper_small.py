#!/usr/bin/env python3
"""
Test version - Scrape just 1-2 semesters to verify functionality
"""

import json
import re
import requests
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/real_courses_nycu")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEST_FILE = OUTPUT_DIR / "test_111-1.json"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
}

BASE_URL = "https://timetable.nycu.edu.tw"


def parse_time(tc: str) -> List[str]:
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
    try:
        logger.info("Fetching course types...")
        res = requests.get(f'{BASE_URL}/?r=main/get_type', headers=HEADERS, verify=False, timeout=15)
        types = res.json()
        logger.info(f"✅ Got {len(types)} types")
        return types
    except Exception as e:
        logger.error(f"Error fetching types: {e}")
        return []


def get_category(ftype: str, flang: str, acysem: str) -> Dict:
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


def main():
    """Test scrape for year 111, semester 1"""
    year, semester = 111, 1
    acysem = str(year) + str(semester)

    logger.info(f"\n{'='*80}")
    logger.info(f"🧪 TEST SCRAPING: Year {year}, Semester {semester}")
    logger.info(f"{'='*80}\n")

    all_courses = []
    dep_list = []
    flang = "zh-tw"

    try:
        # Get types
        types = get_type()

        for type_item in types:
            ftype = type_item["uid"]
            type_name = type_item.get("cname", "Unknown")
            logger.info(f"\n📋 Processing type: {type_name}")

            categories = get_category(ftype, flang, acysem)

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
                                    logger.info(f"   🏢 Fetching department: {fdep}")

                                    raw_data = get_cos(year, semester, fdep)
                                    if raw_data:
                                        # Extract courses
                                        for dep_value in raw_data:
                                            language = raw_data[dep_value].get("language", {})
                                            for dep_content in raw_data[dep_value]:
                                                if not re.match("^[1-2]+$", dep_content):
                                                    continue
                                                for cos_id in raw_data[dep_value][dep_content]:
                                                    try:
                                                        raw_cos_data = raw_data[dep_value][dep_content][cos_id]
                                                        time_list = parse_time(raw_cos_data["cos_time"])
                                                        classroom_list = parse_classroom(raw_cos_data["cos_time"])

                                                        name = raw_cos_data["cos_cname"].replace("(英文授課)", '')
                                                        name = name.replace("(英文班)", '')

                                                        course = {
                                                            "acy": year,
                                                            "sem": semester,
                                                            "crs_no": raw_cos_data["cos_id"],
                                                            "name": name,
                                                            "teacher": raw_cos_data.get("teacher", ""),
                                                            "credits": float(raw_cos_data.get("cos_credit", 0)),
                                                            "time": ",".join(time_list),
                                                            "classroom": ",".join(classroom_list),
                                                        }
                                                        all_courses.append(course)
                                                    except Exception as e:
                                                        logger.debug(f"Error processing course {cos_id}: {e}")
                                        logger.info(f"      ✅ Extracted {len(all_courses)} courses so far")
                else:
                    # Try direct department access
                    deps = get_dep("", fcategory, ftype, flang, acysem)
                    if deps:
                        for fdep in deps.keys():
                            if fdep not in dep_list:
                                dep_list.append(fdep)
                                logger.info(f"   🏢 Fetching department: {fdep}")
                                raw_data = get_cos(year, semester, fdep)
                                if raw_data:
                                    for dep_value in raw_data:
                                        for dep_content in raw_data[dep_value]:
                                            if not re.match("^[1-2]+$", dep_content):
                                                continue
                                            for cos_id in raw_data[dep_value][dep_content]:
                                                try:
                                                    raw_cos_data = raw_data[dep_value][dep_content][cos_id]
                                                    time_list = parse_time(raw_cos_data["cos_time"])
                                                    classroom_list = parse_classroom(raw_cos_data["cos_time"])

                                                    name = raw_cos_data["cos_cname"].replace("(英文授課)", '')
                                                    name = name.replace("(英文班)", '')

                                                    course = {
                                                        "acy": year,
                                                        "sem": semester,
                                                        "crs_no": raw_cos_data["cos_id"],
                                                        "name": name,
                                                        "teacher": raw_cos_data.get("teacher", ""),
                                                        "credits": float(raw_cos_data.get("cos_credit", 0)),
                                                        "time": ",".join(time_list),
                                                        "classroom": ",".join(classroom_list),
                                                    }
                                                    all_courses.append(course)
                                                except Exception as e:
                                                    logger.debug(f"Error: {e}")
                                    logger.info(f"      ✅ Extracted {len(all_courses)} courses so far")

    except Exception as e:
        logger.error(f"Error: {e}")

    # Save results
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "test_semester": f"{year}-{semester}",
        "total_courses": len(all_courses),
        "courses": all_courses[:10]  # Show first 10
    }

    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"\n{'='*80}")
    logger.info(f"✅ TEST COMPLETE!")
    logger.info(f"Total courses found: {len(all_courses)}")
    logger.info(f"Saved (first 10) to: {TEST_FILE}")
    logger.info(f"{'='*80}")

    # Display sample courses
    logger.info("\n📚 Sample courses:")
    for i, course in enumerate(all_courses[:3], 1):
        logger.info(f"\n{i}. {course['name']}")
        logger.info(f"   课号: {course['crs_no']}")
        logger.info(f"   教师: {course['teacher']}")
        logger.info(f"   学分: {course['credits']}")


if __name__ == "__main__":
    main()
