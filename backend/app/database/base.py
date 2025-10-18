"""
Base database operations module.

This module provides common database operations and helper functions that are used
across different database modules. It includes utility functions for fetching records
with proper error handling and common query patterns.
"""

import logging
from typing import Any, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import SQLModel

from app.utils.exceptions import CourseNotFound, DatabaseError, SemesterNotFound

# Set up logging
logger = logging.getLogger(__name__)

# Generic type variable for SQLModel subclasses
T = TypeVar("T", bound=SQLModel)


async def get_or_404(
    session: AsyncSession,
    model: Type[T],
    record_id: int,
    error_message: str | None = None,
) -> T:
    """
    Fetch a record by ID or raise an appropriate not found exception.

    This is a convenience function that fetches a record from the database
    and raises a domain-specific exception if the record is not found.

    Args:
        session: Database session
        model: SQLModel class to query
        record_id: Primary key ID of the record to fetch
        error_message: Optional custom error message

    Returns:
        The fetched record

    Raises:
        CourseNotFound: If model is Course and record is not found
        SemesterNotFound: If model is Semester and record is not found
        DatabaseError: If a database error occurs during the operation

    Example:
        >>> from app.models.course import Course
        >>> course = await get_or_404(session, Course, 123)
    """
    try:
        # Execute query to fetch record by ID
        statement = select(model).where(model.id == record_id)
        result = await session.execute(statement)
        record = result.scalar_one_or_none()

        if record is None:
            # Determine which exception to raise based on model type
            model_name = model.__name__
            default_message = f"{model_name} not found"
            message = error_message or default_message

            if model_name == "Course":
                raise CourseNotFound(message=message, course_id=record_id)
            elif model_name == "Semester":
                raise SemesterNotFound(message=message, semester_id=record_id)
            else:
                raise ValueError(f"Record with ID {record_id} not found")

        logger.debug(f"Fetched {model_name} record with ID {record_id}")
        return record

    except (CourseNotFound, SemesterNotFound):
        # Re-raise domain exceptions as-is
        raise
    except Exception as e:
        # Wrap any other exceptions as DatabaseError
        logger.error(f"Database error while fetching {model.__name__} with ID {record_id}: {e}")
        raise DatabaseError(
            message=f"Failed to fetch {model.__name__} record",
            original_error=e,
        )


async def execute_query(
    session: AsyncSession,
    statement: Any,
    error_message: str = "Query execution failed",
) -> Any:
    """
    Execute a SQLAlchemy query with error handling.

    This helper function wraps query execution in a try-except block
    and converts database exceptions to DatabaseError.

    Args:
        session: Database session
        statement: SQLAlchemy statement to execute
        error_message: Custom error message for exceptions

    Returns:
        Query result

    Raises:
        DatabaseError: If the query execution fails

    Example:
        >>> statement = select(Course).where(Course.acy == 113)
        >>> result = await execute_query(session, statement)
    """
    try:
        result = await session.execute(statement)
        return result
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise DatabaseError(message=error_message, original_error=e)


async def commit_with_error_handling(
    session: AsyncSession,
    error_message: str = "Failed to commit transaction",
) -> None:
    """
    Commit a database transaction with error handling.

    This helper function wraps session.commit() in error handling
    and automatically rolls back on failure.

    Args:
        session: Database session
        error_message: Custom error message for exceptions

    Raises:
        DatabaseError: If the commit fails

    Example:
        >>> session.add(new_course)
        >>> await commit_with_error_handling(session, "Failed to create course")
    """
    try:
        await session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        logger.error(f"Commit error: {e}")
        await session.rollback()
        raise DatabaseError(message=error_message, original_error=e)


async def refresh_record(
    session: AsyncSession,
    record: T,
    error_message: str = "Failed to refresh record",
) -> T:
    """
    Refresh a database record to get updated values.

    This helper function refreshes a record from the database
    and includes error handling.

    Args:
        session: Database session
        record: Record to refresh
        error_message: Custom error message for exceptions

    Returns:
        Refreshed record

    Raises:
        DatabaseError: If the refresh fails

    Example:
        >>> course = await refresh_record(session, course)
    """
    try:
        await session.refresh(record)
        logger.debug(f"Refreshed record: {record}")
        return record
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        raise DatabaseError(message=error_message, original_error=e)


async def count_records(
    session: AsyncSession,
    model: Type[T],
    where_clause: Any = None,
) -> int:
    """
    Count records in a table with optional filtering.

    Args:
        session: Database session
        model: SQLModel class to query
        where_clause: Optional WHERE clause for filtering

    Returns:
        Number of records

    Raises:
        DatabaseError: If the count query fails

    Example:
        >>> from app.models.course import Course
        >>> count = await count_records(session, Course, Course.acy == 113)
    """
    try:
        from sqlalchemy import func

        statement = select(func.count(model.id))
        if where_clause is not None:
            statement = statement.where(where_clause)

        result = await session.execute(statement)
        count = result.scalar_one()
        logger.debug(f"Counted {count} records in {model.__name__}")
        return count
    except Exception as e:
        logger.error(f"Count query error: {e}")
        raise DatabaseError(
            message=f"Failed to count {model.__name__} records",
            original_error=e,
        )


def build_like_filter(column: Any, value: str, case_insensitive: bool = True) -> Any:
    """
    Build a LIKE filter for SQLAlchemy queries.

    This helper function creates a case-insensitive LIKE filter
    for text search operations.

    Args:
        column: SQLAlchemy column to filter
        value: Value to search for
        case_insensitive: Whether to use case-insensitive search (default: True)

    Returns:
        SQLAlchemy filter expression

    Example:
        >>> from app.models.course import Course
        >>> filter_expr = build_like_filter(Course.name, "computer")
        >>> statement = select(Course).where(filter_expr)
    """
    search_value = f"%{value}%"
    if case_insensitive:
        return column.ilike(search_value)
    return column.like(search_value)
