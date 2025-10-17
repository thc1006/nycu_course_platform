"""
Advanced Course Search API Routes.

POST /api/courses/search - Advanced filtering with full-text search scoring.
Optimized for 70,239+ course records with comprehensive filtering options.
"""

import logging
from enum import Enum
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_session
from backend.app.schemas.course import CourseResponse
from backend.app.services.search_service import SearchService
from backend.app.utils.exceptions import DatabaseError, InvalidQueryParameter

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class SortOption(str, Enum):
    """Sorting options for search results."""

    BY_NAME = "by_name"
    BY_CREDITS = "by_credits"
    BY_TEACHER = "by_teacher"
    BY_RELEVANCE = "by_relevance"
    BY_SEMESTER = "by_semester"


class CourseSearchRequest(BaseModel):
    """
    Request model for advanced course search.

    Supports multiple filtering criteria and full-text search.
    """

    # Text search
    query: Optional[str] = Field(
        None,
        max_length=200,
        description="Full-text search query for course name, number, or teacher"
    )

    # Course identifiers
    crs_no: Optional[str] = Field(
        None,
        max_length=50,
        description="Filter by course number (partial match)"
    )

    # Semester filters
    semester_ids: Optional[list[int]] = Field(
        None,
        description="List of semester IDs to filter (from semesters table)"
    )

    acy: Optional[list[int]] = Field(
        None,
        description="Filter by academic years (e.g., [113, 114])"
    )

    sem: Optional[list[int]] = Field(
        None,
        description="Filter by semester numbers (1=Fall, 2=Spring)"
    )

    # Course attributes
    name: Optional[str] = Field(
        None,
        max_length=200,
        description="Filter by course name (partial match)"
    )

    teacher: Optional[str] = Field(
        None,
        max_length=100,
        description="Filter by teacher name (partial match)"
    )

    dept: Optional[list[str]] = Field(
        None,
        description="Filter by department codes"
    )

    # Credit filters
    credits_min: Optional[float] = Field(
        None,
        ge=0,
        le=20,
        description="Minimum credits"
    )

    credits_max: Optional[float] = Field(
        None,
        ge=0,
        le=20,
        description="Maximum credits"
    )

    exact_credits: Optional[float] = Field(
        None,
        ge=0,
        le=20,
        description="Exact credit value"
    )

    # Time/schedule filters
    day_codes: Optional[list[str]] = Field(
        None,
        description="Filter by day codes (e.g., ['M', 'T', 'W'])"
    )

    # Pagination
    limit: int = Field(
        50,
        ge=1,
        le=1000,
        description="Maximum results to return"
    )

    offset: int = Field(
        0,
        ge=0,
        description="Number of results to skip"
    )

    # Sorting
    sort_by: SortOption = Field(
        SortOption.BY_RELEVANCE,
        description="Sort order for results"
    )

    sort_desc: bool = Field(
        False,
        description="Sort in descending order"
    )

    @field_validator("semester_ids", "acy", "sem", "dept", "day_codes")
    @classmethod
    def validate_list_not_empty(cls, v):
        """Ensure lists are not empty if provided."""
        if v is not None and len(v) == 0:
            raise ValueError("List cannot be empty")
        return v

    @field_validator("credits_min", "credits_max", "exact_credits")
    @classmethod
    def validate_credits(cls, v):
        """Validate credit values."""
        if v is not None and v < 0:
            raise ValueError("Credits cannot be negative")
        return v

    class Config:
        """Model configuration."""

        json_schema_extra = {
            "example": {
                "query": "computer science",
                "dept": ["CS", "ECE"],
                "credits_min": 3,
                "credits_max": 4,
                "semester_ids": [1, 2],
                "limit": 50,
                "offset": 0,
                "sort_by": "by_relevance"
            }
        }


class CourseSearchResponse(BaseModel):
    """
    Response model for course search.

    Includes results, pagination info, and query metadata.
    """

    courses: list[CourseResponse] = Field(
        description="List of courses matching search criteria"
    )

    total: int = Field(
        description="Total number of matching courses (before pagination)"
    )

    limit: int = Field(
        description="Page size used"
    )

    offset: int = Field(
        description="Offset used"
    )

    page: int = Field(
        description="Current page number (1-indexed)"
    )

    total_pages: int = Field(
        description="Total number of pages"
    )

    has_next: bool = Field(
        description="Whether there are more results"
    )

    has_previous: bool = Field(
        description="Whether there are previous results"
    )

    query_time_ms: float = Field(
        description="Query execution time in milliseconds"
    )

    filters_applied: dict = Field(
        description="Summary of filters applied"
    )


@router.post(
    "/search",
    response_model=CourseSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Advanced course search with filtering",
    description="""
    Advanced course search endpoint supporting:
    - Full-text search across course names, numbers, and teachers
    - Multiple filter criteria (department, credits, semester, etc.)
    - Flexible sorting options
    - Optimized for 70,000+ course records
    - Result caching with TTL
    - Pagination support
    """,
    response_description="Paginated search results with metadata",
)
async def search_courses(
    request: CourseSearchRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CourseSearchResponse:
    """
    Advanced course search with comprehensive filtering.

    This endpoint is optimized for searching through 70,239 courses with:
    - Database indexes on frequently queried fields
    - Result caching with configurable TTL
    - Query optimization and connection pooling
    - Full-text search scoring

    Args:
        request: Search request with filter criteria
        session: Database session (injected)

    Returns:
        CourseSearchResponse: Paginated results with metadata

    Raises:
        HTTPException: 400 if request validation fails
        HTTPException: 500 if database operation fails

    Example Request:
        POST /api/courses/search
        {
            "query": "algorithms",
            "dept": ["CS"],
            "credits_min": 3,
            "acy": [113, 114],
            "limit": 20,
            "sort_by": "by_name"
        }

    Example Response:
        {
            "courses": [...],
            "total": 127,
            "limit": 20,
            "offset": 0,
            "page": 1,
            "total_pages": 7,
            "has_next": true,
            "has_previous": false,
            "query_time_ms": 45.2,
            "filters_applied": {
                "query": "algorithms",
                "dept": ["CS"],
                "credits_range": [3, null],
                "acy": [113, 114]
            }
        }
    """
    try:
        import time
        start_time = time.time()

        # Validate request
        if request.credits_min and request.credits_max:
            if request.credits_min > request.credits_max:
                raise InvalidQueryParameter(
                    message="credits_min cannot be greater than credits_max",
                    parameter_name="credits_min"
                )

        # Initialize search service
        service = SearchService(session)

        # Perform search
        courses, total = await service.advanced_search(
            query=request.query,
            crs_no=request.crs_no,
            semester_ids=request.semester_ids,
            acy=request.acy,
            sem=request.sem,
            name=request.name,
            teacher=request.teacher,
            dept=request.dept,
            credits_min=request.credits_min,
            credits_max=request.credits_max,
            exact_credits=request.exact_credits,
            day_codes=request.day_codes,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by.value,
            sort_desc=request.sort_desc,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

        # Calculate pagination metadata
        page = (request.offset // request.limit) + 1
        total_pages = (total + request.limit - 1) // request.limit if total > 0 else 0
        has_next = request.offset + request.limit < total
        has_previous = request.offset > 0

        # Build filters summary
        filters_applied = {}
        if request.query:
            filters_applied["query"] = request.query
        if request.crs_no:
            filters_applied["crs_no"] = request.crs_no
        if request.semester_ids:
            filters_applied["semester_ids"] = request.semester_ids
        if request.acy:
            filters_applied["acy"] = request.acy
        if request.sem:
            filters_applied["sem"] = request.sem
        if request.name:
            filters_applied["name"] = request.name
        if request.teacher:
            filters_applied["teacher"] = request.teacher
        if request.dept:
            filters_applied["dept"] = request.dept
        if request.credits_min or request.credits_max:
            filters_applied["credits_range"] = [request.credits_min, request.credits_max]
        if request.exact_credits:
            filters_applied["exact_credits"] = request.exact_credits
        if request.day_codes:
            filters_applied["day_codes"] = request.day_codes

        logger.info(
            f"Search completed: {len(courses)} results (total: {total}), "
            f"query_time: {query_time_ms:.2f}ms, filters: {len(filters_applied)}"
        )

        return CourseSearchResponse(
            courses=[
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
            ],
            total=total,
            limit=request.limit,
            offset=request.offset,
            page=page,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
            query_time_ms=query_time_ms,
            filters_applied=filters_applied,
        )

    except InvalidQueryParameter as e:
        logger.warning(f"Invalid search parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search operation failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during search",
        )


@router.get(
    "/popular-departments",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get popular departments with course counts",
)
async def get_popular_departments(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100, description="Number of departments")] = 20,
) -> dict:
    """
    Get most popular departments by course count.

    Results are cached for 1 hour for performance.

    Args:
        session: Database session (injected)
        limit: Number of departments to return

    Returns:
        Dictionary with department statistics

    Example Response:
        {
            "departments": [
                {"code": "CS", "count": 245, "percentage": 12.5},
                {"code": "ECE", "count": 189, "percentage": 9.6}
            ],
            "total_departments": 48,
            "total_courses": 70239
        }
    """
    try:
        service = SearchService(session)
        stats = await service.get_department_stats(limit=limit)

        logger.info(f"Retrieved {len(stats['departments'])} popular departments")
        return stats

    except Exception as e:
        logger.error(f"Error getting department stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve department statistics",
        )


@router.get(
    "/autocomplete",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get autocomplete suggestions",
)
async def get_autocomplete(
    session: Annotated[AsyncSession, Depends(get_session)],
    q: Annotated[str, Query(min_length=1, max_length=100, description="Query string")] = "",
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> dict:
    """
    Get autocomplete suggestions for search queries.

    Returns suggestions from course names, teachers, and departments.

    Args:
        session: Database session (injected)
        q: Query string for autocomplete
        limit: Maximum suggestions to return

    Returns:
        Dictionary with autocomplete suggestions

    Example Response:
        {
            "suggestions": [
                {"type": "course", "value": "Computer Science Fundamentals", "match": "Computer Science"},
                {"type": "teacher", "value": "Dr. Smith", "match": "Smith"},
                {"type": "department", "value": "CS", "match": "CS"}
            ]
        }
    """
    try:
        service = SearchService(session)
        suggestions = await service.get_autocomplete_suggestions(
            query=q,
            limit=limit
        )

        logger.info(f"Autocomplete: '{q}' -> {len(suggestions)} suggestions")
        return {"suggestions": suggestions}

    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get autocomplete suggestions",
        )
