#!/usr/bin/env python3
"""
Installation verification script for NYCU course scraper.

This script checks that all modules can be imported and basic
functionality works as expected.
"""

import sys
from pathlib import Path


def check_imports():
    """Check that all modules can be imported."""
    print("Checking imports...")

    try:
        from app.models.course import Course
        print("  ✓ Course model")

        from app.clients.http_client import fetch_html, get_session
        print("  ✓ HTTP client")

        from app.parsers.course_parser import parse_course_html, parse_course_number_list
        print("  ✓ Course parser")

        from app.scraper import scrape_all, scrape_semester, fetch_course_data
        print("  ✓ Main scraper")

        from app.utils.file_handler import export_json, export_csv, load_json
        print("  ✓ File handler")

        print("\n✓ All imports successful!\n")
        return True

    except ImportError as e:
        print(f"\n✗ Import error: {e}\n")
        return False


def check_course_model():
    """Check Course model functionality."""
    print("Checking Course model...")

    try:
        from app.models.course import Course

        # Create a course
        course = Course(
            acy=113,
            sem=1,
            crs_no="3101",
            name="Test Course",
            teacher="Dr. Test",
            credits=3.0,
            dept="CS",
            time="Mon 10:00",
            classroom="A101",
            details={"test": "value"},
        )

        # Check to_dict
        course_dict = course.to_dict()
        assert course_dict["acy"] == 113
        assert course_dict["name"] == "Test Course"

        # Check __repr__
        repr_str = repr(course)
        assert "3101" in repr_str

        # Check __str__
        str_str = str(course)
        assert "Test Course" in str_str

        # Check equality
        course2 = Course(acy=113, sem=1, crs_no="3101")
        assert course == course2

        # Check hash
        course_set = {course, course2}
        assert len(course_set) == 1

        print("  ✓ Course model working correctly\n")
        return True

    except Exception as e:
        print(f"  ✗ Course model error: {e}\n")
        return False


def check_parser():
    """Check parser functionality."""
    print("Checking parser...")

    try:
        from app.parsers.course_parser import parse_course_html

        html = """
        <html>
        <body>
            <h2>Test Course</h2>
            <table>
                <tr><td>Teacher</td><td>Dr. Test</td></tr>
                <tr><td>Credits</td><td>3.0</td></tr>
            </table>
        </body>
        </html>
        """

        data = parse_course_html(html)
        assert data is not None
        assert isinstance(data, dict)
        assert data.get("name") == "Test Course"
        assert data.get("teacher") == "Dr. Test"
        assert data.get("credits") == 3.0

        print("  ✓ Parser working correctly\n")
        return True

    except Exception as e:
        print(f"  ✗ Parser error: {e}\n")
        return False


def check_file_handler():
    """Check file handler functionality."""
    print("Checking file handler...")

    try:
        from app.models.course import Course
        from app.utils.file_handler import export_json, load_json
        import tempfile
        import os

        # Create test course
        course = Course(acy=113, sem=1, crs_no="3101", name="Test")

        # Test export/import
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")

            # Export
            success = export_json([course], filepath)
            assert success is True
            assert os.path.exists(filepath)

            # Load
            loaded = load_json(filepath)
            assert loaded is not None
            assert len(loaded) == 1
            assert loaded[0].crs_no == "3101"

        print("  ✓ File handler working correctly\n")
        return True

    except Exception as e:
        print(f"  ✗ File handler error: {e}\n")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("NYCU Course Scraper - Installation Verification")
    print("=" * 60)
    print()

    checks = [
        check_imports,
        check_course_model,
        check_parser,
        check_file_handler,
    ]

    results = [check() for check in checks]

    print("=" * 60)
    if all(results):
        print("✓ All checks passed! Installation verified.")
        print("=" * 60)
        print()
        print("You can now run the scraper:")
        print("  python -m app --help")
        print()
        return 0
    else:
        print("✗ Some checks failed. Please review errors above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
