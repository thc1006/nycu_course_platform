"""
Advanced Search Service Module.

Optimized for searching 70,239+ course records with:
- Indexed database queries
- Result caching
- Full-text search scoring
- Connection pooling
"""

import logging
from typing import Any, Optional

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.semester import Semester
from app.utils.cache import cache
from app.utils.exceptions import DatabaseError

# Configure logging
logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for advanced course search operations.

    Provides optimized search with:
    - Multiple filter criteria
    - Full-text search with relevance scoring
    - Result caching
    - Query optimization
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize SearchService.

        Args:
            session: Database session for operations
        """
        self.session = session

    @cache(ttl_seconds=300)  # Cache for 5 minutes
    async def advanced_search(
        self,
        query: Optional[str] = None,
        crs_no: Optional[str] = None,
        semester_ids: Optional[list[int]] = None,
        acy: Optional[list[int]] = None,
        sem: Optional[list[int]] = None,
        name: Optional[str] = None,
        teacher: Optional[str] = None,
        dept: Optional[list[str]] = None,
        credits_min: Optional[float] = None,
        credits_max: Optional[float] = None,
        exact_credits: Optional[float] = None,
        day_codes: Optional[list[str]] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "by_relevance",
        sort_desc: bool = False,
    ) -> tuple[list[Course], int]:
        """
        Perform advanced course search with multiple filters.

        Args:
            query: Full-text search query
            crs_no: Course number filter
            semester_ids: List of semester IDs
            acy: List of academic years
            sem: List of semester numbers (1 or 2)
            name: Course name filter
            teacher: Teacher name filter
            dept: List of department codes
            credits_min: Minimum credits
            credits_max: Maximum credits
            exact_credits: Exact credit value
            day_codes: List of day codes
            limit: Maximum results
            offset: Result offset for pagination
            sort_by: Sort field (by_name, by_credits, by_teacher, by_relevance, by_semester)
            sort_desc: Sort in descending order

        Returns:
            Tuple of (courses, total_count)

        Raises:
            DatabaseError: If search operation fails
        """
        try:
            filters = []

            # Full-text search across multiple fields
            if query and query.strip():
                search_pattern = f"%{query}%"
                query_filter = or_(
                    Course.name.ilike(search_pattern),
                    Course.crs_no.ilike(search_pattern),
                    Course.teacher.ilike(search_pattern),
                    Course.dept.ilike(search_pattern),
                )
                filters.append(query_filter)

            # Course number filter
            if crs_no:
                filters.append(Course.crs_no.ilike(f"%{crs_no}%"))

            # Semester ID filter (requires join with semesters table)
            if semester_ids:
                # Query semester table to get acy, sem pairs
                sem_stmt = select(Semester.acy, Semester.sem).where(
                    Semester.id.in_(semester_ids)
                )
                sem_result = await self.session.execute(sem_stmt)
                sem_pairs = sem_result.all()

                if sem_pairs:
                    # semester_ids directly filter the Course.semester_id
                    filters.append(Course.semester_id.in_(semester_ids))

            # Academic year and semester filters require join with semesters table
            # We'll handle this by converting to semester_ids
            if acy or sem:
                # Build query to get matching semester IDs
                sem_filters = []
                if acy:
                    sem_filters.append(Semester.acy.in_(acy))
                if sem:
                    sem_filters.append(Semester.sem.in_(sem))

                sem_stmt = select(Semester.id).where(and_(*sem_filters))
                sem_result = await self.session.execute(sem_stmt)
                matching_semester_ids = [row[0] for row in sem_result.all()]

                if matching_semester_ids:
                    filters.append(Course.semester_id.in_(matching_semester_ids))

            # Course name filter
            if name:
                filters.append(Course.name.ilike(f"%{name}%"))

            # Teacher filter
            if teacher:
                filters.append(Course.teacher.ilike(f"%{teacher}%"))

            # Department filter (multiple departments)
            if dept:
                dept_filters = [Course.dept.ilike(f"%{d}%") for d in dept]
                filters.append(or_(*dept_filters))

            # Credits filters
            if exact_credits is not None:
                filters.append(Course.credits == exact_credits)
            else:
                if credits_min is not None:
                    filters.append(Course.credits >= credits_min)
                if credits_max is not None:
                    filters.append(Course.credits <= credits_max)

            # Day codes filter (partial match in day_codes field)
            if day_codes:
                day_filters = [
                    Course.day_codes.ilike(f"%{day}%") for day in day_codes
                ]
                filters.append(or_(*day_filters))

            # Build base query
            stmt = select(Course)
            if filters:
                stmt = stmt.where(and_(*filters))

            # Get total count before pagination
            count_stmt = select(func.count()).select_from(Course)
            if filters:
                count_stmt = count_stmt.where(and_(*filters))

            total = await self.session.scalar(count_stmt) or 0

            # Apply sorting
            stmt = self._apply_sorting(stmt, sort_by, sort_desc, query)

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            # Execute query with timeout
            # Note: SQLite doesn't support native query timeout, but we can add this
            # at the connection level in production
            result = await self.session.execute(stmt)
            courses = list(result.scalars().all())

            logger.info(
                f"Search executed: {len(courses)} results (total: {total}), "
                f"offset: {offset}, limit: {limit}"
            )

            return courses, total

        except Exception as e:
            logger.error(f"Advanced search failed: {e}", exc_info=True)
            raise DatabaseError(f"Search operation failed: {str(e)}")

    def _apply_sorting(
        self,
        stmt,
        sort_by: str,
        sort_desc: bool,
        query: Optional[str] = None,
    ):
        """
        Apply sorting to query statement.

        Args:
            stmt: SQLAlchemy select statement
            sort_by: Sort field
            sort_desc: Sort descending
            query: Original search query (for relevance scoring)

        Returns:
            Modified statement with sorting
        """
        if sort_by == "by_name":
            order_col = Course.name
        elif sort_by == "by_credits":
            order_col = Course.credits
        elif sort_by == "by_teacher":
            order_col = Course.teacher
        elif sort_by == "by_semester":
            # Sort by semester_id (which corresponds to chronological order)
            if sort_desc:
                return stmt.order_by(Course.semester_id.desc())
            else:
                return stmt.order_by(Course.semester_id.asc())
        elif sort_by == "by_relevance" and query:
            # Simple relevance scoring: prioritize exact matches in name
            # For production, consider using full-text search extensions
            if sort_desc:
                return stmt.order_by(
                    Course.name.ilike(f"%{query}%").desc(),
                    Course.crs_no.ilike(f"%{query}%").desc(),
                    Course.name.asc()
                )
            else:
                return stmt.order_by(
                    Course.name.ilike(f"%{query}%").desc(),
                    Course.crs_no.ilike(f"%{query}%").desc(),
                    Course.name.asc()
                )
        else:
            # Default: sort by ID
            order_col = Course.id

        if sort_desc:
            return stmt.order_by(order_col.desc())
        else:
            return stmt.order_by(order_col.asc())

    @cache(ttl_seconds=3600)  # Cache for 1 hour
    async def get_department_stats(
        self,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get department statistics with course counts.

        Results are cached for 1 hour as department data rarely changes.

        Args:
            limit: Number of top departments to return

        Returns:
            Dictionary with department statistics

        Raises:
            DatabaseError: If query fails
        """
        try:
            # Get total course count
            total_stmt = select(func.count()).select_from(Course)
            total_courses = await self.session.scalar(total_stmt) or 0

            # Get department counts
            dept_stmt = (
                select(
                    Course.dept,
                    func.count(Course.id).label("count")
                )
                .where(Course.dept.isnot(None))
                .group_by(Course.dept)
                .order_by(func.count(Course.id).desc())
                .limit(limit)
            )

            result = await self.session.execute(dept_stmt)
            dept_data = result.all()

            departments = [
                {
                    "code": row[0],
                    "count": row[1],
                    "percentage": round((row[1] / total_courses) * 100, 2) if total_courses > 0 else 0
                }
                for row in dept_data
            ]

            # Get total unique departments
            unique_dept_stmt = select(func.count(func.distinct(Course.dept))).where(
                Course.dept.isnot(None)
            )
            total_departments = await self.session.scalar(unique_dept_stmt) or 0

            logger.info(
                f"Department stats: {len(departments)} departments, "
                f"{total_courses} courses"
            )

            return {
                "departments": departments,
                "total_departments": total_departments,
                "total_courses": total_courses,
            }

        except Exception as e:
            logger.error(f"Failed to get department stats: {e}", exc_info=True)
            raise DatabaseError(f"Department statistics query failed: {str(e)}")

    @cache(ttl_seconds=600)  # Cache for 10 minutes
    async def get_autocomplete_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """
        Get autocomplete suggestions for search queries.

        Searches across course names, teachers, and departments.

        Args:
            query: Query string for autocomplete
            limit: Maximum suggestions to return

        Returns:
            List of suggestion dictionaries

        Raises:
            DatabaseError: If query fails
        """
        try:
            if not query or not query.strip():
                return []

            suggestions = []
            search_pattern = f"%{query}%"

            # Get course name suggestions
            name_stmt = (
                select(Course.name)
                .where(Course.name.ilike(search_pattern))
                .distinct()
                .limit(limit // 3 + 1)
            )
            name_result = await self.session.execute(name_stmt)
            for row in name_result.scalars():
                suggestions.append({
                    "type": "course",
                    "value": row,
                    "match": query
                })

            # Get teacher suggestions
            teacher_stmt = (
                select(Course.teacher)
                .where(Course.teacher.ilike(search_pattern))
                .where(Course.teacher.isnot(None))
                .distinct()
                .limit(limit // 3 + 1)
            )
            teacher_result = await self.session.execute(teacher_stmt)
            for row in teacher_result.scalars():
                suggestions.append({
                    "type": "teacher",
                    "value": row,
                    "match": query
                })

            # Get department suggestions
            dept_stmt = (
                select(Course.dept)
                .where(Course.dept.ilike(search_pattern))
                .where(Course.dept.isnot(None))
                .distinct()
                .limit(limit // 3 + 1)
            )
            dept_result = await self.session.execute(dept_stmt)
            for row in dept_result.scalars():
                suggestions.append({
                    "type": "department",
                    "value": row,
                    "match": query
                })

            # Return limited results
            return suggestions[:limit]

        except Exception as e:
            logger.error(f"Autocomplete query failed: {e}", exc_info=True)
            raise DatabaseError(f"Autocomplete operation failed: {str(e)}")

    async def get_search_suggestions_by_semester(
        self,
        acy: int,
        sem: int,
        limit: int = 10,
    ) -> dict[str, list[str]]:
        """
        Get popular courses, teachers, and departments for a specific semester.

        Useful for search suggestions on the frontend.

        Args:
            acy: Academic year
            sem: Semester number
            limit: Number of suggestions per category

        Returns:
            Dictionary with suggestions by category

        Raises:
            DatabaseError: If query fails
        """
        try:
            # Get semester ID for the given acy/sem
            sem_stmt = select(Semester.id).where(
                and_(Semester.acy == acy, Semester.sem == sem)
            )
            sem_result = await self.session.execute(sem_stmt)
            semester_id = sem_result.scalar_one_or_none()

            if not semester_id:
                # No matching semester found
                return {
                    "departments": [],
                    "teachers": [],
                    "courses": [],
                }

            filters = [Course.semester_id == semester_id]

            # Top departments
            dept_stmt = (
                select(Course.dept, func.count(Course.id))
                .where(and_(*filters))
                .where(Course.dept.isnot(None))
                .group_by(Course.dept)
                .order_by(func.count(Course.id).desc())
                .limit(limit)
            )
            dept_result = await self.session.execute(dept_stmt)
            departments = [row[0] for row in dept_result.all()]

            # Top teachers (by number of courses)
            teacher_stmt = (
                select(Course.teacher, func.count(Course.id))
                .where(and_(*filters))
                .where(Course.teacher.isnot(None))
                .group_by(Course.teacher)
                .order_by(func.count(Course.id).desc())
                .limit(limit)
            )
            teacher_result = await self.session.execute(teacher_stmt)
            teachers = [row[0] for row in teacher_result.all()]

            # Popular course names (by frequency)
            course_stmt = (
                select(Course.name, func.count(Course.id))
                .where(and_(*filters))
                .where(Course.name.isnot(None))
                .group_by(Course.name)
                .order_by(func.count(Course.id).desc())
                .limit(limit)
            )
            course_result = await self.session.execute(course_stmt)
            courses = [row[0] for row in course_result.all()]

            return {
                "departments": departments,
                "teachers": teachers,
                "courses": courses,
            }

        except Exception as e:
            logger.error(f"Failed to get semester suggestions: {e}", exc_info=True)
            raise DatabaseError(
                f"Semester suggestions query failed: {str(e)}"
            )
