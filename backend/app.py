"""
FastAPI backend for the NYCU Course Platform.

This service exposes endpoints for listing semesters, querying
courses with filters, and retrieving individual course details.

It uses SQLModel to interact with a SQLite (or Postgres) database.
The database can be configured via the `DATABASE_URL` environment variable.
"""

from typing import Optional, List
import os

from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, Session, create_engine, select


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./nycu_courses.db")
engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI(title="NYCU Course API")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    acy: int
    sem: int
    crs_no: str
    name: Optional[str] = None
    teacher: Optional[str] = None
    credits: Optional[float] = None
    dept: Optional[str] = None
    time: Optional[str] = None
    classroom: Optional[str] = None
    details: Optional[str] = None  # JSON string with additional fields


@app.on_event("startup")
def on_startup() -> None:
    # Create tables if they do not exist
    SQLModel.metadata.create_all(engine)


@app.get("/semesters")
def get_semesters() -> List[dict]:
    """
    Return a list of available semesters (academic year and semester).
    Sorted by academic year descending.
    """
    with Session(engine) as session:
        rows = session.exec(
            select(Course.acy, Course.sem).distinct().order_by(Course.acy.desc(), Course.sem.desc())
        ).all()
        return [ {"acy": acy, "sem": sem} for acy, sem in rows ]


@app.get("/courses")
def list_courses(
    acy: Optional[int] = Query(None, description="Academic year"),
    sem: Optional[int] = Query(None, description="Semester (1=Fall, 2=Spring)"),
    dept: Optional[str] = Query(None, description="Department code"),
    teacher: Optional[str] = Query(None, description="Instructor name"),
    q: Optional[str] = Query(None, description="Keyword to search in course name"),
) -> List[Course]:
    """
    List courses matching the provided filters.  If no filters are
    provided, returns all courses up to a limit of 200.
    """
    stmt = select(Course)
    if acy is not None:
        stmt = stmt.where(Course.acy == acy)
    if sem is not None:
        stmt = stmt.where(Course.sem == sem)
    if dept:
        stmt = stmt.where(Course.dept.contains(dept))
    if teacher:
        stmt = stmt.where(Course.teacher.contains(teacher))
    if q:
        stmt = stmt.where(Course.name.contains(q))
    stmt = stmt.limit(200)
    with Session(engine) as session:
        return session.exec(stmt).all()


@app.get("/courses/{course_id}")
def get_course(course_id: int) -> Course:
    """
    Retrieve a single course by its ID.
    """
    with Session(engine) as session:
        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course