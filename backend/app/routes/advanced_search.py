"""
Advanced search API routes.

Provides advanced filtering, statistics, and search suggestions.
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.course import CourseResponse
from app.services.advanced_search_service import AdvancedSearchService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/filter", response_model=dict, status_code=status.HTTP_200_OK)
async def advanced_filter(
    session: Annotated[AsyncSession, Depends(get_session)],
    semesters: Optional[list[int]] = Query(None, description="List of semester IDs (e.g., 110, 111)"),
    departments: Optional[list[str]] = Query(None, description="List of department codes"),
    teachers: Optional[list[str]] = Query(None, description="List of teacher names"),
    min_credits: Optional[float] = Query(None, ge=0, description="Minimum credits"),
    max_credits: Optional[float] = Query(None, ge=0, description="Maximum credits"),
    keywords: Optional[list[str]] = Query(None, description="Keywords to search"),
    limit: int = Query(200, ge=1, le=10000, description="Max results"),
    offset: int = Query(0, ge=0, description="Result offset"),
):
    """
    Advanced course filtering with multiple criteria.

    Example:
        POST /api/advanced/filter?semesters=110&semesters=1&departments=CS&min_credits=3&max_credits=4
    """
    try:
        service = AdvancedSearchService(session)

        # Convert semester IDs to (year, semester) tuples
        # e.g., 110 -> (110, 1), 1102 -> (110, 2)
        semester_tuples = None
        if semesters:
            semester_tuples = []
            for sem_id in semesters:
                year = sem_id // 10
                semester = sem_id % 10
                semester_tuples.append((year, semester))

        # Parse credits range
        credits_range = None
        if min_credits is not None or max_credits is not None:
            credits_range = (
                min_credits or 0,
                max_credits or 10,
            )

        courses, total = await service.advanced_filter(
            semesters=semester_tuples,
            departments=departments,
            teachers=teachers,
            credits=credits_range,
            keywords=keywords,
            limit=limit,
            offset=offset,
        )

        return {
            "courses": [
                CourseResponse(
                    id=c.id,
                    acy=c.semester.acy if c.semester else None,
                    sem=c.semester.sem if c.semester else None,
                    crs_no=c.crs_no,
                    name=c.name,
                    teacher=c.teacher,
                    credits=c.credits,
                    dept=c.dept,
                    time=c.time,
                    classroom=c.classroom,
                    details=c.details,
                )
                for c in courses
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        logger.error(f"Advanced filter error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/stats", response_model=dict, status_code=status.HTTP_200_OK)
async def get_statistics(
    session: Annotated[AsyncSession, Depends(get_session)],
    acy: Annotated[
        Optional[int],
        Query(description="Filter by academic year"),
    ] = None,
    sem: Annotated[
        Optional[int],
        Query(description="Filter by semester", ge=1, le=2),
    ] = None,
):
    """
    Get course statistics and analytics.

    Example:
        GET /api/advanced/stats?acy=113&sem=1
    """
    try:
        service = AdvancedSearchService(session)
        stats = await service.get_statistics(acy=acy, sem=sem)
        return stats

    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/search", response_model=dict, status_code=status.HTTP_200_OK)
async def search_with_suggestions(
    session: Annotated[AsyncSession, Depends(get_session)],
    q: Annotated[
        str,
        Query(description="Search query", min_length=1, max_length=200),
    ],
    limit: Annotated[
        int,
        Query(description="Max results", ge=1, le=500),
    ] = 50,
):
    """
    Search courses with suggestions.

    Example:
        GET /api/advanced/search?q=computer%20science&limit=20
    """
    try:
        service = AdvancedSearchService(session)
        result = await service.search_with_suggestions(query=q, limit=limit)

        return {
            "results": [
                CourseResponse(
                    id=c.id,
                    acy=c.semester.acy if c.semester else None,
                    sem=c.semester.sem if c.semester else None,
                    crs_no=c.crs_no,
                    name=c.name,
                    teacher=c.teacher,
                    credits=c.credits,
                    dept=c.dept,
                    time=c.time,
                    classroom=c.classroom,
                    details=c.details,
                )
                for c in result["results"]
            ],
            "suggestions": result["suggestions"],
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/recommend/{course_id}", response_model=list[CourseResponse])
async def get_recommendations(
    course_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[
        int,
        Query(description="Max recommendations", ge=1, le=100),
    ] = 5,
):
    """
    Get course recommendations based on a course.

    Example:
        GET /api/advanced/recommend/123?limit=10
    """
    try:
        service = AdvancedSearchService(session)
        courses = await service.get_course_recommendations(
            course_id=course_id,
            limit=limit,
        )

        return [
            CourseResponse(
                id=c.id,
                acy=c.semester.acy if c.semester else None,
                sem=c.semester.sem if c.semester else None,
                crs_no=c.crs_no,
                name=c.name,
                teacher=c.teacher,
                credits=c.credits,
                dept=c.dept,
                time=c.time,
                classroom=c.classroom,
                details=c.details,
            )
            for c in courses
        ]

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
