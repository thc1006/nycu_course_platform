#!/usr/bin/env python3
"""
NYCU Course Outline/Syllabus Scraper
從NYCU官方課程系統獲取課程綱要資訊
針對每個課程獲取其英文和中文綱要
"""

import requests
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/course_outlines")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTLINES_FILE = OUTPUT_DIR / "outlines_all.json"

BASE_URL = "https://timetable.nycu.edu.tw"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 年份和學期組合
SEMESTERS = [
    (110, 1), (110, 2),
    (111, 1), (111, 2),
    (112, 1), (112, 2),
    (113, 1), (113, 2),
    (114, 1),
]


def get_course_outline(acy: int, sem: int, crs_no: str, lang: str = "zh-tw") -> Optional[str]:
    """
    獲取單個課程的綱要信息

    Args:
        acy: 學年
        sem: 學期
        crs_no: 課程號
        lang: 語言 ('zh-tw' 或 'en')

    Returns:
        課程綱要文本或None
    """
    url = f"{BASE_URL}/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={crs_no}&lang={lang}"

    try:
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        if resp.status_code == 200:
            # 解析HTML獲取綱要內容
            # 通常綱要會在特定的div中
            content = resp.text

            # 簡單的提取邏輯 - 可根據實際HTML結構調整
            # 查找課程綱要內容區域
            if "crsoutline" in content.lower() or "course outline" in content.lower():
                # 基本提取: 尋找內容標籤
                matches = re.findall(r'<div[^>]*class="[^"]*outline[^"]*"[^>]*>(.+?)</div>', content, re.IGNORECASE | re.DOTALL)
                if matches:
                    outline = matches[0]
                    # 清理HTML標籤
                    outline = re.sub(r'<[^>]+>', '\n', outline)
                    outline = re.sub(r'\n\s*\n', '\n', outline).strip()
                    return outline

            return None
        else:
            logger.warning(f"HTTP {resp.status_code} for {acy}-{sem}-{crs_no}")
            return None

    except Exception as e:
        logger.warning(f"Error fetching outline for {crs_no}: {e}")
        return None


def get_courses_for_semester(acy: int, sem: int) -> List[Dict]:
    """
    獲取某學期的所有課程列表
    使用之前實現的API或爬蟲結果
    """
    try:
        # 嘗試從本地數據獲取
        data_file = Path(f"data/real_courses_nycu/courses_all_semesters.json")
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                courses = data.get('courses', [])
                # 篩選特定學期
                return [c for c in courses if c.get('acy') == acy and c.get('sem') == sem]
        return []
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return []


def scrape_course_outlines():
    """
    批量爬取所有課程的綱要信息
    """
    logger.info("=" * 80)
    logger.info("🚀 開始爬取課程綱要信息")
    logger.info("=" * 80)

    all_outlines = {}
    total_fetched = 0

    for acy, sem in SEMESTERS:
        logger.info(f"\n📚 處理學年 {acy}, 學期 {sem}")

        # 獲取該學期的課程列表
        courses = get_courses_for_semester(acy, sem)
        logger.info(f"   找到 {len(courses)} 門課程")

        semester_key = f"{acy}-{sem}"
        all_outlines[semester_key] = {}

        for idx, course in enumerate(courses, 1):  # 獲取所有課程
            crs_no = course.get('crs_no', '')
            crs_name = course.get('name', '')

            if not crs_no:
                continue

            # 獲取中文綱要
            outline_zh = get_course_outline(acy, sem, crs_no, "zh-tw")

            # 獲取英文綱要
            outline_en = get_course_outline(acy, sem, crs_no, "en")

            if outline_zh or outline_en:
                all_outlines[semester_key][crs_no] = {
                    "course_name": crs_name,
                    "zh_TW": outline_zh,
                    "en": outline_en
                }
                total_fetched += 1
                logger.info(f"   ✅ [{idx}] {crs_no} - {crs_name}: 已獲取")

            # 速率限制 - 避免被伺服器封禁
            if idx % 10 == 0:
                time.sleep(1)

        time.sleep(2)

    # 保存結果
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "source": "NYCU Timetable - Course Outline Scraper",
        "total_outlines": total_fetched,
        "outlines": all_outlines
    }

    with open(OUTLINES_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"\n{'='*80}")
    logger.info(f"✅ 爬取完成！")
    logger.info(f"{'='*80}")
    logger.info(f"✅ 總共獲取 {total_fetched} 份課程綱要")
    logger.info(f"✅ 保存到: {OUTLINES_FILE}")
    logger.info(f"📦 文件大小: {OUTLINES_FILE.stat().st_size / 1024:.1f} KB")

    return all_outlines


if __name__ == "__main__":
    scrape_course_outlines()
