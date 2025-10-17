"""
Course API routes.

This module defines FastAPI routes for course-related operations including
listing courses with filtering, searching, and retrieving individual course details.
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_session
from backend.app.schemas.course import CourseResponse
from backend.app.services.course_service import CourseService
from backend.app.utils.exceptions import (
    CourseNotFound,
    DatabaseError,
    InvalidQueryParameter,
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/", response_model=list[CourseResponse], status_code=status.HTTP_200_OK)
async def list_courses(
    session: Annotated[AsyncSession, Depends(get_session)],
    acy: Annotated[
        Optional[int],
        Query(
            description="Filter by academic year",
            gt=0,
            example=113,
        ),
    ] = None,
    sem: Annotated[
        Optional[int],
        Query(
            description="Filter by semester (1=Fall, 2=Spring)",
            ge=1,
            le=2,
            example=1,
        ),
    ] = None,
    dept: Annotated[
        Optional[str],
        Query(
            description="Filter by department code (case-insensitive partial match)",
            max_length=50,
            example="CS",
        ),
    ] = None,
    teacher: Annotated[
        Optional[str],
        Query(
            description="Filter by teacher name (case-insensitive partial match)",
            max_length=100,
            example="Smith",
        ),
    ] = None,
    q: Annotated[
        Optional[str],
        Query(
            description="Search query for course name or number (case-insensitive)",
            max_length=200,
            example="computer science",
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            description="Maximum number of results to return",
            ge=1,
            le=1000,
            example=50,
        ),
    ] = 200,
    offset: Annotated[
        int,
        Query(
            description="Number of results to skip for pagination",
            ge=0,
            example=0,
        ),
    ] = 0,
) -> list[CourseResponse]:
    """
    List courses with optional filtering and pagination.

    Retrieves courses from the database with support for:
    - Filtering by academic year, semester, department, and teacher
    - Full-text search in course name and number
    - Pagination with limit and offset

    Args:
        session: Database session (injected)
        acy: Filter by academic year (exact match)
        sem: Filter by semester number (exact match)
        dept: Filter by department code (partial match)
        teacher: Filter by teacher name (partial match)
        q: Search query for course name or number
        limit: Maximum number of results (default: 200, max: 1000)
        offset: Number of results to skip (default: 0)

    Returns:
        list[CourseResponse]: List of course records matching the filters

    Raises:
        HTTPException: 400 if query parameters are invalid
        HTTPException: 500 if database operation fails

    Example:
        GET /api/courses/?acy=113&sem=1&dept=CS&limit=10

        Response:
        [
            {
                "id": 1,
                "acy": 113,
                "sem": 1,
                "crs_no": "CS1001",
                "name": "Introduction to Computer Science",
                "teacher": "Dr. Alice Smith",
                "credits": 3.0,
                "dept": "CS",
                "time": "Mon 10:00-12:00",
                "classroom": "A101",
                "details": "{\"capacity\": 50}"
            }
        ]
    """
    try:
        service = CourseService(session)
        courses = await service.list_courses(
            acy=acy,
            sem=sem,
            dept=dept,
            teacher=teacher,
            q=q,
            limit=limit,
            offset=offset,
        )

        logger.info(
            f"Successfully listed {len(courses)} courses "
            f"(filters: acy={acy}, sem={sem}, dept={dept}, "
            f"teacher={teacher}, q={q}, limit={limit}, offset={offset})"
        )

        return [
            CourseResponse(
                id=course.id,
                acy=course.acy,
                sem=course.sem,
                crs_no=course.crs_no,
                name=course.name,
                teacher=course.teacher,
                credits=course.credits,
                dept=course.dept,
                time=course.time,
                classroom=course.classroom,
                details=course.details,
            )
            for course in courses
        ]

    except InvalidQueryParameter as e:
        logger.warning(f"Invalid query parameter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error while listing courses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve courses: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while listing courses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving courses",
        )


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
)
async def get_course(
    course_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CourseResponse:
    """
    Get a specific course by ID.

    Retrieves detailed information for a single course identified by its ID.
    The response includes the course details with parsed JSON metadata.

    Args:
        course_id: ID of the course to retrieve
        session: Database session (injected)

    Returns:
        CourseResponse: Course details with parsed metadata

    Raises:
        HTTPException: 404 if course not found
        HTTPException: 500 if database operation fails

    Example:
        GET /api/courses/1

        Response:
        {
            "id": 1,
            "acy": 113,
            "sem": 1,
            "crs_no": "CS1001",
            "name": "Introduction to Computer Science",
            "teacher": "Dr. Alice Smith",
            "credits": 3.0,
            "dept": "CS",
            "time": "Mon 10:00-12:00",
            "classroom": "A101",
            "details": "{\"capacity\": 50, \"enrollment\": 45}"
        }
    """
    try:
        service = CourseService(session)
        course_detail = await service.get_course_detail(course_id)

        logger.info(f"Successfully retrieved course {course_id}")

        return CourseResponse(
            id=course_detail["id"],
            acy=course_detail["acy"],
            sem=course_detail["sem"],
            crs_no=course_detail["crs_no"],
            name=course_detail["name"],
            teacher=course_detail["teacher"],
            credits=course_detail["credits"],
            dept=course_detail["dept"],
            time=course_detail["time"],
            classroom=course_detail["classroom"],
            details=course_detail["details"],
        )

    except CourseNotFound as e:
        logger.warning(f"Course not found: {course_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error while retrieving course {course_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving course {course_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the course",
        )
