"""
Course database operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for courses
in the database. It includes complex filtering, search, and pagination capabilities.
"""

import logging
from typing import Optional

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.database.base import (
    build_like_filter,
    commit_with_error_handling,
    get_or_404,
    refresh_record,
)
from app.models.course import Course
from app.models.semester import Semester
from app.utils.exceptions import CourseNotFound, DatabaseError

# Set up logging
logger = logging.getLogger(__name__)


async def get_all_courses(
    session: AsyncSession,
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

    This function supports complex filtering with multiple criteria:
    - Exact match for academic year (acy) and semester (sem)
    - Case-insensitive partial match for department (dept)
    - Case-insensitive partial match for teacher name
    - Case-insensitive search in course name and course number (q)

    Args:
        session: Database session
        acy: Filter by academic year (exact match)
        sem: Filter by semester number (exact match)
        dept: Filter by department code (case-insensitive partial match)
        teacher: Filter by teacher name (case-insensitive partial match)
        q: Search query for course name or number (case-insensitive partial match)
        limit: Maximum number of results to return (default: 200)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        List of course records matching the filters

    Raises:
        DatabaseError: If the query fails

    Example:
        >>> # Get all CS courses from Fall 2024 taught by Smith
        >>> courses = await get_all_courses(
        ...     session, acy=113, sem=1, dept="CS", teacher="Smith"
        ... )
        >>> print(f"Found {len(courses)} courses")
    """
    try:
        # Start building the query with joinedload for semester relationship
        statement = select(Course).options(joinedload(Course.semester))

        # Build list of filter conditions
        filters = []

        # Exact match filters - join with Semester table
        if acy is not None:
            statement = statement.join(Semester)
            filters.append(Semester.acy == acy)
            logger.debug(f"Filtering by acy={acy}")

        if sem is not None:
            if acy is None:  # Join only if not already joined
                statement = statement.join(Semester)
            filters.append(Semester.sem == sem)
            logger.debug(f"Filtering by sem={sem}")

        # Case-insensitive LIKE filters
        if dept is not None:
            filters.append(build_like_filter(Course.dept, dept))
            logger.debug(f"Filtering by dept LIKE '%{dept}%'")

        if teacher is not None:
            filters.append(build_like_filter(Course.teacher, teacher))
            logger.debug(f"Filtering by teacher LIKE '%{teacher}%'")

        # Search query (searches in both name and course number)
        if q is not None:
            search_filters = [
                build_like_filter(Course.name, q),
                build_like_filter(Course.crs_no, q),
            ]
            filters.append(or_(*search_filters))
            logger.debug(f"Searching for q='{q}' in name and crs_no")

        # Apply all filters
        if filters:
            statement = statement.where(and_(*filters))

        # Add ordering (by course number for consistent results)
        statement = statement.order_by(Course.crs_no)

        # Add pagination
        statement = statement.limit(limit).offset(offset)

        # Execute query
        result = await session.execute(statement)
        courses = result.scalars().all()

        logger.info(
            f"Retrieved {len(courses)} courses "
            f"(limit={limit}, offset={offset}, filters={len(filters)})"
        )
        return list(courses)

    except Exception as e:
        logger.error(f"Failed to retrieve courses: {e}")
        raise DatabaseError(
            message="Failed to retrieve courses",
            original_error=e,
        )


async def get_course(session: AsyncSession, course_id: int) -> Course:
    """
    Retrieve a single course by its ID.

    Args:
        session: Database session
        course_id: ID of the course to retrieve

    Returns:
        Course record

    Raises:
        CourseNotFound: If course with given ID doesn't exist
        DatabaseError: If the query fails

    Example:
        >>> course = await get_course(session, 123)
        >>> print(f"Course: {course.name}")
    """
    logger.debug(f"Fetching course with ID: {course_id}")
    try:
        statement = select(Course).options(joinedload(Course.semester)).where(Course.id == course_id)
        result = await session.execute(statement)
        course = result.scalar_one_or_none()

        if course is None:
            from app.utils.exceptions import CourseNotFound
            raise CourseNotFound(message=f"Course with ID {course_id} not found")

        return course
    except CourseNotFound:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve course {course_id}: {e}")
        raise DatabaseError(
            message=f"Failed to retrieve course {course_id}",
            original_error=e,
        )


async def get_courses_by_semester(
    session: AsyncSession,
    acy: int,
    sem: int,
) -> list[Course]:
    """
    Retrieve all courses for a specific semester.

    Args:
        session: Database session
        acy: Academic year
        sem: Semester number

    Returns:
        List of all courses in the specified semester

    Raises:
        DatabaseError: If the query fails

    Example:
        >>> courses = await get_courses_by_semester(session, 113, 1)
        >>> print(f"Found {len(courses)} courses in Fall 2024")
    """
    try:
        statement = (
            select(Course)
            .options(joinedload(Course.semester))
            .join(Semester)
            .where(Semester.acy == acy, Semester.sem == sem)
            .order_by(Course.crs_no)
        )

        result = await session.execute(statement)
        courses = result.scalars().all()

        logger.info(f"Retrieved {len(courses)} courses for acy={acy}, sem={sem}")
        return list(courses)

    except Exception as e:
        logger.error(f"Failed to retrieve courses for semester: {e}")
        raise DatabaseError(
            message=f"Failed to retrieve courses for acy={acy}, sem={sem}",
            original_error=e,
        )


async def search_courses(
    session: AsyncSession,
    query: str,
    limit: int = 100,
) -> list[Course]:
    """
    Search for courses by name or course number.

    This is a convenience function for full-text search across
    course names and course numbers.

    Args:
        session: Database session
        query: Search query string
        limit: Maximum number of results (default: 100)

    Returns:
        List of courses matching the search query

    Raises:
        DatabaseError: If the query fails

    Example:
        >>> courses = await search_courses(session, "computer science")
        >>> for course in courses:
        ...     print(f"{course.crs_no}: {course.name}")
    """
    try:
        statement = (
            select(Course)
            .options(joinedload(Course.semester))
            .where(
                or_(
                    build_like_filter(Course.name, query),
                    build_like_filter(Course.crs_no, query),
                )
            )
            .order_by(Course.crs_no)
            .limit(limit)
        )

        result = await session.execute(statement)
        courses = result.scalars().all()

        logger.info(f"Search for '{query}' returned {len(courses)} courses")
        return list(courses)

    except Exception as e:
        logger.error(f"Failed to search courses: {e}")
        raise DatabaseError(
            message=f"Failed to search courses with query: {query}",
            original_error=e,
        )


async def create_course(
    session: AsyncSession,
    semester_id: int,
    crs_no: str,
    name: str,
    permanent_crs_no: Optional[str] = None,
    teacher: Optional[str] = None,
    credits: Optional[float] = None,
    required: Optional[str] = None,
    dept: Optional[str] = None,
    day_codes: Optional[str] = None,
    time_codes: Optional[str] = None,
    classroom_codes: Optional[str] = None,
    url: Optional[str] = None,
    syllabus: Optional[str] = None,
    syllabus_zh: Optional[str] = None,
    details: Optional[str] = None,
) -> Course:
    """
    Create a new course in the database.

    Args:
        session: Database session
        semester_id: Semester ID (foreign key)
        crs_no: Course number (required)
        name: Course name/title (required)
        permanent_crs_no: Permanent course number
        teacher: Instructor name(s)
        credits: Number of credits
        required: Required/elective status
        dept: Department code
        day_codes: Day codes
        time_codes: Time codes
        classroom_codes: Classroom codes
        url: Course URL
        syllabus: Course syllabus/outline
        syllabus_zh: Course syllabus in Traditional Chinese
        details: JSON string with additional metadata

    Returns:
        Newly created course record

    Raises:
        DatabaseError: If creation fails

    Example:
        >>> course = await create_course(
        ...     session,
        ...     semester_id=1,
        ...     crs_no="CS3101",
        ...     name="Introduction to Computer Science",
        ...     teacher="Dr. Smith",
        ...     credits=3.0,
        ...     dept="CS",
        ... )
        >>> print(f"Created course with ID: {course.id}")
    """
    try:
        # Create new course instance
        course = Course(
            semester_id=semester_id,
            crs_no=crs_no,
            name=name,
            permanent_crs_no=permanent_crs_no,
            teacher=teacher,
            credits=credits,
            required=required,
            dept=dept,
            day_codes=day_codes,
            time_codes=time_codes,
            classroom_codes=classroom_codes,
            url=url,
            syllabus=syllabus,
            syllabus_zh=syllabus_zh,
            details=details,
        )
        session.add(course)

        # Commit and refresh to get the ID
        await commit_with_error_handling(
            session,
            error_message=f"Failed to create course: {crs_no}",
        )
        await refresh_record(
            session,
            course,
            error_message="Failed to refresh course after creation",
        )

        logger.info(f"Created course: id={course.id}, crs_no={crs_no}, name={name}")
        return course

    except DatabaseError:
        # Re-raise DatabaseError as-is
        raise
    except Exception as e:
        # Catch any other exceptions
        logger.error(f"Unexpected error creating course: {e}")
        raise DatabaseError(
            message=f"Failed to create course: {crs_no}",
            original_error=e,
        )


async def update_course(
    session: AsyncSession,
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

    Note: Academic year (acy), semester (sem), and course number (crs_no)
    cannot be updated as they are identifying fields.

    Args:
        session: Database session
        course_id: ID of the course to update
        name: New course name
        teacher: New instructor name(s)
        credits: New number of credits
        dept: New department code
        time: New time/schedule code
        classroom: New classroom location
        details: New JSON string with metadata

    Returns:
        Updated course record

    Raises:
        CourseNotFound: If course with given ID doesn't exist
        DatabaseError: If update fails

    Example:
        >>> course = await update_course(
        ...     session,
        ...     course_id=123,
        ...     teacher="Dr. Johnson",
        ...     classroom="B202",
        ... )
        >>> print(f"Updated course: {course.name}")
    """
    # Fetch the course (raises CourseNotFound if not exists)
    course = await get_course(session, course_id)

    try:
        # Update fields if provided
        if name is not None:
            course.name = name
        if teacher is not None:
            course.teacher = teacher
        if credits is not None:
            course.credits = credits
        if dept is not None:
            course.dept = dept
        if time is not None:
            course.time = time
        if classroom is not None:
            course.classroom = classroom
        if details is not None:
            course.details = details

        # Commit changes
        await commit_with_error_handling(
            session,
            error_message=f"Failed to update course {course_id}",
        )
        await refresh_record(session, course)

        logger.info(f"Updated course: id={course_id}, crs_no={course.crs_no}")
        return course

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating course {course_id}: {e}")
        raise DatabaseError(
            message=f"Failed to update course {course_id}",
            original_error=e,
        )


async def delete_course(session: AsyncSession, course_id: int) -> None:
    """
    Delete a course from the database.

    Args:
        session: Database session
        course_id: ID of the course to delete

    Raises:
        CourseNotFound: If course with given ID doesn't exist
        DatabaseError: If deletion fails

    Example:
        >>> await delete_course(session, 123)
        >>> print("Course deleted successfully")
    """
    # Fetch the course (raises CourseNotFound if not exists)
    course = await get_course(session, course_id)

    try:
        await session.delete(course)
        await commit_with_error_handling(
            session,
            error_message=f"Failed to delete course {course_id}",
        )
        logger.info(f"Deleted course: id={course_id}, crs_no={course.crs_no}")

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting course {course_id}: {e}")
        raise DatabaseError(
            message=f"Failed to delete course {course_id}",
            original_error=e,
        )
