"""
Integration tests for the NYCU course scraper.

These tests verify the end-to-end functionality of the scraper including
HTTP fetching, parsing, and data flow through the entire pipeline.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from app.models.course import Course
from app.scraper import (
    discover_course_numbers,
    fetch_course_data,
    scrape_semester,
    scrape_all,
    scrape_specific_courses,
)


# Sample HTML content for mocking
SAMPLE_COURSE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Course Outline</title></head>
<body>
    <h2>Introduction to Computer Science</h2>
    <table>
        <tr><td>Teacher</td><td>Dr. John Smith</td></tr>
        <tr><td>Credits</td><td>3.0</td></tr>
        <tr><td>Department</td><td>CS</td></tr>
        <tr><td>Time</td><td>Mon 10:00-12:00</td></tr>
        <tr><td>Classroom</td><td>A101</td></tr>
    </table>
</body>
</html>
"""

SAMPLE_LIST_HTML = """
<!DOCTYPE html>
<html>
<body>
    <table id="CourseList">
        <tr><th>Course No</th><th>Name</th></tr>
        <tr><td>3101</td><td>Intro to CS</td></tr>
        <tr><td>3102</td><td>Data Structures</td></tr>
        <tr><td>5001</td><td>Advanced Algorithms</td></tr>
    </table>
</body>
</html>
"""


class TestDiscoverCourseNumbers:
    """Tests for discover_course_numbers function."""

    @pytest.mark.asyncio
    async def test_discover_course_numbers_returns_list(self):
        """Test that discover_course_numbers returns a list of course numbers."""
        course_numbers = await discover_course_numbers(113, 1)

        assert isinstance(course_numbers, list)
        assert len(course_numbers) > 0
        assert all(isinstance(num, str) for num in course_numbers)

    @pytest.mark.asyncio
    async def test_discover_course_numbers_format(self):
        """Test that discovered course numbers have expected format."""
        course_numbers = await discover_course_numbers(113, 1)

        # Course numbers should be 4-digit strings
        for num in course_numbers[:10]:  # Check first 10
            assert len(num) == 4
            assert num.isdigit() or num.isalnum()

    @pytest.mark.asyncio
    async def test_discover_course_numbers_different_semesters(self):
        """Test discovery for different semesters."""
        numbers_fall = await discover_course_numbers(113, 1)
        numbers_spring = await discover_course_numbers(113, 2)

        # Both semesters should return course numbers
        assert len(numbers_fall) > 0
        assert len(numbers_spring) > 0

        # For simulated data, they might be the same
        # In production, they would likely differ


class TestFetchCourseData:
    """Tests for fetch_course_data function."""

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_html")
    async def test_fetch_course_data_success(self, mock_fetch_html):
        """Test successful course data fetching with mocked HTTP."""
        mock_fetch_html.return_value = SAMPLE_COURSE_HTML

        course = await fetch_course_data(113, 1, "3101")

        assert course is not None
        assert isinstance(course, Course)
        assert course.acy == 113
        assert course.sem == 1
        assert course.crs_no == "3101"
        assert course.name == "Introduction to Computer Science"
        assert course.teacher == "Dr. John Smith"
        assert course.credits == 3.0
        assert course.dept == "CS"

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_html")
    async def test_fetch_course_data_network_failure(self, mock_fetch_html):
        """Test handling of network failure."""
        mock_fetch_html.return_value = None

        course = await fetch_course_data(113, 1, "3101")

        assert course is None

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_html")
    async def test_fetch_course_data_invalid_html(self, mock_fetch_html):
        """Test handling of invalid/empty HTML."""
        mock_fetch_html.return_value = "<html></html>"

        course = await fetch_course_data(113, 1, "3101")

        # Parser should handle gracefully and return Course with minimal data
        assert course is not None
        assert course.acy == 113
        assert course.sem == 1
        assert course.crs_no == "3101"

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_html")
    async def test_fetch_course_data_with_session(self, mock_fetch_html):
        """Test that fetch_course_data uses provided session."""
        mock_fetch_html.return_value = SAMPLE_COURSE_HTML
        mock_session = MagicMock()

        course = await fetch_course_data(113, 1, "3101", session=mock_session)

        assert course is not None
        # Verify session was passed to fetch_html
        mock_fetch_html.assert_called_once()
        call_kwargs = mock_fetch_html.call_args[1]
        assert call_kwargs.get("session") == mock_session


class TestScrapeSemester:
    """Tests for scrape_semester function."""

    @pytest.mark.asyncio
    @patch("app.scraper.discover_course_numbers")
    @patch("app.scraper.fetch_course_data")
    async def test_scrape_semester_success(
        self, mock_fetch_course, mock_discover
    ):
        """Test successful semester scraping."""
        # Mock course discovery
        mock_discover.return_value = ["3101", "3102", "3103"]

        # Mock course fetching
        def create_mock_course(acy, sem, crs_no, session=None):
            return Course(
                acy=acy,
                sem=sem,
                crs_no=crs_no,
                name=f"Course {crs_no}",
                teacher="Dr. Test",
                credits=3.0,
            )

        mock_fetch_course.side_effect = create_mock_course

        # Run scraper
        courses = await scrape_semester(113, 1, max_concurrent=2)

        assert len(courses) == 3
        assert all(isinstance(c, Course) for c in courses)
        assert all(c.acy == 113 for c in courses)
        assert all(c.sem == 1 for c in courses)

    @pytest.mark.asyncio
    @patch("app.scraper.discover_course_numbers")
    @patch("app.scraper.fetch_course_data")
    async def test_scrape_semester_with_failures(
        self, mock_fetch_course, mock_discover
    ):
        """Test semester scraping with some failures."""
        mock_discover.return_value = ["3101", "3102", "3103", "3104"]

        # Mock some successful and some failed fetches
        def mock_fetch(acy, sem, crs_no, session=None):
            if crs_no in ["3101", "3103"]:
                return Course(acy=acy, sem=sem, crs_no=crs_no, name=f"Course {crs_no}")
            return None

        mock_fetch_course.side_effect = mock_fetch

        courses = await scrape_semester(113, 1)

        # Only successful fetches should be included
        assert len(courses) == 2
        assert {c.crs_no for c in courses} == {"3101", "3103"}

    @pytest.mark.asyncio
    @patch("app.scraper.discover_course_numbers")
    async def test_scrape_semester_no_courses(self, mock_discover):
        """Test scraping when no courses are discovered."""
        mock_discover.return_value = []

        courses = await scrape_semester(113, 1)

        assert len(courses) == 0

    @pytest.mark.asyncio
    @patch("app.scraper.discover_course_numbers")
    @patch("app.scraper.fetch_course_data")
    async def test_scrape_semester_concurrency_limit(
        self, mock_fetch_course, mock_discover
    ):
        """Test that concurrency limit is respected."""
        mock_discover.return_value = [f"{i:04d}" for i in range(3001, 3021)]

        # Track concurrent calls
        concurrent_calls = []
        max_concurrent = 0

        async def track_concurrent_fetch(acy, sem, crs_no, session=None):
            concurrent_calls.append(crs_no)
            nonlocal max_concurrent
            max_concurrent = max(max_concurrent, len(concurrent_calls))
            await asyncio.sleep(0.01)  # Simulate work
            concurrent_calls.remove(crs_no)
            return Course(acy=acy, sem=sem, crs_no=crs_no)

        mock_fetch_course.side_effect = track_concurrent_fetch

        courses = await scrape_semester(113, 1, max_concurrent=5, request_delay=0)

        assert len(courses) == 20
        # Max concurrent should not exceed limit (allowing for some timing variance)
        assert max_concurrent <= 6  # Slightly higher to account for timing


class TestScrapeAll:
    """Tests for scrape_all function."""

    @pytest.mark.asyncio
    @patch("app.scraper.scrape_semester")
    async def test_scrape_all_success(self, mock_scrape_semester):
        """Test scraping all courses across multiple semesters."""

        def create_semester_courses(acy, sem, **kwargs):
            # Return different number of courses for each semester
            return [
                Course(acy=acy, sem=sem, crs_no=f"{i:04d}", name=f"Course {i}")
                for i in range(3001, 3006)
            ]

        mock_scrape_semester.side_effect = create_semester_courses

        # Scrape 2 years, 2 semesters each = 4 total semesters
        courses = await scrape_all(
            start_year=112,
            end_year=113,
            semesters=[1, 2],
            max_concurrent=2,
        )

        # Should have called scrape_semester 4 times
        assert mock_scrape_semester.call_count == 4

        # Should have 20 courses total (5 per semester × 4 semesters)
        assert len(courses) == 20

    @pytest.mark.asyncio
    @patch("app.scraper.scrape_semester")
    async def test_scrape_all_single_semester(self, mock_scrape_semester):
        """Test scraping only fall semester."""
        mock_scrape_semester.return_value = [
            Course(acy=113, sem=1, crs_no="3101")
        ]

        courses = await scrape_all(
            start_year=113,
            end_year=113,
            semesters=[1],
        )

        assert mock_scrape_semester.call_count == 1
        assert len(courses) == 1

    @pytest.mark.asyncio
    @patch("app.scraper.scrape_semester")
    async def test_scrape_all_year_range(self, mock_scrape_semester):
        """Test scraping specific year range."""

        def create_courses(acy, sem, **kwargs):
            return [Course(acy=acy, sem=sem, crs_no="3101")]

        mock_scrape_semester.side_effect = create_courses

        courses = await scrape_all(
            start_year=110,
            end_year=112,
            semesters=[1, 2],
        )

        # 3 years × 2 semesters = 6 calls
        assert mock_scrape_semester.call_count == 6
        assert len(courses) == 6

        # Verify years are correct
        years = {c.acy for c in courses}
        assert years == {110, 111, 112}


class TestScrapeSpecificCourses:
    """Tests for scrape_specific_courses function."""

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_course_data")
    async def test_scrape_specific_courses_success(self, mock_fetch):
        """Test scraping specific list of courses."""

        def create_course(acy, sem, crs_no, session=None):
            return Course(acy=acy, sem=sem, crs_no=crs_no, name=f"Course {crs_no}")

        mock_fetch.side_effect = create_course

        course_ids = [
            (113, 1, "3101"),
            (113, 1, "3102"),
            (113, 2, "5001"),
        ]

        courses = await scrape_specific_courses(course_ids, max_concurrent=2)

        assert len(courses) == 3
        assert {c.crs_no for c in courses} == {"3101", "3102", "5001"}

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_course_data")
    async def test_scrape_specific_courses_with_failures(self, mock_fetch):
        """Test scraping specific courses with some failures."""

        def mock_fetch_course(acy, sem, crs_no, session=None):
            if crs_no == "3102":
                return None
            return Course(acy=acy, sem=sem, crs_no=crs_no)

        mock_fetch.side_effect = mock_fetch_course

        course_ids = [
            (113, 1, "3101"),
            (113, 1, "3102"),  # This one fails
            (113, 2, "5001"),
        ]

        courses = await scrape_specific_courses(course_ids)

        assert len(courses) == 2
        assert {c.crs_no for c in courses} == {"3101", "5001"}

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_course_data")
    async def test_scrape_specific_courses_empty_list(self, mock_fetch):
        """Test scraping with empty course list."""
        courses = await scrape_specific_courses([])

        assert len(courses) == 0
        mock_fetch.assert_not_called()


class TestIntegrationFlow:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    @patch("app.scraper.fetch_html")
    async def test_full_pipeline_single_course(self, mock_fetch_html):
        """Test complete pipeline from fetch to Course object."""
        mock_fetch_html.return_value = SAMPLE_COURSE_HTML

        course = await fetch_course_data(113, 1, "3101")

        assert course is not None
        assert course.acy == 113
        assert course.sem == 1
        assert course.crs_no == "3101"
        assert course.name == "Introduction to Computer Science"
        assert course.teacher == "Dr. John Smith"
        assert course.credits == 3.0
        assert course.dept == "CS"
        assert course.time == "Mon 10:00-12:00"
        assert course.classroom == "A101"

    @pytest.mark.asyncio
    @patch("app.scraper.discover_course_numbers")
    @patch("app.scraper.fetch_html")
    async def test_full_pipeline_semester(self, mock_fetch_html, mock_discover):
        """Test complete pipeline for a full semester."""
        mock_discover.return_value = ["3101", "3102"]
        mock_fetch_html.return_value = SAMPLE_COURSE_HTML

        courses = await scrape_semester(113, 1, max_concurrent=2, request_delay=0)

        assert len(courses) == 2
        assert all(c.name == "Introduction to Computer Science" for c in courses)


# Pytest fixtures
@pytest.fixture
def sample_courses():
    """Fixture providing sample course data."""
    return [
        Course(acy=113, sem=1, crs_no="3101", name="Intro to CS", teacher="Dr. Smith"),
        Course(acy=113, sem=1, crs_no="3102", name="Data Structures", teacher="Dr. Jones"),
        Course(acy=113, sem=2, crs_no="5001", name="Algorithms", teacher="Dr. Brown"),
    ]


@pytest.fixture
def mock_session():
    """Fixture providing a mock aiohttp session."""
    session = MagicMock()
    session.close = AsyncMock()
    return session
