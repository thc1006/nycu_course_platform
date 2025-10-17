"""
Tests for course API routes.

This module contains comprehensive tests for all course endpoints including
listing courses with various filters, searching, pagination, and retrieving
individual course details.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_courses(client: AsyncClient, sample_data: dict) -> None:
    """
    Test listing all courses without filters.

    Verifies that:
    - GET /api/courses/ returns 200 OK
    - Response contains all courses
    - Response structure matches CourseResponse schema
    - All required fields are present and valid

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Make request to list all courses
    response = await client.get("/api/courses/")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert correct number of courses
    expected_count = len(sample_data["courses"])
    assert len(data) == expected_count, f"Expected {expected_count} courses, got {len(data)}"

    # Assert response structure for each course
    for course in data:
        # Assert required fields
        assert "id" in course, "Course should have 'id' field"
        assert "acy" in course, "Course should have 'acy' field"
        assert "sem" in course, "Course should have 'sem' field"
        assert "crs_no" in course, "Course should have 'crs_no' field"

        # Assert field types
        assert isinstance(course["id"], int), "id should be an integer"
        assert isinstance(course["acy"], int), "acy should be an integer"
        assert isinstance(course["sem"], int), "sem should be an integer"
        assert isinstance(course["crs_no"], str), "crs_no should be a string"

        # Assert valid values
        assert course["acy"] > 0, "acy should be positive"
        assert course["sem"] in [1, 2], "sem should be 1 or 2"
        assert len(course["crs_no"]) > 0, "crs_no should not be empty"

        # Optional fields can be None or have values
        if course.get("name") is not None:
            assert isinstance(course["name"], str), "name should be a string if present"
        if course.get("teacher") is not None:
            assert isinstance(course["teacher"], str), "teacher should be a string if present"
        if course.get("credits") is not None:
            assert isinstance(course["credits"], (int, float)), "credits should be numeric if present"
        if course.get("dept") is not None:
            assert isinstance(course["dept"], str), "dept should be a string if present"


@pytest.mark.asyncio
async def test_list_courses_empty_database(
    client: AsyncClient,
    test_db: AsyncSession,
) -> None:
    """
    Test listing courses when database is empty.

    Verifies that:
    - GET /api/courses/ returns 200 OK even with no data
    - Response is an empty list

    Args:
        client: HTTP client for making requests
        test_db: Database session (empty, no sample data)
    """
    # Make request to list courses
    response = await client.get("/api/courses/")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is an empty list
    assert isinstance(data, list), "Response should be a list"
    assert len(data) == 0, "Response should be empty when no courses exist"


@pytest.mark.asyncio
async def test_list_courses_by_acy_sem(client: AsyncClient, sample_data: dict) -> None:
    """
    Test filtering courses by academic year and semester.

    Verifies that:
    - Courses can be filtered by acy and sem
    - Only courses matching the filter are returned
    - All returned courses have correct acy and sem values

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Filter for semester 113/1
    response = await client.get("/api/courses/?acy=113&sem=1")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert correct number of courses for semester 113/1
    expected_count = len(sample_data["courses_113_1"])
    assert len(data) == expected_count, f"Expected {expected_count} courses, got {len(data)}"

    # Assert all courses have correct acy and sem
    for course in data:
        assert course["acy"] == 113, f"Expected acy=113, got {course['acy']}"
        assert course["sem"] == 1, f"Expected sem=1, got {course['sem']}"

    # Test semester 113/2
    response_2 = await client.get("/api/courses/?acy=113&sem=2")
    assert response_2.status_code == 200
    data_2 = response_2.json()

    expected_count_2 = len(sample_data["courses_113_2"])
    assert len(data_2) == expected_count_2, f"Expected {expected_count_2} courses, got {len(data_2)}"

    # Assert all courses have correct acy and sem
    for course in data_2:
        assert course["acy"] == 113, f"Expected acy=113, got {course['acy']}"
        assert course["sem"] == 2, f"Expected sem=2, got {course['sem']}"


@pytest.mark.asyncio
async def test_list_courses_by_dept(client: AsyncClient, sample_data: dict) -> None:
    """
    Test filtering courses by department.

    Verifies that:
    - Courses can be filtered by department code
    - Filter performs case-insensitive partial matching
    - Only courses from the specified department are returned

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Filter for CS department
    response = await client.get("/api/courses/?dept=CS")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert all courses are from CS department
    assert len(data) > 0, "Should find at least one CS course"
    for course in data:
        assert course["dept"] is not None, "Course should have dept field"
        assert "CS" in course["dept"].upper(), f"Expected CS dept, got {course['dept']}"

    # Test case-insensitive matching
    response_lower = await client.get("/api/courses/?dept=cs")
    assert response_lower.status_code == 200
    data_lower = response_lower.json()
    assert len(data_lower) == len(data), "Case-insensitive search should return same results"

    # Test partial matching
    response_partial = await client.get("/api/courses/?dept=C")
    assert response_partial.status_code == 200
    data_partial = response_partial.json()
    assert len(data_partial) >= len(data), "Partial match should return at least as many results"


@pytest.mark.asyncio
async def test_list_courses_by_teacher(client: AsyncClient, sample_data: dict) -> None:
    """
    Test filtering courses by teacher name.

    Verifies that:
    - Courses can be filtered by teacher name
    - Filter performs case-insensitive partial matching
    - Only courses taught by matching teachers are returned

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Filter for teacher containing "Smith"
    response = await client.get("/api/courses/?teacher=Smith")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert at least one course is found
    assert len(data) > 0, "Should find at least one course taught by Smith"

    # Assert all courses have Smith in teacher name
    for course in data:
        assert course["teacher"] is not None, "Course should have teacher field"
        assert "SMITH" in course["teacher"].upper(), (
            f"Expected 'Smith' in teacher name, got {course['teacher']}"
        )

    # Test case-insensitive matching
    response_lower = await client.get("/api/courses/?teacher=smith")
    assert response_lower.status_code == 200
    data_lower = response_lower.json()
    assert len(data_lower) == len(data), "Case-insensitive search should return same results"


@pytest.mark.asyncio
async def test_list_courses_search(client: AsyncClient, sample_data: dict) -> None:
    """
    Test searching courses by name or course number.

    Verifies that:
    - Courses can be searched using query parameter 'q'
    - Search works on both course name and course number
    - Search is case-insensitive
    - Partial matching works correctly

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Search for "Computer" in course name
    response = await client.get("/api/courses/?q=Computer")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert at least one course is found
    assert len(data) > 0, "Should find at least one course with 'Computer' in name"

    # Assert all courses have "Computer" in name or course number
    for course in data:
        name_match = course["name"] and "COMPUTER" in course["name"].upper()
        crs_no_match = "COMPUTER" in course["crs_no"].upper()
        assert name_match or crs_no_match, (
            f"Expected 'Computer' in name or crs_no, "
            f"got name={course['name']}, crs_no={course['crs_no']}"
        )

    # Search by course number
    response_crs = await client.get("/api/courses/?q=CS1001")
    assert response_crs.status_code == 200
    data_crs = response_crs.json()
    assert len(data_crs) > 0, "Should find course by course number"

    # Verify the found course has the correct course number
    found = any("CS1001" in course["crs_no"] for course in data_crs)
    assert found, "Should find CS1001 in search results"


@pytest.mark.asyncio
async def test_list_courses_combined_filters(
    client: AsyncClient,
    sample_data: dict,
) -> None:
    """
    Test combining multiple filters.

    Verifies that:
    - Multiple filters can be applied simultaneously
    - Filters work together correctly (AND logic)
    - Results match all specified criteria

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Combine acy, sem, and dept filters
    response = await client.get("/api/courses/?acy=113&sem=1&dept=CS")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is a list
    assert isinstance(data, list), "Response should be a list"

    # Assert courses match all filters
    for course in data:
        assert course["acy"] == 113, f"Expected acy=113, got {course['acy']}"
        assert course["sem"] == 1, f"Expected sem=1, got {course['sem']}"
        assert course["dept"] is not None and "CS" in course["dept"].upper(), (
            f"Expected CS dept, got {course['dept']}"
        )


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, sample_data: dict) -> None:
    """
    Test pagination with limit and offset.

    Verifies that:
    - Limit parameter restricts number of results
    - Offset parameter skips specified number of results
    - Pagination works correctly with filtering
    - Results are consistent across paginated requests

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Test limit
    response_limit = await client.get("/api/courses/?limit=3")
    assert response_limit.status_code == 200
    data_limit = response_limit.json()
    assert len(data_limit) <= 3, f"Expected at most 3 courses, got {len(data_limit)}"

    # Test offset
    response_all = await client.get("/api/courses/")
    assert response_all.status_code == 200
    data_all = response_all.json()

    if len(data_all) > 2:
        response_offset = await client.get("/api/courses/?offset=2")
        assert response_offset.status_code == 200
        data_offset = response_offset.json()

        # Assert offset skipped first 2 results
        expected_count = len(data_all) - 2
        assert len(data_offset) == expected_count, (
            f"Expected {expected_count} courses after offset=2, got {len(data_offset)}"
        )

        # Verify the first course in offset response is the third course overall
        if len(data_all) > 2 and len(data_offset) > 0:
            assert data_offset[0]["id"] == data_all[2]["id"], (
                "First course with offset=2 should match third course overall"
            )

    # Test limit and offset together
    response_both = await client.get("/api/courses/?limit=2&offset=1")
    assert response_both.status_code == 200
    data_both = response_both.json()
    assert len(data_both) <= 2, f"Expected at most 2 courses, got {len(data_both)}"


@pytest.mark.asyncio
async def test_get_course(client: AsyncClient, sample_data: dict) -> None:
    """
    Test retrieving a specific course by ID.

    Verifies that:
    - GET /api/courses/{id} returns 200 OK
    - Response contains correct course data
    - Response structure matches CourseResponse schema
    - All fields have correct values and types

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Get a course from sample data
    course = sample_data["courses"][0]
    course_id = course.id

    # Make request to get specific course
    response = await client.get(f"/api/courses/{course_id}")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response structure and values
    assert data["id"] == course.id, f"Expected id={course.id}, got {data['id']}"
    assert data["acy"] == course.acy, f"Expected acy={course.acy}, got {data['acy']}"
    assert data["sem"] == course.sem, f"Expected sem={course.sem}, got {data['sem']}"
    assert data["crs_no"] == course.crs_no, (
        f"Expected crs_no={course.crs_no}, got {data['crs_no']}"
    )
    assert data["name"] == course.name, f"Expected name={course.name}, got {data['name']}"
    assert data["teacher"] == course.teacher, (
        f"Expected teacher={course.teacher}, got {data['teacher']}"
    )
    assert data["credits"] == course.credits, (
        f"Expected credits={course.credits}, got {data['credits']}"
    )
    assert data["dept"] == course.dept, f"Expected dept={course.dept}, got {data['dept']}"
    assert data["time"] == course.time, f"Expected time={course.time}, got {data['time']}"
    assert data["classroom"] == course.classroom, (
        f"Expected classroom={course.classroom}, got {data['classroom']}"
    )
    assert data["details"] == course.details, (
        f"Expected details={course.details}, got {data['details']}"
    )


@pytest.mark.asyncio
async def test_get_course_not_found(client: AsyncClient, sample_data: dict) -> None:
    """
    Test retrieving a non-existent course.

    Verifies that:
    - GET /api/courses/{invalid_id} returns 404 NOT FOUND
    - Response contains appropriate error message
    - Error detail explains the issue

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Use an ID that doesn't exist
    invalid_id = 99999

    # Make request to get non-existent course
    response = await client.get(f"/api/courses/{invalid_id}")

    # Assert response status
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert error message structure
    assert "detail" in data, "Error response should have 'detail' field"

    # Assert error message mentions the course or not found
    detail = data["detail"].lower()
    assert "not found" in detail or "course" in detail, (
        f"Error message should mention 'not found' or 'course', got: {data['detail']}"
    )


@pytest.mark.asyncio
async def test_get_course_invalid_id_type(client: AsyncClient) -> None:
    """
    Test retrieving a course with invalid ID type.

    Verifies that:
    - GET /api/courses/{invalid_string} returns 422 UNPROCESSABLE ENTITY
    - FastAPI validation catches type mismatch

    Args:
        client: HTTP client for making requests
    """
    # Use an invalid ID type (string instead of int)
    response = await client.get("/api/courses/invalid-id")

    # Assert response status (FastAPI returns 422 for validation errors)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert error structure
    assert "detail" in data, "Validation error should have 'detail' field"


@pytest.mark.asyncio
async def test_list_courses_invalid_parameters(client: AsyncClient) -> None:
    """
    Test listing courses with invalid query parameters.

    Verifies that:
    - Invalid parameter values are caught by validation
    - Appropriate error responses are returned
    - Error messages are descriptive

    Args:
        client: HTTP client for making requests
    """
    # Test invalid acy (negative)
    response_acy = await client.get("/api/courses/?acy=-1")
    assert response_acy.status_code == 422, "Negative acy should be rejected"

    # Test invalid sem (out of range)
    response_sem = await client.get("/api/courses/?sem=3")
    assert response_sem.status_code == 422, "sem=3 should be rejected"

    # Test invalid limit (too large)
    response_limit = await client.get("/api/courses/?limit=10000")
    assert response_limit.status_code == 422, "limit=10000 should be rejected"

    # Test invalid offset (negative)
    response_offset = await client.get("/api/courses/?offset=-1")
    assert response_offset.status_code == 422, "Negative offset should be rejected"


@pytest.mark.asyncio
async def test_get_all_courses_from_different_semesters(
    client: AsyncClient,
    sample_data: dict,
) -> None:
    """
    Test retrieving individual courses from different semesters.

    Verifies that:
    - Courses from different semesters can be retrieved
    - Each course has correct semester information
    - Course data is distinct and accurate

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Get courses from semester 113/1
    course_113_1 = sample_data["courses_113_1"][0]
    response_1 = await client.get(f"/api/courses/{course_113_1.id}")
    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert data_1["acy"] == 113
    assert data_1["sem"] == 1

    # Get courses from semester 113/2
    course_113_2 = sample_data["courses_113_2"][0]
    response_2 = await client.get(f"/api/courses/{course_113_2.id}")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2["acy"] == 113
    assert data_2["sem"] == 2

    # Verify courses are different
    assert data_1["id"] != data_2["id"], "Courses should have different IDs"
    assert data_1["crs_no"] != data_2["crs_no"], "Courses should have different course numbers"


@pytest.mark.asyncio
async def test_list_courses_no_matches(client: AsyncClient, sample_data: dict) -> None:
    """
    Test listing courses with filters that match no courses.

    Verifies that:
    - Empty result set is handled correctly
    - Returns 200 OK with empty list
    - No errors are raised

    Args:
        client: HTTP client for making requests
        sample_data: Fixture providing sample semesters and courses
    """
    # Search for non-existent department
    response = await client.get("/api/courses/?dept=NONEXISTENT")

    # Assert response status
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Get response data
    data = response.json()

    # Assert response is an empty list
    assert isinstance(data, list), "Response should be a list"
    assert len(data) == 0, "Should return empty list when no courses match"
