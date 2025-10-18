"""
Database operations for schedules.

This module provides CRUD operations for Schedule and ScheduleCourse models.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.course import Course
from app.models.schedule import Schedule, ScheduleCourse
from app.utils.exceptions import DatabaseError, ScheduleNotFound

logger = logging.getLogger(__name__)


async def create_schedule(
    session: AsyncSession,
    name: str,
    acy: int,
    sem: int,
    user_id: Optional[str] = None,
) -> Schedule:
    """
    Create a new schedule.

    Args:
        session: Database session
        name: Schedule name
        acy: Academic year
        sem: Semester
        user_id: Optional user identifier

    Returns:
        Created Schedule object

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        schedule = Schedule(
            name=name,
            acy=acy,
            sem=sem,
            user_id=user_id,
        )
        session.add(schedule)
        await session.commit()
        await session.refresh(schedule)

        # Eagerly load schedule_courses to avoid lazy loading issues
        await session.refresh(schedule, ["schedule_courses"])

        logger.info(f"Created schedule {schedule.id}: {name}")
        return schedule

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to create schedule: {e}")
        raise DatabaseError(f"Failed to create schedule: {str(e)}")


async def get_schedule(
    session: AsyncSession, schedule_id: int, include_courses: bool = False
) -> Schedule:
    """
    Get a schedule by ID.

    Args:
        session: Database session
        schedule_id: Schedule ID
        include_courses: Whether to eagerly load courses

    Returns:
        Schedule object

    Raises:
        ScheduleNotFound: If schedule doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        statement = select(Schedule).where(Schedule.id == schedule_id)

        if include_courses:
            statement = statement.options(
                selectinload(Schedule.schedule_courses).joinedload(ScheduleCourse.course).joinedload(Course.semester)
            )

        result = await session.execute(statement)
        schedule = result.scalars().first()

        if not schedule:
            raise ScheduleNotFound(f"Schedule with ID {schedule_id} not found")

        return schedule

    except ScheduleNotFound:
        raise
    except Exception as e:
        logger.error(f"Failed to get schedule {schedule_id}: {e}")
        raise DatabaseError(f"Failed to retrieve schedule: {str(e)}")


async def get_user_schedules(
    session: AsyncSession,
    user_id: str,
    acy: Optional[int] = None,
    sem: Optional[int] = None,
) -> list[Schedule]:
    """
    Get all schedules for a user.

    Args:
        session: Database session
        user_id: User identifier
        acy: Optional filter by academic year
        sem: Optional filter by semester

    Returns:
        List of Schedule objects

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        statement = select(Schedule).where(Schedule.user_id == user_id)

        if acy is not None:
            statement = statement.where(Schedule.acy == acy)
        if sem is not None:
            statement = statement.where(Schedule.sem == sem)

        statement = statement.order_by(Schedule.updated_at.desc())

        result = await session.execute(statement)
        schedules = result.scalars().all()

        logger.info(f"Retrieved {len(schedules)} schedules for user {user_id}")
        return list(schedules)

    except Exception as e:
        logger.error(f"Failed to get schedules for user {user_id}: {e}")
        raise DatabaseError(f"Failed to retrieve schedules: {str(e)}")


async def update_schedule(
    session: AsyncSession, schedule_id: int, name: Optional[str] = None
) -> Schedule:
    """
    Update a schedule.

    Args:
        session: Database session
        schedule_id: Schedule ID
        name: New schedule name

    Returns:
        Updated Schedule object

    Raises:
        ScheduleNotFound: If schedule doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        schedule = await get_schedule(session, schedule_id)

        if name is not None:
            schedule.name = name

        schedule.updated_at = datetime.utcnow()

        session.add(schedule)
        await session.commit()
        await session.refresh(schedule)

        logger.info(f"Updated schedule {schedule_id}")
        return schedule

    except ScheduleNotFound:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to update schedule {schedule_id}: {e}")
        raise DatabaseError(f"Failed to update schedule: {str(e)}")


async def delete_schedule(session: AsyncSession, schedule_id: int) -> None:
    """
    Delete a schedule.

    Args:
        session: Database session
        schedule_id: Schedule ID

    Raises:
        ScheduleNotFound: If schedule doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        schedule = await get_schedule(session, schedule_id)

        await session.delete(schedule)
        await session.commit()

        logger.info(f"Deleted schedule {schedule_id}")

    except ScheduleNotFound:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to delete schedule {schedule_id}: {e}")
        raise DatabaseError(f"Failed to delete schedule: {str(e)}")


async def add_course_to_schedule(
    session: AsyncSession,
    schedule_id: int,
    course_id: int,
    color: Optional[str] = None,
    notes: Optional[str] = None,
) -> ScheduleCourse:
    """
    Add a course to a schedule.

    Args:
        session: Database session
        schedule_id: Schedule ID
        course_id: Course ID
        color: Optional display color
        notes: Optional user notes

    Returns:
        Created ScheduleCourse object

    Raises:
        ScheduleNotFound: If schedule doesn't exist
        DatabaseError: If course doesn't exist or database operation fails
    """
    try:
        # Verify schedule exists
        await get_schedule(session, schedule_id)

        # Verify course exists
        course_result = await session.execute(select(Course).where(Course.id == course_id))
        course = course_result.scalars().first()
        if not course:
            raise DatabaseError(f"Course with ID {course_id} not found")

        # Check if course already in schedule
        existing = await session.execute(
            select(ScheduleCourse).where(
                ScheduleCourse.schedule_id == schedule_id,
                ScheduleCourse.course_id == course_id,
            )
        )
        if existing.scalars().first():
            raise DatabaseError(f"Course {course_id} is already in schedule {schedule_id}")

        # Add course to schedule
        schedule_course = ScheduleCourse(
            schedule_id=schedule_id,
            course_id=course_id,
            color=color,
            notes=notes,
        )
        session.add(schedule_course)

        # Update schedule timestamp
        schedule = await get_schedule(session, schedule_id)
        schedule.updated_at = datetime.utcnow()
        session.add(schedule)

        await session.commit()
        await session.refresh(schedule_course)

        logger.info(f"Added course {course_id} to schedule {schedule_id}")
        return schedule_course

    except (ScheduleNotFound, DatabaseError):
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to add course {course_id} to schedule {schedule_id}: {e}")
        raise DatabaseError(f"Failed to add course to schedule: {str(e)}")


async def remove_course_from_schedule(
    session: AsyncSession, schedule_id: int, course_id: int
) -> None:
    """
    Remove a course from a schedule.

    Args:
        session: Database session
        schedule_id: Schedule ID
        course_id: Course ID

    Raises:
        ScheduleNotFound: If schedule doesn't exist
        DatabaseError: If course not in schedule or database operation fails
    """
    try:
        # Verify schedule exists
        await get_schedule(session, schedule_id)

        # Find schedule course
        result = await session.execute(
            select(ScheduleCourse).where(
                ScheduleCourse.schedule_id == schedule_id,
                ScheduleCourse.course_id == course_id,
            )
        )
        schedule_course = result.scalars().first()

        if not schedule_course:
            raise DatabaseError(f"Course {course_id} not found in schedule {schedule_id}")

        # Remove course
        await session.delete(schedule_course)

        # Update schedule timestamp
        schedule = await get_schedule(session, schedule_id)
        schedule.updated_at = datetime.utcnow()
        session.add(schedule)

        await session.commit()

        logger.info(f"Removed course {course_id} from schedule {schedule_id}")

    except (ScheduleNotFound, DatabaseError):
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to remove course {course_id} from schedule {schedule_id}: {e}")
        raise DatabaseError(f"Failed to remove course from schedule: {str(e)}")


async def update_schedule_course(
    session: AsyncSession,
    schedule_id: int,
    course_id: int,
    color: Optional[str] = None,
    notes: Optional[str] = None,
) -> ScheduleCourse:
    """
    Update a course in a schedule.

    Args:
        session: Database session
        schedule_id: Schedule ID
        course_id: Course ID
        color: Optional new display color
        notes: Optional new notes

    Returns:
        Updated ScheduleCourse object

    Raises:
        ScheduleNotFound: If schedule doesn't exist
        DatabaseError: If course not in schedule or database operation fails
    """
    try:
        # Verify schedule exists
        await get_schedule(session, schedule_id)

        # Find schedule course
        result = await session.execute(
            select(ScheduleCourse).where(
                ScheduleCourse.schedule_id == schedule_id,
                ScheduleCourse.course_id == course_id,
            )
        )
        schedule_course = result.scalars().first()

        if not schedule_course:
            raise DatabaseError(f"Course {course_id} not found in schedule {schedule_id}")

        # Update fields
        if color is not None:
            schedule_course.color = color
        if notes is not None:
            schedule_course.notes = notes

        session.add(schedule_course)

        # Update schedule timestamp
        schedule = await get_schedule(session, schedule_id)
        schedule.updated_at = datetime.utcnow()
        session.add(schedule)

        await session.commit()
        await session.refresh(schedule_course)

        logger.info(f"Updated course {course_id} in schedule {schedule_id}")
        return schedule_course

    except (ScheduleNotFound, DatabaseError):
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to update course {course_id} in schedule {schedule_id}: {e}")
        raise DatabaseError(f"Failed to update course in schedule: {str(e)}")
