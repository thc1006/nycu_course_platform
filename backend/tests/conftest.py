"""
Pytest configuration and fixtures for backend tests.

This module provides reusable fixtures for testing the NYCU Course Platform backend,
including database setup, test client, and sample data generation.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from backend.app.database.session import get_session
from backend.app.main import app
from backend.app.models.course import Course
from backend.app.models.semester import Semester


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the entire test session.

    This fixture ensures that async tests can run properly by providing
    a consistent event loop throughout the test session.

    Yields:
        asyncio.AbstractEventLoop: Event loop for async operations
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create an in-memory SQLite database for testing.

    This fixture creates a fresh database for each test function, ensuring
    test isolation. The database is automatically cleaned up after each test.

    Yields:
        AsyncSession: Database session for test operations

    Example:
        >>> async def test_something(test_db):
        ...     semester = Semester(acy=113, sem=1)
        ...     test_db.add(semester)
        ...     await test_db.commit()
    """
    # Create async engine with in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )

    # Create and yield session
    async with async_session() as session:
        yield session

    # Cleanup: close connections
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(test_db: AsyncSession) -> AsyncSession:
    """
    Provide an async SQLAlchemy session for tests.

    This is an alias for test_db fixture to provide a more descriptive
    name in some test contexts.

    Args:
        test_db: Test database session

    Returns:
        AsyncSession: Database session for test operations
    """
    return test_db


@pytest.fixture(scope="function")
async def app_fixture(test_db: AsyncSession):
    """
    Create a FastAPI test app instance with dependency overrides.

    This fixture overrides the database session dependency to use the
    test database instead of the production database.

    Args:
        test_db: Test database session

    Returns:
        FastAPI: Configured FastAPI application for testing

    Example:
        >>> async def test_endpoint(app_fixture, client):
        ...     response = await client.get("/api/semesters/")
        ...     assert response.status_code == 200
    """

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        """Override get_session dependency to use test database."""
        yield test_db

    # Override the session dependency
    app.dependency_overrides[get_session] = override_get_session

    yield app

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client(app_fixture) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.

    This fixture provides an HTTPX AsyncClient configured to make requests
    to the test FastAPI application.

    Args:
        app_fixture: FastAPI test application

    Yields:
        AsyncClient: HTTP client for making API requests

    Example:
        >>> async def test_get_semesters(client):
        ...     response = await client.get("/api/semesters/")
        ...     assert response.status_code == 200
        ...     data = response.json()
        ...     assert len(data) > 0
    """
    async with AsyncClient(app=app_fixture, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def sample_data(test_db: AsyncSession) -> dict:
    """
    Create sample data for testing.

    This fixture populates the test database with:
    - 2 semesters (113/1, 113/2)
    - 5 courses per semester (10 total courses)

    The sample data includes various departments, teachers, and course details
    to facilitate comprehensive testing of filtering and search functionality.

    Args:
        test_db: Test database session

    Returns:
        dict: Dictionary containing created semesters and courses

    Example:
        >>> async def test_with_data(sample_data):
        ...     semesters = sample_data["semesters"]
        ...     courses = sample_data["courses"]
        ...     assert len(semesters) == 2
        ...     assert len(courses) == 10
    """
    # Create semesters
    semester_113_1 = Semester(acy=113, sem=1)
    semester_113_2 = Semester(acy=113, sem=2)

    test_db.add(semester_113_1)
    test_db.add(semester_113_2)
    await test_db.commit()
    await test_db.refresh(semester_113_1)
    await test_db.refresh(semester_113_2)

    # Create courses for semester 113/1
    courses_113_1 = [
        Course(
            acy=113,
            sem=1,
            crs_no="CS1001",
            name="Introduction to Computer Science",
            teacher="Dr. Alice Smith",
            credits=3.0,
            dept="CS",
            time="Mon 10:00-12:00",
            classroom="A101",
            details='{"capacity": 50, "enrollment": 45}',
        ),
        Course(
            acy=113,
            sem=1,
            crs_no="CS2002",
            name="Data Structures and Algorithms",
            teacher="Dr. Bob Johnson",
            credits=4.0,
            dept="CS",
            time="Tue 14:00-16:00",
            classroom="A102",
            details='{"capacity": 40, "enrollment": 38}',
        ),
        Course(
            acy=113,
            sem=1,
            crs_no="MATH1001",
            name="Calculus I",
            teacher="Dr. Carol Davis",
            credits=3.0,
            dept="MATH",
            time="Wed 09:00-11:00",
            classroom="B201",
            details='{"capacity": 60, "enrollment": 55}',
        ),
        Course(
            acy=113,
            sem=1,
            crs_no="PHY2001",
            name="Physics I",
            teacher="Dr. David Wilson",
            credits=3.0,
            dept="PHY",
            time="Thu 13:00-15:00",
            classroom="C301",
            details='{"capacity": 45, "enrollment": 42}',
        ),
        Course(
            acy=113,
            sem=1,
            crs_no="EE3001",
            name="Digital Circuit Design",
            teacher="Dr. Eve Martinez",
            credits=3.0,
            dept="EE",
            time="Fri 10:00-12:00",
            classroom="D401",
            details='{"capacity": 35, "enrollment": 33}',
        ),
    ]

    # Create courses for semester 113/2
    courses_113_2 = [
        Course(
            acy=113,
            sem=2,
            crs_no="CS1002",
            name="Object-Oriented Programming",
            teacher="Dr. Alice Smith",
            credits=3.0,
            dept="CS",
            time="Mon 14:00-16:00",
            classroom="A103",
            details='{"capacity": 50, "enrollment": 47}',
        ),
        Course(
            acy=113,
            sem=2,
            crs_no="CS3003",
            name="Database Systems",
            teacher="Dr. Bob Johnson",
            credits=3.0,
            dept="CS",
            time="Tue 10:00-12:00",
            classroom="A104",
            details='{"capacity": 40, "enrollment": 35}',
        ),
        Course(
            acy=113,
            sem=2,
            crs_no="MATH2002",
            name="Linear Algebra",
            teacher="Dr. Frank Brown",
            credits=3.0,
            dept="MATH",
            time="Wed 13:00-15:00",
            classroom="B202",
            details='{"capacity": 55, "enrollment": 50}',
        ),
        Course(
            acy=113,
            sem=2,
            crs_no="PHY2002",
            name="Physics II",
            teacher="Dr. David Wilson",
            credits=3.0,
            dept="PHY",
            time="Thu 09:00-11:00",
            classroom="C302",
            details='{"capacity": 45, "enrollment": 40}',
        ),
        Course(
            acy=113,
            sem=2,
            crs_no="EE4001",
            name="Embedded Systems",
            teacher="Dr. Grace Lee",
            credits=4.0,
            dept="EE",
            time="Fri 14:00-17:00",
            classroom="D402",
            details='{"capacity": 30, "enrollment": 28}',
        ),
    ]

    # Add all courses to database
    for course in courses_113_1 + courses_113_2:
        test_db.add(course)

    await test_db.commit()

    # Refresh all objects to get their IDs
    for course in courses_113_1 + courses_113_2:
        await test_db.refresh(course)

    return {
        "semesters": [semester_113_1, semester_113_2],
        "courses": courses_113_1 + courses_113_2,
        "courses_113_1": courses_113_1,
        "courses_113_2": courses_113_2,
    }
