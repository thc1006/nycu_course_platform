"""
Semester database model.

Defines the structure of semester records in the database.
"""

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .course import Course


class Semester(SQLModel, table=True):
    """
    Semester model representing an academic semester.

    Attributes:
        id: Primary key, auto-incremented
        acy: Academic year (e.g., 113 for 2024)
        sem: Semester identifier (1=Fall, 2=Spring)
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    acy: int = Field(index=True, description="Academic year")
    sem: int = Field(description="Semester (1=Fall, 2=Spring)")

    # Relationship to Course
    courses: list["Course"] = Relationship(back_populates="semester")

    class Config:
        """Model configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "acy": 113,
                "sem": 1,
            }
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"Semester(acy={self.acy}, sem={self.sem})"
