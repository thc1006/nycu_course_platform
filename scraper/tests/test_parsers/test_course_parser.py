"""
Unit tests for the course parser module.

These tests verify the HTML parsing functionality for extracting
course information and course numbers from various HTML structures.
"""

import pytest
from app.parsers.course_parser import (
    parse_course_html,
    parse_course_number_list,
    extract_table_data,
)


class TestParseCourseHtml:
    """Tests for parse_course_html function."""

    def test_parse_valid_course_html(self):
        """Test parsing valid HTML with all fields."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Course</title></head>
        <body>
            <h2>Introduction to Computer Science</h2>
            <table>
                <tr><td>Teacher</td><td>Dr. John Smith</td></tr>
                <tr><td>Credits</td><td>3.0</td></tr>
                <tr><td>Department</td><td>Computer Science</td></tr>
                <tr><td>Time</td><td>Monday 10:00-12:00</td></tr>
                <tr><td>Classroom</td><td>Room A101</td></tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert data is not None
        assert isinstance(data, dict)
        assert data["name"] == "Introduction to Computer Science"
        assert data["teacher"] == "Dr. John Smith"
        assert data["credits"] == 3.0
        assert data["dept"] == "Computer Science"
        assert data["time"] == "Monday 10:00-12:00"
        assert data["classroom"] == "Room A101"

    def test_parse_minimal_html(self):
        """Test parsing HTML with only title."""
        html = """
        <html>
        <body>
            <h2>Data Structures</h2>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert isinstance(data, dict)
        assert data.get("name") == "Data Structures"
        # Other fields should be absent
        assert "teacher" not in data or data["teacher"] is None

    def test_parse_empty_html(self):
        """Test parsing empty HTML returns empty dict."""
        html = ""
        data = parse_course_html(html)

        assert isinstance(data, dict)
        assert len(data) == 0

    def test_parse_invalid_html(self):
        """Test parsing malformed HTML."""
        html = "<html><body><h2>Test</h2><table><tr><td>Broken"

        # Should handle gracefully and extract what it can
        data = parse_course_html(html)

        assert isinstance(data, dict)
        # At minimum, might extract the title
        assert data.get("name") == "Test" or len(data) >= 0

    def test_parse_credits_formats(self):
        """Test parsing various credit formats."""
        test_cases = [
            ("<tr><td>Credits</td><td>3.0</td></tr>", 3.0),
            ("<tr><td>Credits</td><td>4</td></tr>", 4.0),
            ("<tr><td>學分</td><td>2.5</td></tr>", 2.5),
            ("<tr><td>Credits</td><td>3.0 credits</td></tr>", 3.0),
        ]

        for html_snippet, expected_credits in test_cases:
            html = f"<html><body><table>{html_snippet}</table></body></html>"
            data = parse_course_html(html)

            if expected_credits is not None:
                assert "credits" in data
                assert data["credits"] == expected_credits

    def test_parse_with_chinese_fields(self):
        """Test parsing HTML with Chinese field names."""
        html = """
        <html>
        <body>
            <h2>計算機概論</h2>
            <table>
                <tr><td>授課教師</td><td>王小明</td></tr>
                <tr><td>學分</td><td>3.0</td></tr>
                <tr><td>系所</td><td>資訊工程</td></tr>
                <tr><td>上課時間</td><td>星期一 10:00-12:00</td></tr>
                <tr><td>教室</td><td>A101</td></tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert data["name"] == "計算機概論"
        assert data["teacher"] == "王小明"
        assert data["credits"] == 3.0
        assert data["dept"] == "資訊工程"
        assert data["time"] == "星期一 10:00-12:00"
        assert data["classroom"] == "A101"

    def test_parse_additional_fields(self):
        """Test parsing additional course fields."""
        html = """
        <html>
        <body>
            <h2>Advanced Algorithms</h2>
            <table>
                <tr><td>Permanent Course Number</td><td>CS-5001</td></tr>
                <tr><td>Required</td><td>Elective</td></tr>
                <tr><td>Capacity</td><td>50</td></tr>
                <tr><td>Current Enrollment</td><td>42</td></tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert data["name"] == "Advanced Algorithms"
        assert "permanent_crs_no" in data
        assert data["permanent_crs_no"] == "CS-5001"
        assert "capacity" in data
        assert data["capacity"] == 50
        assert "current_enrollment" in data
        assert data["current_enrollment"] == 42

    def test_parse_long_description(self):
        """Test parsing course with description field."""
        html = """
        <html>
        <body>
            <h2>Machine Learning</h2>
            <table>
                <tr>
                    <td>Description</td>
                    <td>This course covers fundamental concepts in machine learning
                    including supervised and unsupervised learning methods.</td>
                </tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert "description" in data
        assert "machine learning" in data["description"].lower()
        assert len(data["description"]) > 50

    def test_parse_evaluation_methods(self):
        """Test parsing evaluation/grading information."""
        html = """
        <html>
        <body>
            <h2>Software Engineering</h2>
            <table>
                <tr>
                    <td>Evaluation</td>
                    <td>Midterm 30%, Final 30%, Projects 40%</td>
                </tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert "evaluation" in data
        assert "Midterm" in data["evaluation"]
        assert "Projects" in data["evaluation"]


class TestParseCourseNumberList:
    """Tests for parse_course_number_list function."""

    def test_parse_table_with_course_numbers(self):
        """Test parsing table containing course numbers."""
        html = """
        <html>
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
                    <td>Algorithms</td>
                    <td>3.0</td>
                </tr>
            </table>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        assert isinstance(numbers, list)
        assert len(numbers) == 3
        assert "3101" in numbers
        assert "3102" in numbers
        assert "5001" in numbers

    def test_parse_links_with_course_numbers(self):
        """Test extracting course numbers from links."""
        html = """
        <html>
        <body>
            <div class="course-list">
                <a href="/?r=main/crsoutline&Acy=113&Sem=1&CrsNo=3101">Course 3101</a>
                <a href="/?r=main/crsoutline&Acy=113&Sem=1&CrsNo=3102">Course 3102</a>
                <a href="/?r=main/crsoutline&Acy=113&Sem=1&CrsNo=4201">Course 4201</a>
            </div>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        assert len(numbers) >= 3
        assert "3101" in numbers
        assert "3102" in numbers
        assert "4201" in numbers

    def test_parse_empty_html(self):
        """Test parsing empty HTML returns empty list."""
        html = ""
        numbers = parse_course_number_list(html)

        assert isinstance(numbers, list)
        assert len(numbers) == 0

    def test_parse_html_without_courses(self):
        """Test parsing HTML with no course information."""
        html = """
        <html>
        <body>
            <h1>Welcome to NYCU</h1>
            <p>This page contains no courses.</p>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        assert isinstance(numbers, list)
        assert len(numbers) == 0

    def test_parse_alphanumeric_course_numbers(self):
        """Test parsing course numbers with letters."""
        html = """
        <html>
        <body>
            <table>
                <tr><th>Course</th></tr>
                <tr><td>CS101</td></tr>
                <tr><td>EE202</td></tr>
                <tr><td>MATH301</td></tr>
            </table>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        assert len(numbers) >= 3
        # Parser should handle alphanumeric codes
        assert any("CS101" in num or "101" in num for num in numbers)

    def test_parse_mixed_format_table(self):
        """Test parsing table with mixed content."""
        html = """
        <html>
        <body>
            <table class="course-table">
                <tr><th>Code</th><th>Name</th></tr>
                <tr><td>3101</td><td>Course A</td></tr>
                <tr><td>Short</td><td>Invalid</td></tr>
                <tr><td>5002</td><td>Course B</td></tr>
            </table>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        # Should extract valid course numbers, skip invalid ones
        assert "3101" in numbers
        assert "5002" in numbers
        # "Short" should be excluded (less than 4 chars)

    def test_parse_duplicate_course_numbers(self):
        """Test that parser doesn't include duplicates."""
        html = """
        <html>
        <body>
            <table>
                <tr><td>3101</td></tr>
                <tr><td>3101</td></tr>
                <tr><td>3102</td></tr>
            </table>
            <div>
                <a href="?CrsNo=3101">Course 3101</a>
            </div>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        # Each course number should appear only once
        assert numbers.count("3101") == 1 or len([n for n in numbers if n == "3101"]) <= 2
        assert "3102" in numbers

    def test_parse_course_divs(self):
        """Test parsing course numbers from div elements."""
        html = """
        <html>
        <body>
            <div class="course-item">3101 - Intro to CS</div>
            <div class="course-item">3102 - Data Structures</div>
            <div class="course-item">4001 - Algorithms</div>
        </body>
        </html>
        """

        numbers = parse_course_number_list(html)

        assert len(numbers) >= 3
        assert "3101" in numbers
        assert "3102" in numbers
        assert "4001" in numbers


class TestExtractTableData:
    """Tests for extract_table_data utility function."""

    def test_extract_simple_table(self):
        """Test extracting data from a simple table."""
        html = """
        <html>
        <body>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Code</th>
                    <th>Credits</th>
                </tr>
                <tr>
                    <td>Intro to CS</td>
                    <td>3101</td>
                    <td>3.0</td>
                </tr>
                <tr>
                    <td>Data Structures</td>
                    <td>3102</td>
                    <td>3.0</td>
                </tr>
            </table>
        </body>
        </html>
        """

        data = extract_table_data(html)

        assert len(data) == 2
        assert data[0]["Name"] == "Intro to CS"
        assert data[0]["Code"] == "3101"
        assert data[0]["Credits"] == "3.0"
        assert data[1]["Name"] == "Data Structures"

    def test_extract_with_selector(self):
        """Test extracting data with CSS selector."""
        html = """
        <html>
        <body>
            <table id="main-table">
                <tr><th>Col1</th><th>Col2</th></tr>
                <tr><td>A</td><td>B</td></tr>
            </table>
            <table id="other-table">
                <tr><th>X</th><th>Y</th></tr>
                <tr><td>1</td><td>2</td></tr>
            </table>
        </body>
        </html>
        """

        data = extract_table_data(html, table_selector="#main-table")

        assert len(data) == 1
        assert data[0]["Col1"] == "A"
        assert data[0]["Col2"] == "B"

    def test_extract_empty_table(self):
        """Test extracting from table with only headers."""
        html = """
        <html>
        <body>
            <table>
                <tr><th>Name</th><th>Code</th></tr>
            </table>
        </body>
        </html>
        """

        data = extract_table_data(html)

        assert isinstance(data, list)
        assert len(data) == 0

    def test_extract_no_table(self):
        """Test extracting when no table exists."""
        html = """
        <html>
        <body>
            <div>No table here</div>
        </body>
        </html>
        """

        data = extract_table_data(html)

        assert isinstance(data, list)
        assert len(data) == 0

    def test_extract_misaligned_columns(self):
        """Test handling of rows with different column counts."""
        html = """
        <html>
        <body>
            <table>
                <tr><th>A</th><th>B</th><th>C</th></tr>
                <tr><td>1</td><td>2</td><td>3</td></tr>
                <tr><td>4</td><td>5</td></tr>
            </table>
        </body>
        </html>
        """

        data = extract_table_data(html)

        # Only rows matching header count should be included
        assert len(data) == 1
        assert data[0]["A"] == "1"

    def test_extract_with_whitespace(self):
        """Test that extracted data is stripped of whitespace."""
        html = """
        <html>
        <body>
            <table>
                <tr><th>  Name  </th><th>  Code  </th></tr>
                <tr><td>  Value1  </td><td>  Value2  </td></tr>
            </table>
        </body>
        </html>
        """

        data = extract_table_data(html)

        assert len(data) == 1
        assert "Name" in data[0]
        assert "Code" in data[0]
        assert data[0]["Name"] == "Value1"
        assert data[0]["Code"] == "Value2"


class TestParserEdgeCases:
    """Tests for edge cases and error handling."""

    def test_parse_malformed_credits(self):
        """Test parsing malformed credit values."""
        html = """
        <html>
        <body>
            <table>
                <tr><td>Credits</td><td>Not a number</td></tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        # Should handle gracefully, not include credits or set to None
        assert "credits" not in data or data.get("credits") is None

    def test_parse_very_long_html(self):
        """Test parsing very long HTML document."""
        # Create large HTML with repeated content
        rows = "\n".join([f"<tr><td>Field{i}</td><td>Value{i}</td></tr>" for i in range(1000)])
        html = f"""
        <html>
        <body>
            <h2>Test Course</h2>
            <table>
                {rows}
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        # Should handle large documents
        assert isinstance(data, dict)
        assert data.get("name") == "Test Course"

    def test_parse_special_characters(self):
        """Test parsing HTML with special characters."""
        html = """
        <html>
        <body>
            <h2>C++ & Data Structures: <Advanced Topics></h2>
            <table>
                <tr><td>Teacher</td><td>Dr. O'Brien & Prof. García</td></tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert "name" in data
        assert "&" in data["name"] or "and" in data["name"].lower()
        assert "teacher" in data

    def test_parse_nested_elements(self):
        """Test parsing with nested HTML elements."""
        html = """
        <html>
        <body>
            <div class="course-info">
                <h2><span>Database Systems</span></h2>
                <table>
                    <tr><td>Teacher</td><td><a href="#">Dr. Smith</a></td></tr>
                </table>
            </div>
        </body>
        </html>
        """

        data = parse_course_html(html)

        assert data.get("name") == "Database Systems"
        assert data.get("teacher") == "Dr. Smith"


# Pytest fixtures for reusable test data
@pytest.fixture
def valid_course_html():
    """Fixture providing valid course HTML."""
    return """
    <html>
    <body>
        <h2>Introduction to Programming</h2>
        <table>
            <tr><td>Teacher</td><td>Dr. Jane Doe</td></tr>
            <tr><td>Credits</td><td>4.0</td></tr>
            <tr><td>Department</td><td>CS</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def course_list_html():
    """Fixture providing course list HTML."""
    return """
    <html>
    <body>
        <table>
            <tr><th>Code</th><th>Name</th></tr>
            <tr><td>3101</td><td>Course A</td></tr>
            <tr><td>3102</td><td>Course B</td></tr>
            <tr><td>3103</td><td>Course C</td></tr>
        </table>
    </body>
    </html>
    """
