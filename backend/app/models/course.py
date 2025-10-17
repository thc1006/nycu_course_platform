"""
Course database model.

Defines the structure of course records in the database.
"""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .semester import Semester


class Course(SQLModel, table=True):
    """
    Course model representing a university course.

    Attributes:
        id: Primary key, auto-incremented
        semester_id: Foreign key to semesters table
        crs_no: Course number
        permanent_crs_no: Permanent course number
        name: Course name/title
        credits: Number of credits
        required: Required/elective status
        teacher: Instructor name(s)
        dept: Department code
        day_codes: Day codes (M, T, W, R, F)
        time_codes: Time codes
        classroom_codes: Classroom codes
        url: Course URL
        details: JSON string with additional metadata
    """
    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    semester_id: int = Field(foreign_key="semester.id", index=True, description="Semester ID")
    crs_no: str = Field(index=True, description="Course number")
    permanent_crs_no: Optional[str] = Field(default=None, description="Permanent course number")
    name: str = Field(description="Course name/title")
    credits: Optional[float] = Field(default=None, index=True, description="Number of credits")
    required: Optional[str] = Field(default=None, description="Required/elective status")
    teacher: Optional[str] = Field(default=None, index=True, description="Instructor name(s)")
    dept: Optional[str] = Field(default=None, index=True, description="Department code")
    day_codes: Optional[str] = Field(default=None, index=True, description="Day codes")
    time_codes: Optional[str] = Field(default=None, description="Time codes")
    classroom_codes: Optional[str] = Field(default=None, description="Classroom codes")
    url: Optional[str] = Field(default=None, description="Course URL")
    syllabus: Optional[str] = Field(default=None, description="Course syllabus/outline")
    syllabus_zh: Optional[str] = Field(default=None, description="Course syllabus in Traditional Chinese")
    details: Optional[str] = Field(default=None, description="JSON string with additional metadata")

    # Note: acy and sem are computed properties - we store semester_id
    # If you need acy and sem, join with semesters table or load from semester_id context

    @property
    def time(self) -> Optional[str]:
        """Get time codes (alias for compatibility)."""
        return self.time_codes

    @property
    def classroom(self) -> Optional[str]:
        """Get classroom codes (alias for compatibility)."""
        return self.classroom_codes

    class Config:
        """Model configuration."""

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
                "details": '{"capacity": 30, "enrollment": 28}',
            }
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"Course(crs_no={self.crs_no}, name={self.name}, semester_id={self.semester_id})"
