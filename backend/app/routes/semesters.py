"""
Semester API routes.

This module defines FastAPI routes for semester-related operations including
listing all semesters and retrieving individual semester details.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.semester import SemesterResponse
from app.services.semester_service import SemesterService
from app.utils.exceptions import DatabaseError, SemesterNotFound

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/", response_model=list[SemesterResponse], status_code=status.HTTP_200_OK)
async def list_semesters(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[SemesterResponse]:
    """
    List all semesters.

    Retrieves all semesters from the database, ordered by most recent first
    (descending by academic year and semester number).

    Args:
        session: Database session (injected)

    Returns:
        list[SemesterResponse]: List of all semester records

    Raises:
        HTTPException: 500 if database operation fails

    Example:
        GET /api/semesters/

        Response:
        [
            {
                "id": 2,
                "acy": 113,
                "sem": 2
            },
            {
                "id": 1,
                "acy": 113,
                "sem": 1
            }
        ]
    """
    try:
        service = SemesterService(session)
        semesters = await service.list_semesters()

        logger.info(f"Successfully listed {len(semesters)} semesters")

        return [
            SemesterResponse(
                id=semester.id,
                acy=semester.acy,
                sem=semester.sem,
            )
            for semester in semesters
        ]

    except DatabaseError as e:
        logger.error(f"Database error while listing semesters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve semesters: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while listing semesters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving semesters",
        )


@router.get(
    "/{semester_id}",
    response_model=SemesterResponse,
    status_code=status.HTTP_200_OK,
)
async def get_semester(
    semester_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SemesterResponse:
    """
    Get a specific semester by ID.

    Retrieves detailed information for a single semester identified by its ID.

    Args:
        semester_id: ID of the semester to retrieve
        session: Database session (injected)

    Returns:
        SemesterResponse: Semester details

    Raises:
        HTTPException: 404 if semester not found
        HTTPException: 500 if database operation fails

    Example:
        GET /api/semesters/1

        Response:
        {
            "id": 1,
            "acy": 113,
            "sem": 1
        }
    """
    try:
        service = SemesterService(session)
        semester = await service.get_semester_detail(semester_id)

        logger.info(f"Successfully retrieved semester {semester_id}")

        return SemesterResponse(
            id=semester.id,
            acy=semester.acy,
            sem=semester.sem,
        )

    except SemesterNotFound as e:
        logger.warning(f"Semester not found: {semester_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error while retrieving semester {semester_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve semester: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving semester {semester_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the semester",
        )
