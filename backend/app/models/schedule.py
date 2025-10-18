"""
Schedule and ScheduleCourse models for course scheduling feature.

This module defines the database models for storing user-created course schedules.
Each schedule belongs to a user (or session) and contains multiple courses.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Schedule(SQLModel, table=True):
    """User's course schedule (timetable)."""

    __tablename__ = "schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="Schedule name, e.g., '113-1 我的課表'")

    # Academic year and semester this schedule is for
    acy: int = Field(description="Academic year", gt=0, index=True)
    sem: int = Field(description="Semester (1=Fall, 2=Spring)", ge=1, le=2, index=True)

    # Optional user identification (can be session ID or user ID)
    user_id: Optional[str] = Field(default=None, description="User identifier or session ID", index=True)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Relationships
    schedule_courses: list["ScheduleCourse"] = Relationship(
        back_populates="schedule",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ScheduleCourse(SQLModel, table=True):
    """Association table linking schedules to courses."""

    __tablename__ = "schedule_courses"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    schedule_id: int = Field(foreign_key="schedules.id", index=True, description="Schedule ID")
    course_id: int = Field(foreign_key="courses.id", index=True, description="Course ID")

    # Additional metadata for this course in the schedule
    color: Optional[str] = Field(default=None, description="Display color in hex, e.g., '#3B82F6'")
    notes: Optional[str] = Field(default=None, description="User notes for this course")

    added_at: datetime = Field(default_factory=datetime.utcnow, description="When course was added")

    # Relationships
    schedule: Schedule = Relationship(back_populates="schedule_courses")
    course: "Course" = Relationship()  # type: ignore


# Import Course model to establish relationship
# This is done at the end to avoid circular imports
from app.models.course import Course  # noqa: E402

ScheduleCourse.model_rebuild()
