"""
Course database model.

Defines the structure of course records in the database.
"""

from typing import TYPE_CHECKING, Any, Optional

from pydantic import model_serializer
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

    # Relationship to Semester
    semester: Optional["Semester"] = Relationship(back_populates="courses")

    @property
    def time(self) -> Optional[str]:
        """Get time codes (alias for compatibility)."""
        return self.time_codes

    @property
    def classroom(self) -> Optional[str]:
        """Get classroom codes (alias for compatibility)."""
        return self.classroom_codes

    @property
    def acy(self) -> Optional[int]:
        """Get academic year from semester."""
        return self.semester.acy if self.semester else None

    @property
    def sem(self) -> Optional[int]:
        """Get semester number from semester."""
        return self.semester.sem if self.semester else None

    @property
    def syllabus_url_zh(self) -> Optional[str]:
        """Generate Chinese syllabus URL."""
        if self.semester and self.crs_no:
            acy = self.semester.acy
            sem = self.semester.sem
            return f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={self.crs_no}&lang=zh-tw"
        return None

    @property
    def syllabus_url_en(self) -> Optional[str]:
        """Generate English syllabus URL."""
        if self.semester and self.crs_no:
            acy = self.semester.acy
            sem = self.semester.sem
            return f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={self.crs_no}&lang=en"
        return None

    @model_serializer(mode='wrap')
    def _serialize_model(self, serializer: Any) -> dict[str, Any]:
        """Custom serializer to include computed properties."""
        import logging
        logger = logging.getLogger(__name__)

        data = serializer(self)
        # Add computed properties
        data['acy'] = self.acy
        data['sem'] = self.sem
        data['time'] = self.time
        data['classroom'] = self.classroom

        # Generate syllabus URLs directly (using the acy/sem from above to avoid semester access issues)
        logger.info(f"Serializing course {self.crs_no}: acy={data['acy']}, sem={data['sem']}, semester={self.semester}")
        if data['acy'] is not None and data['sem'] is not None and self.crs_no:
            acy_val = data['acy']
            sem_val = data['sem']
            data['syllabus_url_zh'] = f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy_val}&Sem={sem_val}&CrsNo={self.crs_no}&lang=zh-tw"
            data['syllabus_url_en'] = f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy_val}&Sem={sem_val}&CrsNo={self.crs_no}&lang=en"
            logger.info(f"Generated syllabus URLs for {self.crs_no}")
        else:
            data['syllabus_url_zh'] = None
            data['syllabus_url_en'] = None
            logger.warning(f"Failed to generate syllabus URLs for {self.crs_no}: acy={data['acy']}, sem={data['sem']}, crs_no={self.crs_no}")

        return data

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
