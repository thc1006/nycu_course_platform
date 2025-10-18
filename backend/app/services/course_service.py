"""
Course service module.

This module provides business logic for course operations. It acts as an
intermediary layer between the API routes and the database layer, handling
validation, error handling, data transformation, and business rules.
"""

import json
import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import course as course_db
from app.models.course import Course
from app.utils.exceptions import (
    CourseNotFound,
    DatabaseError,
    InvalidQueryParameter,
)

# Set up logging
logger = logging.getLogger(__name__)


class CourseService:
    """
    Service class for course-related business logic.

    This class encapsulates all business logic related to courses,
    including validation, data processing, details parsing, and
    coordination between different database operations.

    Attributes:
        session: AsyncSession for database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize CourseService.

        Args:
            session: Database session for performing operations
        """
        self.session = session

    async def list_courses(
        self,
        acy: Optional[int] = None,
        sem: Optional[int] = None,
        dept: Optional[str] = None,
        teacher: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[Course]:
        """
        Retrieve courses with optional filtering and pagination.

        This method validates parameters and applies business rules before
        querying the database.

        Args:
            acy: Filter by academic year
            sem: Filter by semester number
            dept: Filter by department code (partial match)
            teacher: Filter by teacher name (partial match)
            q: Search query for course name or number
            limit: Maximum number of results (default: 200, max: 1000)
            offset: Number of results to skip (default: 0)

        Returns:
            List of course records matching the filters

        Raises:
            InvalidQueryParameter: If parameters are invalid
            DatabaseError: If the database operation fails

        Example:
            >>> service = CourseService(session)
            >>> courses = await service.list_courses(acy=113, sem=1, dept="CS")
            >>> print(f"Found {len(courses)} CS courses")
        """
        # Validate parameters
        self._validate_list_params(acy, sem, limit, offset)

        logger.info(
            f"Listing courses: acy={acy}, sem={sem}, dept={dept}, "
            f"teacher={teacher}, q={q}, limit={limit}, offset={offset}"
        )

        try:
            courses = await course_db.get_all_courses(
                session=self.session,
                acy=acy,
                sem=sem,
                dept=dept,
                teacher=teacher,
                q=q,
                limit=limit,
                offset=offset,
            )
            logger.info(f"Successfully retrieved {len(courses)} courses")
            return courses
        except DatabaseError as e:
            logger.error(f"Failed to list courses: {e}")
            raise

    async def get_course_detail(self, course_id: int) -> dict[str, Any]:
        """
        Retrieve detailed information for a specific course.

        This method fetches the course and parses the details JSON field
        into a structured format for easier consumption.

        Args:
            course_id: ID of the course to retrieve

        Returns:
            Dictionary containing course data with parsed details

        Raises:
            CourseNotFound: If course doesn't exist
            DatabaseError: If the database operation fails

        Example:
            >>> service = CourseService(session)
            >>> course_detail = await service.get_course_detail(123)
            >>> print(f"Course: {course_detail['name']}")
            >>> print(f"Details: {course_detail['parsed_details']}")
        """
        logger.info(f"Fetching course detail for ID: {course_id}")
        try:
            course = await course_db.get_course(self.session, course_id)

            # Build response with parsed details
            acy = course.semester.acy if course.semester else 0
            sem = course.semester.sem if course.semester else 0

            # Generate syllabus URLs
            syllabus_url_zh = None
            syllabus_url_en = None
            if course.semester and course.crs_no:
                syllabus_url_zh = f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={course.crs_no}&lang=zh-tw"
                syllabus_url_en = f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={course.crs_no}&lang=en"

            course_dict = {
                "id": course.id,
                "acy": acy,
                "sem": sem,
                "crs_no": course.crs_no,
                "name": course.name,
                "teacher": course.teacher,
                "credits": course.credits,
                "dept": course.dept,
                "time": course.time,
                "classroom": course.classroom,
                "syllabus": course.syllabus,
                "syllabus_zh": course.syllabus_zh,
                "syllabus_url_zh": syllabus_url_zh,
                "syllabus_url_en": syllabus_url_en,
                "details": course.details,
                "parsed_details": self._parse_details(course.details),
            }

            logger.info(f"Successfully retrieved course {course_id}")
            return course_dict

        except CourseNotFound as e:
            logger.warning(f"Course not found: {course_id}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to get course {course_id}: {e}")
            raise

    async def search_courses(
        self, query: str, limit: int = 100
    ) -> list[Course]:
        """
        Search for courses by name or course number.

        This provides a full-text search capability across course names
        and course numbers.

        Args:
            query: Search query string
            limit: Maximum number of results (default: 100, max: 1000)

        Returns:
            List of courses matching the search query

        Raises:
            InvalidQueryParameter: If query is empty or limit is invalid
            DatabaseError: If the database operation fails

        Example:
            >>> service = CourseService(session)
            >>> courses = await service.search_courses("computer science")
            >>> for course in courses:
            ...     print(f"{course.crs_no}: {course.name}")
        """
        # Validate parameters
        if not query or not query.strip():
            raise InvalidQueryParameter(
                message="Search query cannot be empty",
                parameter_name="query",
            )

        if limit <= 0 or limit > 1000:
            raise InvalidQueryParameter(
                message="Limit must be between 1 and 1000",
                parameter_name="limit",
                parameter_value=str(limit),
            )

        logger.info(f"Searching courses with query: '{query}', limit={limit}")
        try:
            courses = await course_db.search_courses(
                self.session, query, limit
            )
            logger.info(f"Search returned {len(courses)} courses")
            return courses
        except DatabaseError as e:
            logger.error(f"Failed to search courses: {e}")
            raise

    async def get_courses_by_semester(
        self, acy: int, sem: int
    ) -> list[Course]:
        """
        Retrieve all courses for a specific semester.

        Args:
            acy: Academic year
            sem: Semester number

        Returns:
            List of all courses in the specified semester

        Raises:
            InvalidQueryParameter: If acy or sem are invalid
            DatabaseError: If the database operation fails

        Example:
            >>> service = CourseService(session)
            >>> courses = await service.get_courses_by_semester(113, 1)
            >>> print(f"Found {len(courses)} courses in Fall 2024")
        """
        # Validate parameters
        self._validate_semester_params(acy, sem)

        logger.info(f"Fetching all courses for acy={acy}, sem={sem}")
        try:
            courses = await course_db.get_courses_by_semester(
                self.session, acy, sem
            )
            logger.info(
                f"Successfully retrieved {len(courses)} courses for semester"
            )
            return courses
        except DatabaseError as e:
            logger.error(f"Failed to get courses by semester: {e}")
            raise

    async def create_course(
        self,
        acy: int,
        sem: int,
        crs_no: str,
        name: Optional[str] = None,
        teacher: Optional[str] = None,
        credits: Optional[float] = None,
        dept: Optional[str] = None,
        time: Optional[str] = None,
        classroom: Optional[str] = None,
        details: Optional[str] = None,
    ) -> Course:
        """
        Create a new course after validation.

        Args:
            acy: Academic year
            sem: Semester number
            crs_no: Course number (required)
            name: Course name/title
            teacher: Instructor name(s)
            credits: Number of credits
            dept: Department code
            time: Time/schedule code
            classroom: Classroom location
            details: JSON string with additional metadata

        Returns:
            Newly created course record

        Raises:
            InvalidQueryParameter: If required parameters are invalid
            DatabaseError: If creation fails

        Example:
            >>> service = CourseService(session)
            >>> course = await service.create_course(
            ...     acy=113, sem=1, crs_no="CS3101",
            ...     name="Intro to CS", teacher="Dr. Smith"
            ... )
        """
        # Validate parameters
        self._validate_semester_params(acy, sem)
        self._validate_course_number(crs_no)

        if credits is not None and credits < 0:
            raise InvalidQueryParameter(
                message="Credits must be non-negative",
                parameter_name="credits",
                parameter_value=str(credits),
            )

        # Validate details JSON if provided
        if details is not None:
            self._validate_json_string(details)

        logger.info(f"Creating new course: crs_no={crs_no}, acy={acy}, sem={sem}")
        try:
            course = await course_db.create_course(
                session=self.session,
                acy=acy,
                sem=sem,
                crs_no=crs_no,
                name=name,
                teacher=teacher,
                credits=credits,
                dept=dept,
                time=time,
                classroom=classroom,
                details=details,
            )
            logger.info(f"Successfully created course: id={course.id}")
            return course
        except DatabaseError as e:
            logger.error(f"Failed to create course: {e}")
            raise

    async def update_course(
        self,
        course_id: int,
        name: Optional[str] = None,
        teacher: Optional[str] = None,
        credits: Optional[float] = None,
        dept: Optional[str] = None,
        time: Optional[str] = None,
        classroom: Optional[str] = None,
        details: Optional[str] = None,
    ) -> Course:
        """
        Update an existing course's fields.

        Args:
            course_id: ID of the course to update
            name: New course name
            teacher: New instructor name
            credits: New number of credits
            dept: New department code
            time: New time/schedule
            classroom: New classroom location
            details: New JSON details string

        Returns:
            Updated course record

        Raises:
            CourseNotFound: If course doesn't exist
            InvalidQueryParameter: If new values are invalid
            DatabaseError: If update fails

        Example:
            >>> service = CourseService(session)
            >>> course = await service.update_course(123, teacher="Dr. Johnson")
        """
        # Validate new parameters if provided
        if credits is not None and credits < 0:
            raise InvalidQueryParameter(
                message="Credits must be non-negative",
                parameter_name="credits",
                parameter_value=str(credits),
            )

        # Validate details JSON if provided
        if details is not None:
            self._validate_json_string(details)

        logger.info(f"Updating course {course_id}")
        try:
            course = await course_db.update_course(
                session=self.session,
                course_id=course_id,
                name=name,
                teacher=teacher,
                credits=credits,
                dept=dept,
                time=time,
                classroom=classroom,
                details=details,
            )
            logger.info(f"Successfully updated course {course_id}")
            return course
        except CourseNotFound as e:
            logger.warning(f"Course not found for update: {course_id}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to update course {course_id}: {e}")
            raise

    async def delete_course(self, course_id: int) -> None:
        """
        Delete a course from the database.

        Args:
            course_id: ID of the course to delete

        Raises:
            CourseNotFound: If course doesn't exist
            DatabaseError: If deletion fails

        Example:
            >>> service = CourseService(session)
            >>> await service.delete_course(123)
            >>> print("Course deleted successfully")
        """
        logger.info(f"Deleting course {course_id}")
        try:
            await course_db.delete_course(self.session, course_id)
            logger.info(f"Successfully deleted course {course_id}")
        except CourseNotFound as e:
            logger.warning(f"Course not found for deletion: {course_id}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to delete course {course_id}: {e}")
            raise

    def _parse_details(self, details: Optional[str]) -> Optional[dict[str, Any]]:
        """
        Parse the details JSON string into a dictionary.

        Args:
            details: JSON string containing course details

        Returns:
            Parsed dictionary or None if details is None or invalid JSON

        Example:
            >>> details_str = '{"capacity": 30, "enrollment": 28}'
            >>> parsed = self._parse_details(details_str)
            >>> print(parsed["capacity"])  # 30
        """
        if details is None or not details.strip():
            return None

        try:
            parsed = json.loads(details)
            logger.debug("Successfully parsed details JSON")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse details JSON: {e}")
            return None

    def _validate_json_string(self, json_string: str) -> None:
        """
        Validate that a string is valid JSON.

        Args:
            json_string: String to validate

        Raises:
            InvalidQueryParameter: If string is not valid JSON
        """
        try:
            json.loads(json_string)
        except json.JSONDecodeError as e:
            raise InvalidQueryParameter(
                message=f"Invalid JSON format: {str(e)}",
                parameter_name="details",
            )

    def _validate_list_params(
        self,
        acy: Optional[int],
        sem: Optional[int],
        limit: int,
        offset: int,
    ) -> None:
        """
        Validate parameters for listing courses.

        Args:
            acy: Academic year to validate
            sem: Semester to validate
            limit: Limit to validate
            offset: Offset to validate

        Raises:
            InvalidQueryParameter: If parameters are invalid
        """
        # Validate acy and sem if provided
        if acy is not None:
            if acy <= 0:
                raise InvalidQueryParameter(
                    message="Academic year must be a positive integer",
                    parameter_name="acy",
                    parameter_value=str(acy),
                )

        if sem is not None:
            if sem not in [1, 2]:
                raise InvalidQueryParameter(
                    message="Semester must be 1 (Fall) or 2 (Spring)",
                    parameter_name="sem",
                    parameter_value=str(sem),
                )

        # Validate limit
        if limit <= 0 or limit > 1000:
            raise InvalidQueryParameter(
                message="Limit must be between 1 and 1000",
                parameter_name="limit",
                parameter_value=str(limit),
            )

        # Validate offset
        if offset < 0:
            raise InvalidQueryParameter(
                message="Offset must be non-negative",
                parameter_name="offset",
                parameter_value=str(offset),
            )

    def _validate_semester_params(self, acy: int, sem: int) -> None:
        """
        Validate semester parameters.

        Args:
            acy: Academic year to validate
            sem: Semester to validate

        Raises:
            InvalidQueryParameter: If parameters are invalid
        """
        if acy <= 0:
            raise InvalidQueryParameter(
                message="Academic year must be a positive integer",
                parameter_name="acy",
                parameter_value=str(acy),
            )

        if sem not in [1, 2]:
            raise InvalidQueryParameter(
                message="Semester must be 1 (Fall) or 2 (Spring)",
                parameter_name="sem",
                parameter_value=str(sem),
            )

    def _validate_course_number(self, crs_no: str) -> None:
        """
        Validate course number.

        Args:
            crs_no: Course number to validate

        Raises:
            InvalidQueryParameter: If course number is invalid
        """
        if not crs_no or not crs_no.strip():
            raise InvalidQueryParameter(
                message="Course number cannot be empty",
                parameter_name="crs_no",
            )
