"""
Advanced search and filtering service for courses.

Provides advanced search, filtering, and statistics capabilities.
"""

import json
import logging
from typing import Any, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.app.models.course import Course
from backend.app.models.semester import Semester
from backend.app.utils.cache import cache
from backend.app.utils.exceptions import DatabaseError

# Configure logging
logger = logging.getLogger(__name__)


class AdvancedSearchService:
    """
    Service for advanced course search and analytics.

    Provides fuzzy search, advanced filtering, and statistics.
    """

    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.session = session

    @cache(ttl_seconds=300)
    async def advanced_filter(
        self,
        semesters: Optional[list[tuple[int, int]]] = None,
        departments: Optional[list[str]] = None,
        teachers: Optional[list[str]] = None,
        credits: Optional[tuple[float, float]] = None,
        keywords: Optional[list[str]] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[Course], int]:
        """
        Advanced filtering with multiple criteria.

        Args:
            semesters: List of (year, semester) tuples
            departments: List of department codes
            teachers: List of teacher names
            credits: (min_credits, max_credits) range
            keywords: Keywords to search in course name
            limit: Max results
            offset: Result offset

        Returns:
            Tuple of (courses, total_count)
        """
        try:
            filters = []

            # Semester filter - join with Semester table
            if semesters:
                semester_filters = [
                    and_(Semester.acy == acy, Semester.sem == sem)
                    for acy, sem in semesters
                ]
                filters.append(or_(*semester_filters))

            # Department filter
            if departments:
                dept_filters = [
                    Course.dept.ilike(f"%{dept}%") for dept in departments
                ]
                filters.append(or_(*dept_filters))

            # Teacher filter
            if teachers:
                teacher_filters = [
                    Course.teacher.ilike(f"%{teacher}%") for teacher in teachers
                ]
                filters.append(or_(*teacher_filters))

            # Credits filter
            if credits:
                min_cred, max_cred = credits
                filters.append(
                    and_(
                        Course.credits >= min_cred,
                        Course.credits <= max_cred,
                    )
                )

            # Keywords filter
            if keywords:
                keyword_filters = [
                    Course.name.ilike(f"%{kw}%") for kw in keywords
                ]
                filters.append(or_(*keyword_filters))

            # Build query with semester join if needed
            stmt = select(Course).options(joinedload(Course.semester))
            if semesters:
                stmt = stmt.join(Semester)
            if filters:
                stmt = stmt.where(and_(*filters))

            # Get total count
            count_stmt = select(func.count()).select_from(Course)
            if semesters:
                count_stmt = count_stmt.join(Semester)
            if filters:
                count_stmt = count_stmt.where(and_(*filters))

            total = await self.session.scalar(count_stmt)

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            result = await self.session.execute(stmt)
            courses = result.scalars().all()

            logger.info(
                f"Advanced filter: {len(courses)} results (total: {total})"
            )
            return courses, total

        except Exception as e:
            logger.error(f"Advanced filter error: {e}")
            raise DatabaseError(f"Failed to perform advanced filter: {str(e)}")

    @cache(ttl_seconds=3600)
    async def get_statistics(
        self,
        acy: Optional[int] = None,
        sem: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Get statistics about courses.

        Args:
            acy: Filter by academic year
            sem: Filter by semester

        Returns:
            Dictionary with statistics
        """
        try:
            filters = []
            has_semester_filter = False
            if acy:
                filters.append(Semester.acy == acy)
                has_semester_filter = True
            if sem:
                filters.append(Semester.sem == sem)
                has_semester_filter = True

            # Build base query with semester join if needed
            base_query = select(Course)
            if has_semester_filter:
                base_query = base_query.join(Semester)
            if filters:
                base_query = base_query.where(and_(*filters))

            # Total courses
            total_stmt = select(func.count()).select_from(Course)
            if has_semester_filter:
                total_stmt = total_stmt.join(Semester)
            if filters:
                total_stmt = total_stmt.where(and_(*filters))
            total = await self.session.scalar(total_stmt) or 0

            # Courses by department
            dept_stmt = select(Course.dept, func.count()).group_by(Course.dept)
            if has_semester_filter:
                dept_stmt = dept_stmt.select_from(Course).join(Semester)
            if filters:
                dept_stmt = dept_stmt.where(and_(*filters))
            dept_result = await self.session.execute(dept_stmt)
            departments = {row[0]: row[1] for row in dept_result}

            # Average credits
            avg_stmt = select(func.avg(Course.credits))
            if filters:
                avg_stmt = avg_stmt.where(and_(*filters))
            avg_credits = await self.session.scalar(avg_stmt) or 0

            # Top teachers
            teacher_stmt = (
                select(Course.teacher, func.count())
                .group_by(Course.teacher)
                .order_by(func.count().desc())
                .limit(10)
            )
            if filters:
                teacher_stmt = teacher_stmt.where(and_(*filters))
            teacher_result = await self.session.execute(teacher_stmt)
            top_teachers = [
                {"name": row[0], "courses": row[1]}
                for row in teacher_result
            ]

            stats = {
                "total_courses": total,
                "departments": departments,
                "average_credits": float(avg_credits),
                "top_teachers": top_teachers,
            }

            logger.info(f"Statistics calculated: {total} total courses")
            return stats

        except Exception as e:
            logger.error(f"Statistics error: {e}")
            raise DatabaseError(f"Failed to calculate statistics: {str(e)}")

    async def search_with_suggestions(
        self,
        query: str,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Search with suggestions.

        Args:
            query: Search query
            limit: Max results

        Returns:
            Dict with results and suggestions
        """
        try:
            if not query or not query.strip():
                return {"results": [], "suggestions": []}

            # Search for exact matches
            search_pattern = f"%{query}%"
            stmt = select(Course).options(joinedload(Course.semester)).where(
                or_(
                    Course.name.ilike(search_pattern),
                    Course.crs_no.ilike(search_pattern),
                    Course.teacher.ilike(search_pattern),
                )
            )
            stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            courses = result.scalars().all()

            # Get suggestions (unique values)
            suggestions = set()
            for course in courses[:20]:
                if query.lower() in course.name.lower():
                    suggestions.add(course.name)
                if query.lower() in course.teacher.lower():
                    suggestions.add(course.teacher)

            return {
                "results": courses,
                "suggestions": sorted(list(suggestions))[:10],
            }

        except Exception as e:
            logger.error(f"Search with suggestions error: {e}")
            raise DatabaseError(
                f"Failed to search with suggestions: {str(e)}"
            )

    async def get_course_recommendations(
        self,
        course_id: int,
        limit: int = 5,
    ) -> list[Course]:
        """
        Get recommended courses based on a course.

        Args:
            course_id: Reference course ID
            limit: Max recommendations

        Returns:
            List of recommended courses
        """
        try:
            # Get reference course
            reference = await self.session.get(Course, course_id)
            if not reference:
                return []

            # Find similar courses (same dept, similar credits)
            stmt = select(Course).options(joinedload(Course.semester)).where(
                and_(
                    Course.dept == reference.dept,
                    Course.credits >= reference.credits - 1,
                    Course.credits <= reference.credits + 1,
                    Course.id != course_id,
                )
            )
            stmt = stmt.limit(limit)

            result = await self.session.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Recommendations error: {e}")
            raise DatabaseError(
                f"Failed to get recommendations: {str(e)}"
            )
