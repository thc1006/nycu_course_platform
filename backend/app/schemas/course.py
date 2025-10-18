"""
Course Pydantic schemas for API serialization.

Defines request and response schemas for course endpoints.
"""

import json
import logging
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_serializer, computed_field

logger = logging.getLogger(__name__)


class CourseBase(BaseModel):
    """Base course schema with common fields."""

    acy: int = Field(..., description="Academic year", gt=0)
    sem: int = Field(..., description="Semester", ge=1, le=2)
    crs_no: str = Field(..., description="Course number", min_length=1)
    name: Optional[str] = Field(None, description="Course name/title")
    teacher: Optional[str] = Field(None, description="Instructor name(s)")
    credits: Optional[float] = Field(None, description="Number of credits", ge=0)
    dept: Optional[str] = Field(None, description="Department code")
    time: Optional[str] = Field(None, description="Time/schedule code")
    classroom: Optional[str] = Field(None, description="Classroom location code")
    syllabus: Optional[str] = Field(None, description="Course syllabus/outline (English)")
    syllabus_zh: Optional[str] = Field(None, description="Course syllabus in Traditional Chinese")
    syllabus_url_zh: Optional[str] = Field(None, description="URL to NYCU official Chinese syllabus")
    syllabus_url_en: Optional[str] = Field(None, description="URL to NYCU official English syllabus")
    # Note: details field is intentionally NOT included here - see CourseResponse for Union type


class CourseCreate(CourseBase):
    """Schema for creating a new course."""

    details: Optional[str] = Field(None, description="JSON string with metadata")


class CourseUpdate(BaseModel):
    """Schema for updating a course."""

    name: Optional[str] = None
    teacher: Optional[str] = None
    credits: Optional[float] = None
    dept: Optional[str] = None
    time: Optional[str] = None
    classroom: Optional[str] = None
    syllabus: Optional[str] = None
    syllabus_zh: Optional[str] = None
    details: Optional[str] = None


class CourseResponse(CourseBase):
    """Schema for course API responses."""

    id: int = Field(..., description="Course ID")
    details: Optional[Union[dict[str, Any], str]] = Field(None, description="Course metadata as JSON object or string")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "acy": 113,
                "sem": 1,
                "crs_no": "3101",
                "name": "Introduction to Computer Science",
                "teacher": "Dr. Smith",
                "credits": 3.0,
                "dept": "CS",
                "time": "Mon 10:00-12:00",
                "classroom": "A101",
                "details": {"capacity": 30},
            }
        }


class CourseFilterParams(BaseModel):
    """Schema for course filtering parameters."""

    acy: Optional[int] = Field(None, description="Filter by academic year", gt=0)
    sem: Optional[int] = Field(None, description="Filter by semester", ge=1, le=2)
    dept: Optional[str] = Field(None, description="Filter by department code")
    teacher: Optional[str] = Field(None, description="Filter by teacher name (partial)")
    q: Optional[str] = Field(None, description="Search query (course name or number)")
    limit: int = Field(200, description="Max results to return", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip", ge=0)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "acy": 113,
                "sem": 1,
                "dept": "CS",
                "teacher": "Smith",
                "q": "introduction",
                "limit": 50,
                "offset": 0,
            }
        }
