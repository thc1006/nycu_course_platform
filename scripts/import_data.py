"""
Script to import scraped course data into the local database.

Run this after `scraper.py` has produced `scraper/data/courses.json`.  It
creates the database tables (if necessary) and inserts courses and
semester rows.  For simplicity, instructor names, classrooms, and
schedule codes are stored as plain text.  You can normalize them
later if needed.
"""

import json
import os
from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Dict, Tuple

from backend.app import Course as CourseModel  # Reuse the model from the API


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./nycu_courses.db")
engine = create_engine(DATABASE_URL, echo=False)


def get_or_create_semester(session: Session, acy: int, sem: int) -> Tuple[int, int]:
    """Ensure a (acy, sem) combination exists in the courses table for grouping."""
    # In this simplified schema, semester info is stored directly on the Course
    # table.  We don't have a separate semesters table in the SQLModel model,
    # but if you extend the schema you can adjust this function.
    return (acy, sem)


def run_import(json_path: str) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    SQLModel.metadata.create_all(engine)
    inserted = 0
    with Session(engine) as session:
        for item in data:
            acy = int(item.get("acy"))
            sem = int(item.get("sem"))
            crs_no = str(item.get("crs_no"))
            # Check if course already exists
            stmt = select(CourseModel).where(
                CourseModel.acy == acy,
                CourseModel.sem == sem,
                CourseModel.crs_no == crs_no,
            )
            exists = session.exec(stmt).first()
            if exists:
                continue
            course = CourseModel(
                acy=acy,
                sem=sem,
                crs_no=crs_no,
                name=item.get("name"),
                teacher=item.get("teacher"),
                credits=item.get("credits"),
                dept=item.get("dept"),
                day_codes=item.get("day_codes"),
                time=item.get("time_codes"),
                classroom=item.get("classroom_codes"),
                details=json.dumps(item, ensure_ascii=False),
            )
            session.add(course)
            inserted += 1
        session.commit()
    print(f"Imported {inserted} new courses into the database.")


if __name__ == "__main__":
    default_path = Path(__file__).resolve().parent.parent / "scraper" / "data" / "courses.json"
    path = os.environ.get("COURSE_JSON_PATH", str(default_path))
    run_import(path)