"""
Semester database operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for semesters
in the database. All functions use async/await for non-blocking database access.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.base import (
    commit_with_error_handling,
    get_or_404,
    refresh_record,
)
from app.models.semester import Semester
from app.utils.exceptions import DatabaseError, SemesterNotFound

# Set up logging
logger = logging.getLogger(__name__)


async def get_all_semesters(session: AsyncSession) -> list[Semester]:
    """
    Retrieve all semesters from the database, ordered by most recent first.

    Semesters are ordered by academic year (descending) and then by semester
    number (descending), so the most recent semester appears first.

    Args:
        session: Database session

    Returns:
        List of all semester records, ordered by acy DESC, sem DESC

    Raises:
        DatabaseError: If the query fails

    Example:
        >>> semesters = await get_all_semesters(session)
        >>> for semester in semesters:
        ...     print(f"{semester.acy}-{semester.sem}")
    """
    try:
        statement = select(Semester).order_by(Semester.acy.desc(), Semester.sem.desc())
        result = await session.execute(statement)
        semesters = result.scalars().all()
        logger.info(f"Retrieved {len(semesters)} semesters")
        return list(semesters)
    except Exception as e:
        logger.error(f"Failed to retrieve all semesters: {e}")
        raise DatabaseError(
            message="Failed to retrieve semesters",
            original_error=e,
        )


async def get_semester(session: AsyncSession, semester_id: int) -> Semester:
    """
    Retrieve a single semester by its ID.

    Args:
        session: Database session
        semester_id: ID of the semester to retrieve

    Returns:
        Semester record

    Raises:
        SemesterNotFound: If semester with given ID doesn't exist
        DatabaseError: If the query fails

    Example:
        >>> semester = await get_semester(session, 1)
        >>> print(f"Academic Year: {semester.acy}, Semester: {semester.sem}")
    """
    logger.debug(f"Fetching semester with ID: {semester_id}")
    semester = await get_or_404(
        session=session,
        model=Semester,
        record_id=semester_id,
        error_message=f"Semester with ID {semester_id} not found",
    )
    return semester


async def get_semester_by_acy_sem(
    session: AsyncSession,
    acy: int,
    sem: int,
) -> Optional[Semester]:
    """
    Retrieve a semester by academic year and semester number.

    Args:
        session: Database session
        acy: Academic year (e.g., 113 for 2024)
        sem: Semester number (1 for Fall, 2 for Spring)

    Returns:
        Semester record if found, None otherwise

    Raises:
        DatabaseError: If the query fails

    Example:
        >>> semester = await get_semester_by_acy_sem(session, 113, 1)
        >>> if semester:
        ...     print(f"Found semester: {semester.id}")
    """
    try:
        statement = select(Semester).where(
            Semester.acy == acy,
            Semester.sem == sem,
        )
        result = await session.execute(statement)
        semester = result.scalar_one_or_none()

        if semester:
            logger.debug(f"Found semester: acy={acy}, sem={sem}, id={semester.id}")
        else:
            logger.debug(f"No semester found for acy={acy}, sem={sem}")

        return semester
    except Exception as e:
        logger.error(f"Failed to retrieve semester by acy/sem: {e}")
        raise DatabaseError(
            message=f"Failed to retrieve semester for acy={acy}, sem={sem}",
            original_error=e,
        )


async def get_or_create_semester(
    session: AsyncSession,
    acy: int,
    sem: int,
) -> tuple[Semester, bool]:
    """
    Get an existing semester or create it if it doesn't exist.

    This is a convenience function that combines checking for existence
    and creation in a single operation.

    Args:
        session: Database session
        acy: Academic year (e.g., 113 for 2024)
        sem: Semester number (1 for Fall, 2 for Spring)

    Returns:
        Tuple of (semester, created) where created is True if a new
        semester was created, False if it already existed

    Raises:
        DatabaseError: If the operation fails

    Example:
        >>> semester, created = await get_or_create_semester(session, 113, 1)
        >>> if created:
        ...     print("Created new semester")
        ... else:
        ...     print("Semester already exists")
    """
    # Try to get existing semester
    existing = await get_semester_by_acy_sem(session, acy, sem)

    if existing:
        logger.info(f"Semester already exists: acy={acy}, sem={sem}, id={existing.id}")
        return existing, False

    # Create new semester
    logger.info(f"Creating new semester: acy={acy}, sem={sem}")
    new_semester = await create_semester(session, acy, sem)
    return new_semester, True


async def create_semester(
    session: AsyncSession,
    acy: int,
    sem: int,
) -> Semester:
    """
    Create a new semester in the database.

    Args:
        session: Database session
        acy: Academic year (e.g., 113 for 2024)
        sem: Semester number (1 for Fall, 2 for Spring)

    Returns:
        Newly created semester record

    Raises:
        DatabaseError: If creation fails (e.g., duplicate semester)

    Example:
        >>> semester = await create_semester(session, 113, 1)
        >>> print(f"Created semester with ID: {semester.id}")
    """
    try:
        # Create new semester instance
        semester = Semester(acy=acy, sem=sem)
        session.add(semester)

        # Commit and refresh to get the ID
        await commit_with_error_handling(
            session,
            error_message=f"Failed to create semester: acy={acy}, sem={sem}",
        )
        await refresh_record(
            session,
            semester,
            error_message="Failed to refresh semester after creation",
        )

        logger.info(f"Created semester: id={semester.id}, acy={acy}, sem={sem}")
        return semester

    except DatabaseError:
        # Re-raise DatabaseError as-is
        raise
    except Exception as e:
        # Catch any other exceptions (like unique constraint violations)
        logger.error(f"Unexpected error creating semester: {e}")
        raise DatabaseError(
            message=f"Failed to create semester: acy={acy}, sem={sem}",
            original_error=e,
        )


async def update_semester(
    session: AsyncSession,
    semester_id: int,
    acy: Optional[int] = None,
    sem: Optional[int] = None,
) -> Semester:
    """
    Update an existing semester's fields.

    Args:
        session: Database session
        semester_id: ID of the semester to update
        acy: New academic year value (optional)
        sem: New semester number value (optional)

    Returns:
        Updated semester record

    Raises:
        SemesterNotFound: If semester with given ID doesn't exist
        DatabaseError: If update fails

    Example:
        >>> semester = await update_semester(session, 1, acy=114)
        >>> print(f"Updated semester: acy={semester.acy}")
    """
    # Fetch the semester (raises SemesterNotFound if not exists)
    semester = await get_semester(session, semester_id)

    try:
        # Update fields if provided
        if acy is not None:
            semester.acy = acy
            logger.debug(f"Updated semester {semester_id} acy to {acy}")

        if sem is not None:
            semester.sem = sem
            logger.debug(f"Updated semester {semester_id} sem to {sem}")

        # Commit changes
        await commit_with_error_handling(
            session,
            error_message=f"Failed to update semester {semester_id}",
        )
        await refresh_record(session, semester)

        logger.info(f"Updated semester: id={semester_id}")
        return semester

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating semester {semester_id}: {e}")
        raise DatabaseError(
            message=f"Failed to update semester {semester_id}",
            original_error=e,
        )


async def delete_semester(session: AsyncSession, semester_id: int) -> None:
    """
    Delete a semester from the database.

    Note: This will fail if there are courses referencing this semester
    due to foreign key constraints (if implemented).

    Args:
        session: Database session
        semester_id: ID of the semester to delete

    Raises:
        SemesterNotFound: If semester with given ID doesn't exist
        DatabaseError: If deletion fails

    Example:
        >>> await delete_semester(session, 1)
        >>> print("Semester deleted successfully")
    """
    # Fetch the semester (raises SemesterNotFound if not exists)
    semester = await get_semester(session, semester_id)

    try:
        await session.delete(semester)
        await commit_with_error_handling(
            session,
            error_message=f"Failed to delete semester {semester_id}",
        )
        logger.info(f"Deleted semester: id={semester_id}, acy={semester.acy}, sem={semester.sem}")

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting semester {semester_id}: {e}")
        raise DatabaseError(
            message=f"Failed to delete semester {semester_id}",
            original_error=e,
        )
