"""
Course data model for the NYCU course scraper.

This module defines the Course dataclass that represents a single course
with all its attributes including academic year, semester, course number,
and detailed information.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Course:
    """
    Data model representing a course at NYCU.

    Attributes:
        acy: Academic year (e.g., 113 for 2024-2025)
        sem: Semester (1 for fall, 2 for spring)
        crs_no: Course number/code (e.g., "3101")
        name: Course name/title
        teacher: Instructor name(s)
        credits: Number of credits for the course
        dept: Department code
        time: Time/schedule code (e.g., "Mon 10:00-12:00")
        classroom: Classroom location code
        details: Dictionary containing additional metadata
    """

    acy: int
    sem: int
    crs_no: str
    name: Optional[str] = None
    teacher: Optional[str] = None
    credits: Optional[float] = None
    dept: Optional[str] = None
    time: Optional[str] = None
    classroom: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Course instance to a dictionary.

        This method serializes the Course object into a dictionary format
        suitable for JSON export or database storage. The details field
        is included as a nested dictionary.

        Returns:
            Dictionary representation of the course with all fields.

        Example:
            >>> course = Course(acy=113, sem=1, crs_no="3101", name="Intro to CS")
            >>> course.to_dict()
            {
                'acy': 113,
                'sem': 1,
                'crs_no': '3101',
                'name': 'Intro to CS',
                'teacher': None,
                'credits': None,
                'dept': None,
                'time': None,
                'classroom': None,
                'details': {}
            }
        """
        return {
            "acy": self.acy,
            "sem": self.sem,
            "crs_no": self.crs_no,
            "name": self.name,
            "teacher": self.teacher,
            "credits": self.credits,
            "dept": self.dept,
            "time": self.time,
            "classroom": self.classroom,
            "details": self.details,
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the Course instance.

        Provides a human-readable representation of the course showing
        the key identifying information (academic year, semester, course
        number, and name if available).

        Returns:
            String representation of the course.

        Example:
            >>> course = Course(acy=113, sem=1, crs_no="3101", name="Intro to CS")
            >>> repr(course)
            'Course(acy=113, sem=1, crs_no=3101, name=Intro to CS)'
        """
        name_str = f", name={self.name}" if self.name else ""
        return f"Course(acy={self.acy}, sem={self.sem}, crs_no={self.crs_no}{name_str})"

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the Course.

        Returns:
            User-friendly string representation.
        """
        if self.name:
            return f"{self.crs_no} - {self.name} ({self.acy}/{self.sem})"
        return f"{self.crs_no} ({self.acy}/{self.sem})"

    def __eq__(self, other: object) -> bool:
        """
        Compare two Course instances for equality.

        Two courses are considered equal if they have the same academic
        year, semester, and course number.

        Args:
            other: Another object to compare with.

        Returns:
            True if courses are equal, False otherwise.
        """
        if not isinstance(other, Course):
            return NotImplemented
        return (
            self.acy == other.acy
            and self.sem == other.sem
            and self.crs_no == other.crs_no
        )

    def __hash__(self) -> int:
        """
        Return hash value for the Course instance.

        Allows Course instances to be used in sets and as dictionary keys.
        The hash is based on the unique identifier (acy, sem, crs_no).

        Returns:
            Hash value for the course.
        """
        return hash((self.acy, self.sem, self.crs_no))
