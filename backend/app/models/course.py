"""
Course database model.

Defines the structure of course records in the database.
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class Course(SQLModel, table=True):
    """
    Course model representing a university course.

    Attributes:
        id: Primary key, auto-incremented
        acy: Academic year
        sem: Semester (1=Fall, 2=Spring)
        crs_no: Course number (unique within semester)
        name: Course name/title
        teacher: Instructor name(s)
        credits: Number of credits
        dept: Department code
        time: Time/schedule code
        classroom: Classroom location code
        details: JSON string with additional metadata
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    acy: int = Field(index=True, description="Academic year")
    sem: int = Field(index=True, description="Semester (1=Fall, 2=Spring)")
    crs_no: str = Field(index=True, description="Course number")
    name: Optional[str] = Field(default=None, description="Course name/title")
    teacher: Optional[str] = Field(default=None, description="Instructor name(s)")
    credits: Optional[float] = Field(default=None, description="Number of credits")
    dept: Optional[str] = Field(default=None, index=True, description="Department code")
    time: Optional[str] = Field(default=None, description="Time/schedule code")
    classroom: Optional[str] = Field(default=None, description="Classroom location code")
    details: Optional[str] = Field(
        default=None, description="JSON string with additional metadata"
    )

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
        return f"Course(crs_no={self.crs_no}, name={self.name}, acy={self.acy}, sem={self.sem})"
