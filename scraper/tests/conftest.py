"""
Shared pytest fixtures for all tests.

This module provides common fixtures that can be used across
all test modules in the scraper test suite.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.course import Course


@pytest.fixture
def sample_course():
    """Fixture providing a single sample course."""
    return Course(
        acy=113,
        sem=1,
        crs_no="3101",
        name="Introduction to Computer Science",
        teacher="Dr. John Smith",
        credits=3.0,
        dept="CS",
        time="Monday 10:00-12:00",
        classroom="A101",
        details={
            "capacity": 30,
            "enrollment": 25,
            "description": "Introduction to programming and computer science concepts",
        },
    )


@pytest.fixture
def sample_courses():
    """Fixture providing a list of sample courses."""
    return [
        Course(
            acy=113,
            sem=1,
            crs_no="3101",
            name="Introduction to Computer Science",
            teacher="Dr. John Smith",
            credits=3.0,
            dept="CS",
        ),
        Course(
            acy=113,
            sem=1,
            crs_no="3102",
            name="Data Structures",
            teacher="Dr. Jane Doe",
            credits=3.0,
            dept="CS",
        ),
        Course(
            acy=113,
            sem=2,
            crs_no="5001",
            name="Advanced Algorithms",
            teacher="Dr. Bob Wilson",
            credits=4.0,
            dept="CS",
        ),
    ]


@pytest.fixture
def sample_course_html():
    """Fixture providing sample HTML for a course detail page."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Course Outline</title></head>
    <body>
        <h2>Introduction to Computer Science</h2>
        <table>
            <tr><td>Teacher</td><td>Dr. John Smith</td></tr>
            <tr><td>Credits</td><td>3.0</td></tr>
            <tr><td>Department</td><td>Computer Science</td></tr>
            <tr><td>Time</td><td>Monday 10:00-12:00</td></tr>
            <tr><td>Classroom</td><td>Room A101</td></tr>
            <tr><td>Permanent Course Number</td><td>CS-3101</td></tr>
            <tr><td>Capacity</td><td>30</td></tr>
            <tr><td>Current Enrollment</td><td>25</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_course_list_html():
    """Fixture providing sample HTML for a course list page."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Course List</title></head>
    <body>
        <table id="CourseList">
            <tr>
                <th>Course No</th>
                <th>Name</th>
                <th>Credits</th>
            </tr>
            <tr>
                <td>3101</td>
                <td>Intro to CS</td>
                <td>3.0</td>
            </tr>
            <tr>
                <td>3102</td>
                <td>Data Structures</td>
                <td>3.0</td>
            </tr>
            <tr>
                <td>5001</td>
                <td>Advanced Algorithms</td>
                <td>4.0</td>
            </tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def mock_aiohttp_response():
    """Fixture providing a mock aiohttp response."""
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="<html>Mock content</html>")
    response.__aenter__.return_value = response
    response.__aexit__.return_value = AsyncMock()
    return response


@pytest.fixture
def mock_aiohttp_session(mock_aiohttp_response):
    """Fixture providing a mock aiohttp session."""
    session = AsyncMock()
    session.get.return_value = mock_aiohttp_response
    session.close = AsyncMock()
    return session


@pytest.fixture
def course_numbers():
    """Fixture providing a list of course numbers."""
    return ["3101", "3102", "3103", "4001", "4002", "5001"]


@pytest.fixture(autouse=True)
def reset_logging():
    """Fixture to reset logging configuration between tests."""
    import logging
    # Clear all handlers
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    yield
    # Cleanup after test
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
