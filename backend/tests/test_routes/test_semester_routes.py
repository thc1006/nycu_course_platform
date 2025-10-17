"""
Tests for semester API routes.

This module contains comprehensive tests for all semester endpoints including
listing semesters and retrieving individual semester details.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_semesters(client: AsyncClient, sample_data: dict) -> None:
    """
    Test listing all semesters.

    Verifies that:
    - GET /api/semesters/ returns 200 OK
    - Response contains all semesters
    - Semesters are ordered correctly (most recent first)
    - Response structure matches SemesterResponse schema
    - All required fields are present

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Make request to list semesters
    response = await client.get("/api/semesters/")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert correct number of semesters
    expected_count = len(sample_data["semesters"])
    assert len(data) == expected_count, f"Expected {expected_count} semesters, got {len(data)}"

    # Assert response structure for each semester
    for semester in data:
        assert "id" in semester, "Semester should have 'id' field"
        assert "acy" in semester, "Semester should have 'acy' field"
        assert "sem" in semester, "Semester should have 'sem' field"

        # Assert field types
        assert isinstance(semester["id"], int), "id should be an integer"
        assert isinstance(semester["acy"], int), "acy should be an integer"
        assert isinstance(semester["sem"], int), "sem should be an integer"

        # Assert valid semester values
        assert semester["acy"] > 0, "acy should be positive"
        assert semester["sem"] in [1, 2], "sem should be 1 or 2"

    # Verify semesters are ordered correctly (most recent first)
    # For same academic year, semester 2 should come before semester 1
    semester_113_2 = next((s for s in data if s["acy"] == 113 and s["sem"] == 2), None)
    semester_113_1 = next((s for s in data if s["acy"] == 113 and s["sem"] == 1), None)

    assert semester_113_2 is not None, "Semester 113/2 should exist"
    assert semester_113_1 is not None, "Semester 113/1 should exist"

    # Find indices
    idx_113_2 = data.index(semester_113_2)
    idx_113_1 = data.index(semester_113_1)

    assert idx_113_2 < idx_113_1, "Semester 113/2 should appear before 113/1"


@pytest.mark.asyncio
async def test_list_semesters_empty_database(
    client: AsyncClient,
    test_db: AsyncSession,
) -> None:
    """
    Test listing semesters when database is empty.

    Verifies that:
    - GET /api/semesters/ returns 200 OK even with no data
    - Response is an empty list

    Args:
        client: HTTP client for making requests
        test_db: Database session (empty, no sample data)
    """
    # Make request to list semesters
    response = await client.get("/api/semesters/")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is an empty list
    assert isinstance(data, list), "Response should be a list"
    assert len(data) == 0, "Response should be empty when no semesters exist"


@pytest.mark.asyncio
async def test_get_semester(client: AsyncClient, sample_data: dict) -> None:
    """
    Test retrieving a specific semester by ID.

    Verifies that:
    - GET /api/semesters/{id} returns 200 OK
    - Response contains correct semester data
    - Response structure matches SemesterResponse schema
    - All fields have correct values

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Get a semester from sample data
    semester = sample_data["semesters"][0]
    semester_id = semester.id

    # Make request to get specific semester
    response = await client.get(f"/api/semesters/{semester_id}")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response structure
    assert "id" in data, "Response should have 'id' field"
    assert "acy" in data, "Response should have 'acy' field"
    assert "sem" in data, "Response should have 'sem' field"

    # Assert correct values
    assert data["id"] == semester.id, f"Expected id={semester.id}, got {data['id']}"
    assert data["acy"] == semester.acy, f"Expected acy={semester.acy}, got {data['acy']}"
    assert data["sem"] == semester.sem, f"Expected sem={semester.sem}, got {data['sem']}"

    # Assert field types
    assert isinstance(data["id"], int), "id should be an integer"
    assert isinstance(data["acy"], int), "acy should be an integer"
    assert isinstance(data["sem"], int), "sem should be an integer"


@pytest.mark.asyncio
async def test_get_semester_not_found(client: AsyncClient, sample_data: dict) -> None:
    """
    Test retrieving a non-existent semester.

    Verifies that:
    - GET /api/semesters/{invalid_id} returns 404 NOT FOUND
    - Response contains appropriate error message
    - Error detail explains the issue

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Use an ID that doesn't exist
    invalid_id = 99999

    # Make request to get non-existent semester
    response = await client.get(f"/api/semesters/{invalid_id}")

    # Assert response status
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert error message structure
    assert "detail" in data, "Error response should have 'detail' field"

    # Assert error message mentions the semester
    detail = data["detail"].lower()
    assert "not found" in detail or "semester" in detail, (
        f"Error message should mention 'not found' or 'semester', got: {data['detail']}"
    )


@pytest.mark.asyncio
async def test_get_semester_with_both_semesters(
    client: AsyncClient,
    sample_data: dict,
) -> None:
    """
    Test retrieving both semesters individually.

    Verifies that:
    - Both semesters can be retrieved successfully
    - Each semester has correct data
    - Semesters are distinct and have different data

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Get both semesters from sample data
    semester_1 = sample_data["semesters"][0]
    semester_2 = sample_data["semesters"][1]

    # Retrieve first semester
    response_1 = await client.get(f"/api/semesters/{semester_1.id}")
    assert response_1.status_code == 200
    data_1 = response_1.json()

    # Retrieve second semester
    response_2 = await client.get(f"/api/semesters/{semester_2.id}")
    assert response_2.status_code == 200
    data_2 = response_2.json()

    # Assert both have correct data
    assert data_1["id"] == semester_1.id
    assert data_1["acy"] == semester_1.acy
    assert data_1["sem"] == semester_1.sem

    assert data_2["id"] == semester_2.id
    assert data_2["acy"] == semester_2.acy
    assert data_2["sem"] == semester_2.sem

    # Assert semesters are different
    assert data_1["id"] != data_2["id"], "Semesters should have different IDs"


@pytest.mark.asyncio
async def test_get_semester_invalid_id_type(client: AsyncClient) -> None:
    """
    Test retrieving a semester with invalid ID type.

    Verifies that:
    - GET /api/semesters/{invalid_string} returns 422 UNPROCESSABLE ENTITY
    - FastAPI validation catches type mismatch

    Args:
        client: HTTP client for making requests
    """
    # Use an invalid ID type (string instead of int)
    response = await client.get("/api/semesters/invalid-id")

    # Assert response status (FastAPI returns 422 for validation errors)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert error structure
    assert "detail" in data, "Validation error should have 'detail' field"
