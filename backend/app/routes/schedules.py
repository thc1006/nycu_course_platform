"""
Schedule API routes.

This module defines FastAPI routes for schedule (timetable) operations including
creating schedules, adding/removing courses, and retrieving schedule details.
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.schemas.schedule import (
    AddCourseRequest,
    RemoveCourseRequest,
    ScheduleCreate,
    ScheduleDetailResponse,
    ScheduleResponse,
    ScheduleUpdate,
)
from app.services.schedule_service import ScheduleService
from app.utils.exceptions import DatabaseError, ScheduleNotFound

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScheduleResponse:
    """
    Create a new schedule.

    Creates a new course schedule (timetable) for a specific academic year and semester.

    Args:
        schedule_data: Schedule creation data
        session: Database session (injected)

    Returns:
        ScheduleResponse: Created schedule details

    Raises:
        HTTPException: 400 if data invalid, 500 if database operation fails

    Example:
        POST /api/schedules/
        {
            "name": "113-1 我的課表",
            "acy": 113,
            "sem": 1,
            "user_id": "session_abc123"
        }
    """
    try:
        service = ScheduleService(session)
        schedule = await service.create_schedule(
            name=schedule_data.name,
            acy=schedule_data.acy,
            sem=schedule_data.sem,
            user_id=schedule_data.user_id,
        )

        logger.info(f"Created schedule: {schedule['name']}")

        return ScheduleResponse(**schedule)

    except DatabaseError as e:
        logger.error(f"Database error while creating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating schedule",
        )


@router.get("/{schedule_id}", response_model=ScheduleDetailResponse, status_code=status.HTTP_200_OK)
async def get_schedule(
    schedule_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScheduleDetailResponse:
    """
    Get a schedule by ID with all courses.

    Retrieves detailed information for a single schedule including all courses
    in the schedule with their full details.

    Args:
        schedule_id: Schedule ID
        session: Database session (injected)

    Returns:
        ScheduleDetailResponse: Schedule details with all courses

    Raises:
        HTTPException: 404 if schedule not found, 500 if database operation fails

    Example:
        GET /api/schedules/1
    """
    try:
        service = ScheduleService(session)
        schedule = await service.get_schedule(schedule_id, include_courses=True)

        logger.info(f"Retrieved schedule {schedule_id}")

        return ScheduleDetailResponse(**schedule)

    except ScheduleNotFound as e:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error while retrieving schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schedule: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving schedule",
        )


@router.get("/user/{user_id}", response_model=list[ScheduleResponse], status_code=status.HTTP_200_OK)
async def get_user_schedules(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    acy: Annotated[Optional[int], Query(description="Filter by academic year", gt=0)] = None,
    sem: Annotated[Optional[int], Query(description="Filter by semester", ge=1, le=2)] = None,
) -> list[ScheduleResponse]:
    """
    Get all schedules for a user.

    Retrieves all schedules belonging to a specific user, with optional filtering
    by academic year and semester.

    Args:
        user_id: User identifier or session ID
        session: Database session (injected)
        acy: Optional filter by academic year
        sem: Optional filter by semester

    Returns:
        list[ScheduleResponse]: List of user schedules

    Raises:
        HTTPException: 500 if database operation fails

    Example:
        GET /api/schedules/user/session_abc123?acy=113&sem=1
    """
    try:
        service = ScheduleService(session)
        schedules = await service.get_user_schedules(user_id, acy=acy, sem=sem)

        logger.info(f"Retrieved {len(schedules)} schedules for user {user_id}")

        return [ScheduleResponse(**schedule) for schedule in schedules]

    except DatabaseError as e:
        logger.error(f"Database error while retrieving schedules for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schedules: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving schedules for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving schedules",
        )


@router.patch("/{schedule_id}", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScheduleResponse:
    """
    Update a schedule.

    Updates schedule properties like name.

    Args:
        schedule_id: Schedule ID
        schedule_data: Update data
        session: Database session (injected)

    Returns:
        ScheduleResponse: Updated schedule details

    Raises:
        HTTPException: 404 if not found, 500 if database operation fails

    Example:
        PATCH /api/schedules/1
        {
            "name": "113-1 更新的課表"
        }
    """
    try:
        service = ScheduleService(session)

        if schedule_data.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update",
            )

        schedule = await service.update_schedule(schedule_id, name=schedule_data.name)

        logger.info(f"Updated schedule {schedule_id}")

        return ScheduleResponse(**schedule)

    except ScheduleNotFound as e:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error while updating schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update schedule: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while updating schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating schedule",
        )


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """
    Delete a schedule.

    Permanently deletes a schedule and all its course associations.

    Args:
        schedule_id: Schedule ID
        session: Database session (injected)

    Raises:
        HTTPException: 404 if not found, 500 if database operation fails

    Example:
        DELETE /api/schedules/1
    """
    try:
        service = ScheduleService(session)
        await service.delete_schedule(schedule_id)

        logger.info(f"Deleted schedule {schedule_id}")

    except ScheduleNotFound as e:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        logger.error(f"Database error while deleting schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete schedule: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while deleting schedule {schedule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting schedule",
        )


@router.post("/{schedule_id}/courses", status_code=status.HTTP_201_CREATED)
async def add_course_to_schedule(
    schedule_id: int,
    request: AddCourseRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """
    Add a course to a schedule.

    Adds a course to the schedule with optional display color and notes.

    Args:
        schedule_id: Schedule ID
        request: Add course request data
        session: Database session (injected)

    Returns:
        dict: Added schedule course details

    Raises:
        HTTPException: 404 if schedule/course not found, 400 if course already in schedule,
                      500 if database operation fails

    Example:
        POST /api/schedules/1/courses
        {
            "course_id": 123,
            "color": "#3B82F6",
            "notes": "重要課程"
        }
    """
    try:
        service = ScheduleService(session)
        schedule_course = await service.add_course(
            schedule_id, request.course_id, color=request.color, notes=request.notes
        )

        logger.info(f"Added course {request.course_id} to schedule {schedule_id}")

        return schedule_course

    except ScheduleNotFound as e:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        # Check if it's a "already exists" error
        if "already in schedule" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        elif "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        logger.error(f"Database error while adding course to schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add course to schedule: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while adding course to schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding course",
        )


@router.delete("/{schedule_id}/courses", status_code=status.HTTP_204_NO_CONTENT)
async def remove_course_from_schedule(
    schedule_id: int,
    request: RemoveCourseRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """
    Remove a course from a schedule.

    Removes a course from the schedule.

    Args:
        schedule_id: Schedule ID
        request: Remove course request data
        session: Database session (injected)

    Raises:
        HTTPException: 404 if schedule/course not found, 500 if database operation fails

    Example:
        DELETE /api/schedules/1/courses
        {
            "course_id": 123
        }
    """
    try:
        service = ScheduleService(session)
        await service.remove_course(schedule_id, request.course_id)

        logger.info(f"Removed course {request.course_id} from schedule {schedule_id}")

    except ScheduleNotFound as e:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DatabaseError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        logger.error(f"Database error while removing course from schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove course from schedule: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while removing course from schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing course",
        )
