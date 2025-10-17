"""
Unit tests for file handler utilities.

These tests verify file I/O operations including JSON and CSV
export/import functionality.
"""

import json
import csv
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.models.course import Course
from app.utils.file_handler import (
    export_json,
    export_csv,
    load_json,
    load_csv,
    export_by_semester,
    merge_json_files,
)


class TestExportJson:
    """Tests for export_json function."""

    def test_export_json_success(self):
        """Test successful JSON export."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101", name="Intro to CS", teacher="Dr. Smith"),
            Course(acy=113, sem=1, crs_no="3102", name="Data Structures", teacher="Dr. Jones"),
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_courses.json"
            success = export_json(courses, str(filepath))

            assert success is True
            assert filepath.exists()

            # Verify content
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data) == 2
            assert data[0]["crs_no"] == "3101"
            assert data[0]["name"] == "Intro to CS"

    def test_export_json_empty_list(self):
        """Test exporting empty course list."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "empty.json"
            success = export_json([], str(filepath))

            assert success is True
            assert filepath.exists()

            with open(filepath, "r") as f:
                data = json.load(f)

            assert data == []

    def test_export_json_creates_directory(self):
        """Test that export_json creates parent directories."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "courses.json"
            courses = [Course(acy=113, sem=1, crs_no="3101")]

            success = export_json(courses, str(filepath))

            assert success is True
            assert filepath.exists()

    def test_export_json_with_details(self):
        """Test exporting courses with details dictionary."""
        courses = [
            Course(
                acy=113,
                sem=1,
                crs_no="3101",
                name="Advanced Topics",
                details={"capacity": 30, "enrollment": 25, "prerequisites": ["CS101"]},
            )
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.json"
            success = export_json(courses, str(filepath))

            assert success is True

            with open(filepath, "r") as f:
                data = json.load(f)

            assert "details" in data[0]
            assert data[0]["details"]["capacity"] == 30
            assert "prerequisites" in data[0]["details"]


class TestExportCsv:
    """Tests for export_csv function."""

    def test_export_csv_success(self):
        """Test successful CSV export."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101", name="Intro to CS", credits=3.0),
            Course(acy=113, sem=2, crs_no="3102", name="Algorithms", credits=4.0),
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.csv"
            success = export_csv(courses, str(filepath))

            assert success is True
            assert filepath.exists()

            # Verify content
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 2
            assert rows[0]["crs_no"] == "3101"
            assert rows[0]["name"] == "Intro to CS"
            assert rows[0]["credits"] == "3.0"

    def test_export_csv_with_details(self):
        """Test CSV export with details field."""
        courses = [
            Course(
                acy=113,
                sem=1,
                crs_no="3101",
                details={"capacity": 30, "room": "A101"},
            )
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.csv"
            success = export_csv(courses, str(filepath), include_details=True)

            assert success is True

            with open(filepath, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert "details" in rows[0]
            details = json.loads(rows[0]["details"])
            assert details["capacity"] == 30

    def test_export_csv_empty_list(self):
        """Test exporting empty course list to CSV."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "empty.csv"
            success = export_csv([], str(filepath))

            assert success is False  # Should return False for empty list

    def test_export_csv_with_none_values(self):
        """Test CSV export handles None values."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101", name=None, teacher=None, credits=None)
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.csv"
            success = export_csv(courses, str(filepath))

            assert success is True

            with open(filepath, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert rows[0]["name"] == ""
            assert rows[0]["teacher"] == ""


class TestLoadJson:
    """Tests for load_json function."""

    def test_load_json_success(self):
        """Test successful JSON loading."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101", name="Intro to CS"),
            Course(acy=113, sem=2, crs_no="3102", name="Algorithms"),
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.json"
            export_json(courses, str(filepath))

            loaded_courses = load_json(str(filepath))

            assert loaded_courses is not None
            assert len(loaded_courses) == 2
            assert loaded_courses[0].crs_no == "3101"
            assert loaded_courses[1].name == "Algorithms"

    def test_load_json_file_not_found(self):
        """Test loading from non-existent file."""
        loaded = load_json("/nonexistent/path/courses.json")

        assert loaded is None

    def test_load_json_invalid_json(self):
        """Test loading invalid JSON file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "invalid.json"
            with open(filepath, "w") as f:
                f.write("{invalid json content")

            loaded = load_json(str(filepath))

            assert loaded is None

    def test_load_json_with_details(self):
        """Test loading courses with details field."""
        courses = [
            Course(
                acy=113,
                sem=1,
                crs_no="3101",
                details={"capacity": 50, "location": "Building A"},
            )
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.json"
            export_json(courses, str(filepath))

            loaded = load_json(str(filepath))

            assert loaded is not None
            assert len(loaded[0].details) > 0
            assert loaded[0].details["capacity"] == 50


class TestLoadCsv:
    """Tests for load_csv function."""

    def test_load_csv_success(self):
        """Test successful CSV loading."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101", name="Intro to CS", credits=3.0),
            Course(acy=113, sem=2, crs_no="3102", name="Algorithms", credits=4.0),
        ]

        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.csv"
            export_csv(courses, str(filepath))

            loaded = load_csv(str(filepath))

            assert loaded is not None
            assert len(loaded) == 2
            assert loaded[0].crs_no == "3101"
            assert loaded[0].credits == 3.0

    def test_load_csv_file_not_found(self):
        """Test loading from non-existent CSV file."""
        loaded = load_csv("/nonexistent/courses.csv")

        assert loaded is None

    def test_load_csv_with_empty_credits(self):
        """Test loading CSV with empty credit values."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "courses.csv"

            # Write CSV with empty credits
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["acy", "sem", "crs_no", "name", "teacher", "credits", "dept", "time", "classroom"],
                )
                writer.writeheader()
                writer.writerow({
                    "acy": "113",
                    "sem": "1",
                    "crs_no": "3101",
                    "name": "Test",
                    "teacher": "Dr. Test",
                    "credits": "",
                    "dept": "CS",
                    "time": "",
                    "classroom": "",
                })

            loaded = load_csv(str(filepath))

            assert loaded is not None
            assert len(loaded) == 1
            assert loaded[0].credits is None


class TestExportBySemester:
    """Tests for export_by_semester function."""

    def test_export_by_semester_json(self):
        """Test exporting courses grouped by semester."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101", name="Course A"),
            Course(acy=113, sem=1, crs_no="3102", name="Course B"),
            Course(acy=113, sem=2, crs_no="4101", name="Course C"),
            Course(acy=114, sem=1, crs_no="5101", name="Course D"),
        ]

        with TemporaryDirectory() as tmpdir:
            results = export_by_semester(courses, tmpdir, format="json")

            assert len(results) == 3
            assert results[(113, 1)] is True
            assert results[(113, 2)] is True
            assert results[(114, 1)] is True

            # Verify files exist
            assert (Path(tmpdir) / "courses_113_1.json").exists()
            assert (Path(tmpdir) / "courses_113_2.json").exists()
            assert (Path(tmpdir) / "courses_114_1.json").exists()

            # Verify content
            loaded = load_json(str(Path(tmpdir) / "courses_113_1.json"))
            assert len(loaded) == 2

    def test_export_by_semester_csv(self):
        """Test exporting by semester in CSV format."""
        courses = [
            Course(acy=113, sem=1, crs_no="3101"),
            Course(acy=113, sem=2, crs_no="3102"),
        ]

        with TemporaryDirectory() as tmpdir:
            results = export_by_semester(courses, tmpdir, format="csv")

            assert len(results) == 2
            assert (Path(tmpdir) / "courses_113_1.csv").exists()
            assert (Path(tmpdir) / "courses_113_2.csv").exists()


class TestMergeJsonFiles:
    """Tests for merge_json_files function."""

    def test_merge_json_files_success(self):
        """Test merging multiple JSON files."""
        courses1 = [
            Course(acy=113, sem=1, crs_no="3101"),
            Course(acy=113, sem=1, crs_no="3102"),
        ]
        courses2 = [
            Course(acy=113, sem=2, crs_no="4101"),
        ]

        with TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "courses1.json"
            file2 = Path(tmpdir) / "courses2.json"
            output = Path(tmpdir) / "merged.json"

            export_json(courses1, str(file1))
            export_json(courses2, str(file2))

            success = merge_json_files([str(file1), str(file2)], str(output))

            assert success is True
            assert output.exists()

            # Verify merged content
            merged = load_json(str(output))
            assert len(merged) == 3

    def test_merge_json_files_empty_list(self):
        """Test merging with empty file list."""
        with TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "merged.json"
            success = merge_json_files([], str(output))

            assert success is False

    def test_merge_json_files_with_invalid_file(self):
        """Test merging when some files are invalid."""
        courses = [Course(acy=113, sem=1, crs_no="3101")]

        with TemporaryDirectory() as tmpdir:
            valid_file = Path(tmpdir) / "valid.json"
            invalid_file = Path(tmpdir) / "invalid.json"
            output = Path(tmpdir) / "merged.json"

            export_json(courses, str(valid_file))

            # Create invalid JSON file
            with open(invalid_file, "w") as f:
                f.write("{invalid}")

            success = merge_json_files(
                [str(valid_file), str(invalid_file)],
                str(output),
            )

            # Should still succeed with valid file
            assert success is True
            merged = load_json(str(output))
            assert len(merged) >= 1


# Pytest fixtures
@pytest.fixture
def sample_courses():
    """Fixture providing sample course data."""
    return [
        Course(acy=113, sem=1, crs_no="3101", name="Intro to CS", teacher="Dr. Smith", credits=3.0),
        Course(acy=113, sem=1, crs_no="3102", name="Data Structures", teacher="Dr. Jones", credits=3.0),
        Course(acy=113, sem=2, crs_no="5001", name="Algorithms", teacher="Dr. Brown", credits=4.0),
    ]


@pytest.fixture
def temp_directory():
    """Fixture providing a temporary directory."""
    with TemporaryDirectory() as tmpdir:
        yield tmpdir
