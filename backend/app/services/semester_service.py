"""
Semester service module.

This module provides business logic for semester operations. It acts as an
intermediary layer between the API routes and the database layer, handling
validation, error handling, and business rules.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import semester as semester_db
from app.models.semester import Semester
from app.utils.exceptions import (
    DatabaseError,
    InvalidQueryParameter,
    SemesterNotFound,
)

# Set up logging
logger = logging.getLogger(__name__)


class SemesterService:
    """
    Service class for semester-related business logic.

    This class encapsulates all business logic related to semesters,
    including validation, data processing, and coordination between
    different database operations.

    Attributes:
        session: AsyncSession for database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize SemesterService.

        Args:
            session: Database session for performing operations
        """
        self.session = session

    async def list_semesters(self) -> list[Semester]:
        """
        Retrieve all semesters ordered by most recent first.

        Returns:
            List of all semester records, ordered by academic year and
            semester number (descending)

        Raises:
            DatabaseError: If the database operation fails

        Example:
            >>> service = SemesterService(session)
            >>> semesters = await service.list_semesters()
            >>> for semester in semesters:
            ...     print(f"{semester.acy}-{semester.sem}")
        """
        logger.info("Listing all semesters")
        try:
            semesters = await semester_db.get_all_semesters(self.session)
            logger.info(f"Successfully retrieved {len(semesters)} semesters")
            return semesters
        except DatabaseError as e:
            logger.error(f"Failed to list semesters: {e}")
            raise

    async def get_semester_detail(self, semester_id: int) -> Semester:
        """
        Retrieve details for a specific semester.

        Args:
            semester_id: ID of the semester to retrieve

        Returns:
            Semester record with all details

        Raises:
            SemesterNotFound: If semester doesn't exist
            DatabaseError: If the database operation fails

        Example:
            >>> service = SemesterService(session)
            >>> semester = await service.get_semester_detail(1)
            >>> print(f"Academic Year: {semester.acy}, Semester: {semester.sem}")
        """
        logger.info(f"Fetching semester detail for ID: {semester_id}")
        try:
            semester = await semester_db.get_semester(self.session, semester_id)
            logger.info(f"Successfully retrieved semester {semester_id}")
            return semester
        except SemesterNotFound as e:
            logger.warning(f"Semester not found: {semester_id}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to get semester {semester_id}: {e}")
            raise

    async def get_semester_by_acy_sem(
        self, acy: int, sem: int
    ) -> Optional[Semester]:
        """
        Retrieve a semester by academic year and semester number.

        Args:
            acy: Academic year
            sem: Semester number

        Returns:
            Semester record if found, None otherwise

        Raises:
            InvalidQueryParameter: If acy or sem are invalid
            DatabaseError: If the database operation fails

        Example:
            >>> service = SemesterService(session)
            >>> semester = await service.get_semester_by_acy_sem(113, 1)
            >>> if semester:
            ...     print(f"Found semester: {semester.id}")
        """
        # Validate parameters
        self._validate_semester_params(acy, sem)

        logger.info(f"Fetching semester by acy={acy}, sem={sem}")
        try:
            semester = await semester_db.get_semester_by_acy_sem(
                self.session, acy, sem
            )
            if semester:
                logger.info(f"Found semester: acy={acy}, sem={sem}, id={semester.id}")
            else:
                logger.info(f"No semester found for acy={acy}, sem={sem}")
            return semester
        except DatabaseError as e:
            logger.error(f"Failed to get semester by acy/sem: {e}")
            raise

    async def create_new_semester(self, acy: int, sem: int) -> Semester:
        """
        Create a new semester after validation.

        This method validates the input parameters and checks for duplicates
        before creating a new semester.

        Args:
            acy: Academic year (must be positive)
            sem: Semester number (must be 1 or 2)

        Returns:
            Newly created semester record

        Raises:
            InvalidQueryParameter: If acy or sem are invalid
            DatabaseError: If creation fails or semester already exists

        Example:
            >>> service = SemesterService(session)
            >>> semester = await service.create_new_semester(113, 1)
            >>> print(f"Created semester with ID: {semester.id}")
        """
        # Validate parameters
        self._validate_semester_params(acy, sem)

        logger.info(f"Creating new semester: acy={acy}, sem={sem}")

        # Check if semester already exists
        existing = await semester_db.get_semester_by_acy_sem(
            self.session, acy, sem
        )
        if existing:
            error_msg = f"Semester already exists: acy={acy}, sem={sem}, id={existing.id}"
            logger.warning(error_msg)
            raise DatabaseError(message=error_msg)

        try:
            semester = await semester_db.create_semester(self.session, acy, sem)
            logger.info(
                f"Successfully created semester: id={semester.id}, acy={acy}, sem={sem}"
            )
            return semester
        except DatabaseError as e:
            logger.error(f"Failed to create semester: {e}")
            raise

    async def get_or_create_semester(
        self, acy: int, sem: int
    ) -> tuple[Semester, bool]:
        """
        Get existing semester or create it if it doesn't exist.

        This is a convenience method that combines checking and creation.

        Args:
            acy: Academic year
            sem: Semester number

        Returns:
            Tuple of (semester, created) where created is True if a new
            semester was created

        Raises:
            InvalidQueryParameter: If acy or sem are invalid
            DatabaseError: If the operation fails

        Example:
            >>> service = SemesterService(session)
            >>> semester, created = await service.get_or_create_semester(113, 1)
            >>> if created:
            ...     print("Created new semester")
            ... else:
            ...     print("Using existing semester")
        """
        # Validate parameters
        self._validate_semester_params(acy, sem)

        logger.info(f"Get or create semester: acy={acy}, sem={sem}")
        try:
            semester, created = await semester_db.get_or_create_semester(
                self.session, acy, sem
            )
            if created:
                logger.info(f"Created new semester: id={semester.id}")
            else:
                logger.info(f"Using existing semester: id={semester.id}")
            return semester, created
        except DatabaseError as e:
            logger.error(f"Failed to get or create semester: {e}")
            raise

    async def update_semester(
        self,
        semester_id: int,
        acy: Optional[int] = None,
        sem: Optional[int] = None,
    ) -> Semester:
        """
        Update an existing semester's fields.

        Args:
            semester_id: ID of the semester to update
            acy: New academic year (optional)
            sem: New semester number (optional)

        Returns:
            Updated semester record

        Raises:
            SemesterNotFound: If semester doesn't exist
            InvalidQueryParameter: If new values are invalid
            DatabaseError: If update fails

        Example:
            >>> service = SemesterService(session)
            >>> semester = await service.update_semester(1, acy=114)
            >>> print(f"Updated to academic year: {semester.acy}")
        """
        # Validate new parameters if provided
        if acy is not None or sem is not None:
            validate_acy = acy if acy is not None else 100  # Dummy valid value
            validate_sem = sem if sem is not None else 1  # Dummy valid value
            self._validate_semester_params(validate_acy, validate_sem)

        logger.info(f"Updating semester {semester_id}")
        try:
            semester = await semester_db.update_semester(
                self.session, semester_id, acy=acy, sem=sem
            )
            logger.info(f"Successfully updated semester {semester_id}")
            return semester
        except SemesterNotFound as e:
            logger.warning(f"Semester not found for update: {semester_id}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to update semester {semester_id}: {e}")
            raise

    async def delete_semester(self, semester_id: int) -> None:
        """
        Delete a semester from the database.

        Note: This may fail if there are courses associated with this semester.

        Args:
            semester_id: ID of the semester to delete

        Raises:
            SemesterNotFound: If semester doesn't exist
            DatabaseError: If deletion fails (e.g., foreign key constraint)

        Example:
            >>> service = SemesterService(session)
            >>> await service.delete_semester(1)
            >>> print("Semester deleted successfully")
        """
        logger.info(f"Deleting semester {semester_id}")
        try:
            await semester_db.delete_semester(self.session, semester_id)
            logger.info(f"Successfully deleted semester {semester_id}")
        except SemesterNotFound as e:
            logger.warning(f"Semester not found for deletion: {semester_id}")
            raise
        except DatabaseError as e:
            logger.error(f"Failed to delete semester {semester_id}: {e}")
            raise

    def _validate_semester_params(self, acy: int, sem: int) -> None:
        """
        Validate semester parameters.

        Args:
            acy: Academic year to validate
            sem: Semester number to validate

        Raises:
            InvalidQueryParameter: If parameters are invalid
        """
        # Validate academic year
        if acy <= 0:
            raise InvalidQueryParameter(
                message="Academic year must be a positive integer",
                parameter_name="acy",
                parameter_value=str(acy),
            )

        # Validate semester number
        if sem not in [1, 2]:
            raise InvalidQueryParameter(
                message="Semester must be 1 (Fall) or 2 (Spring)",
                parameter_name="sem",
                parameter_value=str(sem),
            )

        # Validate reasonable academic year range (e.g., 90-150 for years 2001-2061)
        if acy < 90 or acy > 150:
            logger.warning(
                f"Academic year {acy} is outside typical range (90-150)"
            )
