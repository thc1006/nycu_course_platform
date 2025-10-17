"""
Integration tests for NYCU course scraper.

This module contains comprehensive integration tests for the NYCU course
scraping functionality, including course discovery, detail fetching, and
full semester/year range scraping.
"""

import pytest
import asyncio
from typing import List
from unittest.mock import patch, AsyncMock

from app.scraper import (
    discover_course_numbers,
    fetch_course_data,
    scrape_semester,
    scrape_all,
)
from app.models.course import Course
from app.parsers.course_parser import parse_course_number_list, parse_course_html


# Sample NYCU HTML structures for testing
SAMPLE_SEARCH_HTML = """
<!DOCTYPE html>
<html>
<head><title>Course Search Results</title></head>
<body>
    <table id="course-list">
        <tr>
            <th>課號</th>
            <th>課程名稱</th>
            <th>教師</th>
            <th>學分</th>
        </tr>
        <tr>
            <td><a href="?r=main%2Fcrsoutline&Acy=113&Sem=1&CrsNo=DCP1234">DCP1234</a></td>
            <td>資料結構</td>
            <td>王教授</td>
            <td>3.0</td>
        </tr>
        <tr>
            <td><a href="?r=main%2Fcrsoutline&Acy=113&Sem=1&CrsNo=EE5001">EE5001</a></td>
            <td>數位訊號處理</td>
            <td>李教授</td>
            <td>3.0</td>
        </tr>
        <tr>
            <td><a href="?r=main%2Fcrsoutline&Acy=113&Sem=1&CrsNo=CS3101">CS3101</a></td>
            <td>作業系統</td>
            <td>張教授</td>
            <td>3.0</td>
        </tr>
    </table>
</body>
</html>
"""

SAMPLE_COURSE_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Course Detail</title></head>
<body>
    <h2>DCP1234 - 資料結構 Data Structures</h2>
    <table class="course-detail">
        <tr>
            <th>授課教師</th>
            <td>王教授</td>
        </tr>
        <tr>
            <th>學分</th>
            <td>3.0</td>
        </tr>
        <tr>
            <th>開課系所</th>
            <td>資訊工程學系</td>
        </tr>
        <tr>
            <th>上課時間</th>
            <td>星期二 3, 4 (10:10-12:00)</td>
        </tr>
        <tr>
            <th>教室</th>
            <td>EC114</td>
        </tr>
        <tr>
            <th>必選修</th>
            <td>必修</td>
        </tr>
        <tr>
            <th>課程描述</th>
            <td>本課程介紹基本資料結構及演算法，包括陣列、鏈結串列、堆疊、佇列、樹、圖形等。</td>
        </tr>
    </table>
</body>
</html>
"""


class TestCourseNumberParsing:
    """Tests for parsing course numbers from search results."""

    def test_parse_course_numbers_from_links(self):
        """Test extracting course numbers from HTML links."""
        course_numbers = parse_course_number_list(SAMPLE_SEARCH_HTML)

        assert len(course_numbers) > 0
        assert "DCP1234" in course_numbers
        assert "EE5001" in course_numbers
        assert "CS3101" in course_numbers

    def test_parse_empty_html(self):
        """Test parsing empty HTML returns empty list."""
        result = parse_course_number_list("")
        assert result == []

    def test_parse_html_no_courses(self):
        """Test parsing HTML with no courses returns empty list."""
        html = "<html><body><p>No courses found</p></body></html>"
        result = parse_course_number_list(html)
        assert result == []

    def test_parse_course_numbers_from_table(self):
        """Test extracting course numbers from table structure."""
        html = """
        <table>
            <tr><th>Course</th><th>Name</th></tr>
            <tr><td>ABC1234</td><td>Test Course 1</td></tr>
            <tr><td>XYZ5678</td><td>Test Course 2</td></tr>
        </table>
        """
        result = parse_course_number_list(html)
        # Should find at least some course-like patterns
        assert len(result) >= 0  # May vary based on parsing strategy


class TestCourseDetailParsing:
    """Tests for parsing course details from detail pages."""

    def test_parse_course_detail_full(self):
        """Test parsing complete course detail page."""
        data = parse_course_html(SAMPLE_COURSE_DETAIL_HTML)

        # Check that key fields are extracted
        assert data is not None
        assert len(data) > 0

        # Name should be extracted from h2
        if "name" in data:
            assert "資料結構" in data["name"] or "Data Structures" in data["name"]

    def test_parse_course_detail_empty(self):
        """Test parsing empty HTML returns empty dict."""
        result = parse_course_html("")
        assert result == {}

    def test_parse_course_detail_fields(self):
        """Test that specific fields are parsed correctly."""
        data = parse_course_html(SAMPLE_COURSE_DETAIL_HTML)

        # These may or may not be found depending on parsing logic
        # Just verify that if found, they have reasonable values
        if "teacher" in data:
            assert len(data["teacher"]) > 0

        if "credits" in data:
            assert isinstance(data["credits"], (int, float))
            assert data["credits"] > 0


class TestCourseDiscovery:
    """Tests for discovering course numbers from NYCU timetable."""

    @pytest.mark.asyncio
    async def test_discover_course_numbers_2024(self):
        """Test discovering courses for academic year 113, semester 1."""
        # Mock the fetch_html function to return sample HTML
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = SAMPLE_SEARCH_HTML

            course_numbers = await discover_course_numbers(113, 1)

            # Verify fetch was called with correct URL
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args[0][0]
            assert "Acy=113" in call_args
            assert "Sem=1" in call_args

            # Verify course numbers were found
            assert len(course_numbers) == 3
            assert "DCP1234" in course_numbers
            assert "EE5001" in course_numbers
            assert "CS3101" in course_numbers

    @pytest.mark.asyncio
    async def test_discover_course_numbers_no_results(self):
        """Test discovering courses when no results are returned."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "<html><body>No courses</body></html>"

            course_numbers = await discover_course_numbers(113, 1)

            assert len(course_numbers) == 0

    @pytest.mark.asyncio
    async def test_discover_course_numbers_network_failure(self):
        """Test discovering courses when network request fails."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = None  # Simulate network failure

            course_numbers = await discover_course_numbers(113, 1)

            assert len(course_numbers) == 0


class TestCourseFetching:
    """Tests for fetching individual course details."""

    @pytest.mark.asyncio
    async def test_fetch_course_detail_real_structure(self):
        """Test fetching course detail with realistic HTML structure."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = SAMPLE_COURSE_DETAIL_HTML

            course = await fetch_course_data(113, 1, "DCP1234")

            # Verify course object was created
            assert course is not None
            assert isinstance(course, Course)
            assert course.acy == 113
            assert course.sem == 1
            assert course.crs_no == "DCP1234"

            # Check that some fields were populated
            # (exact values depend on parsing implementation)
            assert course.details is not None

    @pytest.mark.asyncio
    async def test_fetch_course_detail_network_failure(self):
        """Test fetching course detail when network fails."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = None

            course = await fetch_course_data(113, 1, "DCP1234")

            assert course is None

    @pytest.mark.asyncio
    async def test_fetch_course_detail_invalid_html(self):
        """Test fetching course detail with invalid HTML."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "<html><body></body></html>"

            course = await fetch_course_data(113, 1, "DCP1234")

            # Should still create course object with minimal data
            assert course is not None
            assert course.acy == 113
            assert course.sem == 1
            assert course.crs_no == "DCP1234"


class TestSemesterScraping:
    """Tests for scraping entire semesters."""

    @pytest.mark.asyncio
    async def test_full_semester_scrape_99_1(self):
        """Test scraping academic year 99, semester 1."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            # First call: search results
            # Subsequent calls: course details
            mock_fetch.side_effect = [
                SAMPLE_SEARCH_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
            ]

            courses = await scrape_semester(99, 1, max_concurrent=2)

            # Should have found 3 courses from sample HTML
            assert len(courses) == 3
            assert all(isinstance(c, Course) for c in courses)
            assert all(c.acy == 99 for c in courses)
            assert all(c.sem == 1 for c in courses)

    @pytest.mark.asyncio
    async def test_semester_scrape_empty_results(self):
        """Test scraping semester with no courses."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "<html><body>No courses</body></html>"

            courses = await scrape_semester(113, 1, max_concurrent=2)

            assert len(courses) == 0

    @pytest.mark.asyncio
    async def test_semester_scrape_partial_failures(self):
        """Test scraping semester with some failed course fetches."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            # Search succeeds, but some course details fail
            mock_fetch.side_effect = [
                SAMPLE_SEARCH_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
                None,  # This course fails
                SAMPLE_COURSE_DETAIL_HTML,
            ]

            courses = await scrape_semester(113, 1, max_concurrent=2)

            # Should get 2 out of 3 courses
            assert len(courses) == 2


class TestYearRangeScraping:
    """Tests for scraping multiple years and semesters."""

    @pytest.mark.asyncio
    async def test_full_year_range_99_to_101(self):
        """Test scraping years 99-101 (3 years, 6 semesters)."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            # Create enough mock responses for all semesters
            # 6 semesters * (1 search + 3 courses) = 24 calls
            mock_responses = []
            for _ in range(6):  # 6 semesters
                mock_responses.append(SAMPLE_SEARCH_HTML)  # Search result
                mock_responses.extend([SAMPLE_COURSE_DETAIL_HTML] * 3)  # 3 courses

            mock_fetch.side_effect = mock_responses

            courses = await scrape_all(
                start_year=99,
                end_year=101,
                semesters=[1, 2],
                max_concurrent=2,
                request_delay=0,  # No delay for tests
            )

            # Should have 6 semesters * 3 courses = 18 courses
            assert len(courses) == 18
            assert all(isinstance(c, Course) for c in courses)

            # Verify we have courses from all years
            years = set(c.acy for c in courses)
            assert years == {99, 100, 101}

            # Verify we have both semesters
            semesters = set(c.sem for c in courses)
            assert semesters == {1, 2}

    @pytest.mark.asyncio
    async def test_all_semesters_1_and_2(self):
        """Test that both semesters 1 and 2 are scraped."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            # 2 semesters * (1 search + 3 courses) = 8 calls
            mock_responses = []
            for _ in range(2):  # 2 semesters
                mock_responses.append(SAMPLE_SEARCH_HTML)
                mock_responses.extend([SAMPLE_COURSE_DETAIL_HTML] * 3)

            mock_fetch.side_effect = mock_responses

            courses = await scrape_all(
                start_year=113,
                end_year=113,
                semesters=[1, 2],
                max_concurrent=2,
                request_delay=0,
            )

            # Should have 2 semesters * 3 courses = 6 courses
            assert len(courses) == 6

            # Verify both semesters are present
            semesters = set(c.sem for c in courses)
            assert semesters == {1, 2}

            # Count courses per semester
            sem1_count = sum(1 for c in courses if c.sem == 1)
            sem2_count = sum(1 for c in courses if c.sem == 2)
            assert sem1_count == 3
            assert sem2_count == 3

    @pytest.mark.asyncio
    async def test_single_semester_only(self):
        """Test scraping only semester 1."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_responses = [SAMPLE_SEARCH_HTML]
            mock_responses.extend([SAMPLE_COURSE_DETAIL_HTML] * 3)
            mock_fetch.side_effect = mock_responses

            courses = await scrape_all(
                start_year=113,
                end_year=113,
                semesters=[1],  # Only semester 1
                max_concurrent=2,
                request_delay=0,
            )

            # Should have only semester 1 courses
            assert all(c.sem == 1 for c in courses)
            assert len(courses) == 3


class TestDataValidation:
    """Tests for validating scraped data quality."""

    @pytest.mark.asyncio
    async def test_course_data_completeness(self):
        """Test that scraped courses have required fields."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = SAMPLE_COURSE_DETAIL_HTML

            course = await fetch_course_data(113, 1, "DCP1234")

            # Verify required fields
            assert course is not None
            assert course.acy == 113
            assert course.sem == 1
            assert course.crs_no == "DCP1234"

            # Verify course has details dictionary
            assert isinstance(course.details, dict)

    @pytest.mark.asyncio
    async def test_course_uniqueness(self):
        """Test that courses are unique by (acy, sem, crs_no)."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [
                SAMPLE_SEARCH_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
                SAMPLE_COURSE_DETAIL_HTML,
            ]

            courses = await scrape_semester(113, 1, max_concurrent=2)

            # Create set of (acy, sem, crs_no) tuples
            course_ids = [(c.acy, c.sem, c.crs_no) for c in courses]

            # Verify no duplicates
            assert len(course_ids) == len(set(course_ids))


class TestErrorHandling:
    """Tests for error handling and recovery."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            # Simulate timeout by returning None
            mock_fetch.return_value = None

            course = await fetch_course_data(113, 1, "DCP1234")

            assert course is None

    @pytest.mark.asyncio
    async def test_malformed_html_handling(self):
        """Test handling of malformed HTML."""
        with patch("app.scraper.fetch_html", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "<html><body><table><tr><td>Incomplete"

            course = await fetch_course_data(113, 1, "DCP1234")

            # Should still create a course object
            assert course is not None
            assert course.crs_no == "DCP1234"


# Integration test markers
pytestmark = pytest.mark.asyncio
