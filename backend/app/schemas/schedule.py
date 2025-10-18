"""
Schedule Pydantic schemas for API serialization.

Defines request and response schemas for schedule (timetable) endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.course import CourseResponse


class ScheduleCourseBase(BaseModel):
    """Base schema for schedule course."""

    course_id: int = Field(..., description="Course ID to add to schedule")
    color: Optional[str] = Field(None, description="Display color in hex format", pattern=r"^#[0-9A-Fa-f]{6}$")
    notes: Optional[str] = Field(None, description="User notes for this course", max_length=500)


class ScheduleCourseCreate(ScheduleCourseBase):
    """Schema for adding a course to a schedule."""

    pass


class ScheduleCourseResponse(ScheduleCourseBase):
    """Schema for schedule course response with course details."""

    id: int = Field(..., description="Schedule course ID")
    schedule_id: int = Field(..., description="Schedule ID")
    added_at: datetime = Field(..., description="When course was added")
    course: CourseResponse = Field(..., description="Full course details")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ScheduleBase(BaseModel):
    """Base schedule schema."""

    name: str = Field(..., description="Schedule name", min_length=1, max_length=100)
    acy: int = Field(..., description="Academic year", gt=0)
    sem: int = Field(..., description="Semester (1=Fall, 2=Spring)", ge=1, le=2)


class ScheduleCreate(ScheduleBase):
    """Schema for creating a new schedule."""

    user_id: Optional[str] = Field(None, description="User identifier or session ID", max_length=100)


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule."""

    name: Optional[str] = Field(None, description="Schedule name", min_length=1, max_length=100)


class ScheduleResponse(ScheduleBase):
    """Schema for schedule API responses."""

    id: int = Field(..., description="Schedule ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    total_credits: float = Field(0.0, description="Total credits in this schedule")
    total_courses: int = Field(0, description="Total number of courses")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "113-1 我的課表",
                "acy": 113,
                "sem": 1,
                "user_id": "session_abc123",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T14:20:00",
                "total_credits": 18.0,
                "total_courses": 6,
            }
        }


class ScheduleDetailResponse(ScheduleResponse):
    """Detailed schedule response with all courses."""

    schedule_courses: list[ScheduleCourseResponse] = Field(
        default_factory=list, description="Courses in this schedule"
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class AddCourseRequest(BaseModel):
    """Request to add a course to schedule."""

    course_id: int = Field(..., description="Course ID to add")
    color: Optional[str] = Field(None, description="Display color", pattern=r"^#[0-9A-Fa-f]{6}$")
    notes: Optional[str] = Field(None, description="Notes", max_length=500)


class RemoveCourseRequest(BaseModel):
    """Request to remove a course from schedule."""

    course_id: int = Field(..., description="Course ID to remove")
