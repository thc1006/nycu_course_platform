"""
Schedule service layer.

Business logic for schedule operations.
"""

import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import schedule as schedule_db
from app.models.course import Course
from app.models.schedule import Schedule, ScheduleCourse
from app.schemas.course import CourseResponse
from app.schemas.schedule import ScheduleCourseResponse
from app.utils.exceptions import DatabaseError, ScheduleNotFound

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for schedule operations."""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.session = session

    async def create_schedule(
        self, name: str, acy: int, sem: int, user_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a new schedule.

        Args:
            name: Schedule name
            acy: Academic year
            sem: Semester
            user_id: Optional user identifier

        Returns:
            Schedule details with metadata

        Raises:
            DatabaseError: If creation fails
        """
        schedule = await schedule_db.create_schedule(
            self.session, name=name, acy=acy, sem=sem, user_id=user_id
        )

        return self._build_schedule_response(schedule)

    async def get_schedule(self, schedule_id: int, include_courses: bool = False) -> dict[str, Any]:
        """
        Get a schedule by ID.

        Args:
            schedule_id: Schedule ID
            include_courses: Whether to include course details

        Returns:
            Schedule details

        Raises:
            ScheduleNotFound: If schedule doesn't exist
            DatabaseError: If retrieval fails
        """
        schedule = await schedule_db.get_schedule(
            self.session, schedule_id, include_courses=include_courses
        )

        response = self._build_schedule_response(schedule)

        if include_courses:
            response["schedule_courses"] = await self._build_schedule_courses_response(schedule)

        return response

    async def get_user_schedules(
        self, user_id: str, acy: Optional[int] = None, sem: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """
        Get all schedules for a user.

        Args:
            user_id: User identifier
            acy: Optional filter by academic year
            sem: Optional filter by semester

        Returns:
            List of schedule details

        Raises:
            DatabaseError: If retrieval fails
        """
        schedules = await schedule_db.get_user_schedules(
            self.session, user_id, acy=acy, sem=sem
        )

        return [self._build_schedule_response(schedule) for schedule in schedules]

    async def update_schedule(self, schedule_id: int, name: str) -> dict[str, Any]:
        """
        Update a schedule.

        Args:
            schedule_id: Schedule ID
            name: New schedule name

        Returns:
            Updated schedule details

        Raises:
            ScheduleNotFound: If schedule doesn't exist
            DatabaseError: If update fails
        """
        schedule = await schedule_db.update_schedule(self.session, schedule_id, name=name)

        return self._build_schedule_response(schedule)

    async def delete_schedule(self, schedule_id: int) -> None:
        """
        Delete a schedule.

        Args:
            schedule_id: Schedule ID

        Raises:
            ScheduleNotFound: If schedule doesn't exist
            DatabaseError: If deletion fails
        """
        await schedule_db.delete_schedule(self.session, schedule_id)
        logger.info(f"Schedule {schedule_id} deleted via service")

    async def add_course(
        self,
        schedule_id: int,
        course_id: int,
        color: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Add a course to a schedule.

        Args:
            schedule_id: Schedule ID
            course_id: Course ID
            color: Optional display color
            notes: Optional notes

        Returns:
            Schedule course details

        Raises:
            ScheduleNotFound: If schedule doesn't exist
            DatabaseError: If course doesn't exist or add fails
        """
        schedule_course = await schedule_db.add_course_to_schedule(
            self.session, schedule_id, course_id, color=color, notes=notes
        )

        # Reload with relationships
        schedule = await schedule_db.get_schedule(self.session, schedule_id, include_courses=True)

        # Find the specific schedule_course with relationships loaded
        for sc in schedule.schedule_courses:
            if sc.id == schedule_course.id:
                return await self._build_single_schedule_course_response(sc)

        raise DatabaseError("Failed to reload schedule course after creation")

    async def remove_course(self, schedule_id: int, course_id: int) -> None:
        """
        Remove a course from a schedule.

        Args:
            schedule_id: Schedule ID
            course_id: Course ID

        Raises:
            ScheduleNotFound: If schedule doesn't exist
            DatabaseError: If course not in schedule or removal fails
        """
        await schedule_db.remove_course_from_schedule(self.session, schedule_id, course_id)
        logger.info(f"Course {course_id} removed from schedule {schedule_id} via service")

    async def update_course(
        self,
        schedule_id: int,
        course_id: int,
        color: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Update a course in a schedule.

        Args:
            schedule_id: Schedule ID
            course_id: Course ID
            color: Optional new color
            notes: Optional new notes

        Returns:
            Updated schedule course details

        Raises:
            ScheduleNotFound: If schedule doesn't exist
            DatabaseError: If course not in schedule or update fails
        """
        schedule_course = await schedule_db.update_schedule_course(
            self.session, schedule_id, course_id, color=color, notes=notes
        )

        # Reload with relationships
        schedule = await schedule_db.get_schedule(self.session, schedule_id, include_courses=True)

        # Find the specific schedule_course with relationships loaded
        for sc in schedule.schedule_courses:
            if sc.id == schedule_course.id:
                return await self._build_single_schedule_course_response(sc)

        raise DatabaseError("Failed to reload schedule course after update")

    def _build_schedule_response(self, schedule: Schedule) -> dict[str, Any]:
        """Build schedule response dict with metadata."""
        # Calculate total credits and courses
        # Only access relationships if they are already loaded (not in lazy state)
        total_credits = 0.0
        total_courses = 0

        try:
            # Check if schedule_courses is loaded (not in lazy state)
            if hasattr(schedule, "schedule_courses"):
                # Access without triggering lazy load
                schedule_courses = schedule.__dict__.get("schedule_courses")
                if schedule_courses is not None and len(schedule_courses) > 0:
                    total_courses = len(schedule_courses)
                    for sc in schedule_courses:
                        # Check if course is loaded
                        course = sc.__dict__.get("course")
                        if course is not None and hasattr(course, "credits") and course.credits:
                            total_credits += course.credits
        except Exception as e:
            # If any error accessing relationships, just skip calculation
            logger.debug(f"Could not calculate totals for schedule {schedule.id}: {e}")

        return {
            "id": schedule.id,
            "name": schedule.name,
            "acy": schedule.acy,
            "sem": schedule.sem,
            "user_id": schedule.user_id,
            "created_at": schedule.created_at,
            "updated_at": schedule.updated_at,
            "total_credits": total_credits,
            "total_courses": total_courses,
        }

    async def _build_schedule_courses_response(
        self, schedule: Schedule
    ) -> list[dict[str, Any]]:
        """Build list of schedule courses with full course details."""
        result = []

        for sc in schedule.schedule_courses:
            result.append(await self._build_single_schedule_course_response(sc))

        return result

    async def _build_single_schedule_course_response(
        self, sc: ScheduleCourse
    ) -> dict[str, Any]:
        """Build single schedule course response."""
        course = sc.course

        # Build course response with syllabus URLs
        acy = course.semester.acy if course.semester else 0
        sem = course.semester.sem if course.semester else 0

        syllabus_url_zh = None
        syllabus_url_en = None
        if course.semester and course.crs_no:
            syllabus_url_zh = f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={course.crs_no}&lang=zh-tw"
            syllabus_url_en = f"https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={acy}&Sem={sem}&CrsNo={course.crs_no}&lang=en"

        course_response = {
            "id": course.id,
            "acy": acy,
            "sem": sem,
            "crs_no": course.crs_no,
            "name": course.name,
            "teacher": course.teacher,
            "credits": course.credits,
            "dept": course.dept,
            "time": course.time,
            "classroom": course.classroom,
            "syllabus": course.syllabus,
            "syllabus_zh": course.syllabus_zh,
            "syllabus_url_zh": syllabus_url_zh,
            "syllabus_url_en": syllabus_url_en,
            "details": course.details,
        }

        return {
            "id": sc.id,
            "schedule_id": sc.schedule_id,
            "course_id": sc.course_id,
            "color": sc.color,
            "notes": sc.notes,
            "added_at": sc.added_at,
            "course": course_response,
        }
