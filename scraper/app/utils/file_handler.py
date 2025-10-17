"""
File handling utilities for importing and exporting course data.

This module provides functions for reading and writing course data
in various formats including JSON and CSV.
"""

import csv
import json
import logging
from pathlib import Path
from typing import List, Optional, Any, Dict

from app.models.course import Course


logger = logging.getLogger(__name__)


def export_json(
    courses: List[Course],
    filepath: str,
    pretty: bool = True,
    ensure_ascii: bool = False,
) -> bool:
    """
    Export a list of courses to a JSON file.

    Args:
        courses: List of Course objects to export
        filepath: Path to the output JSON file
        pretty: If True, format JSON with indentation (default: True)
        ensure_ascii: If True, escape non-ASCII characters (default: False)

    Returns:
        True if export was successful, False otherwise

    Example:
        >>> courses = [Course(acy=113, sem=1, crs_no="3101", name="Intro to CS")]
        >>> success = export_json(courses, "data/courses.json")
        >>> if success:
        ...     print("Export successful")
    """
    try:
        # Ensure the directory exists
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert courses to dictionaries
        course_dicts = [course.to_dict() for course in courses]

        # Write to JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(
                    course_dicts,
                    f,
                    ensure_ascii=ensure_ascii,
                    indent=2,
                    sort_keys=False,
                )
            else:
                json.dump(course_dicts, f, ensure_ascii=ensure_ascii)

        logger.info(
            f"Successfully exported {len(courses)} courses to {filepath} "
            f"({output_path.stat().st_size} bytes)"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to export courses to JSON: {e}", exc_info=True)
        return False


def export_csv(
    courses: List[Course],
    filepath: str,
    include_details: bool = False,
) -> bool:
    """
    Export a list of courses to a CSV file.

    Args:
        courses: List of Course objects to export
        filepath: Path to the output CSV file
        include_details: If True, serialize the details dict as a JSON string
                        column (default: False)

    Returns:
        True if export was successful, False otherwise

    Example:
        >>> courses = [Course(acy=113, sem=1, crs_no="3101", name="Intro to CS")]
        >>> success = export_csv(courses, "data/courses.csv")
        >>> if success:
        ...     print("Export successful")
    """
    if not courses:
        logger.warning("No courses to export to CSV")
        return False

    try:
        # Ensure the directory exists
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Define CSV columns
        base_columns = [
            "acy",
            "sem",
            "crs_no",
            "name",
            "teacher",
            "credits",
            "dept",
            "time",
            "classroom",
        ]

        if include_details:
            base_columns.append("details")

        # Write to CSV file
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=base_columns)
            writer.writeheader()

            for course in courses:
                row = {
                    "acy": course.acy,
                    "sem": course.sem,
                    "crs_no": course.crs_no,
                    "name": course.name or "",
                    "teacher": course.teacher or "",
                    "credits": course.credits if course.credits is not None else "",
                    "dept": course.dept or "",
                    "time": course.time or "",
                    "classroom": course.classroom or "",
                }

                if include_details:
                    # Serialize details dict to JSON string
                    row["details"] = json.dumps(course.details, ensure_ascii=False)

                writer.writerow(row)

        logger.info(
            f"Successfully exported {len(courses)} courses to {filepath} "
            f"({output_path.stat().st_size} bytes)"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to export courses to CSV: {e}", exc_info=True)
        return False


def load_json(filepath: str) -> Optional[List[Course]]:
    """
    Load courses from a JSON file.

    Args:
        filepath: Path to the JSON file to load

    Returns:
        List of Course objects if successful, None if loading fails

    Example:
        >>> courses = load_json("data/courses.json")
        >>> if courses:
        ...     print(f"Loaded {len(courses)} courses")
        ... else:
        ...     print("Failed to load courses")
    """
    try:
        file_path = Path(filepath)

        if not file_path.exists():
            logger.error(f"File not found: {filepath}")
            return None

        # Read JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            course_dicts = json.load(f)

        if not isinstance(course_dicts, list):
            logger.error(f"Invalid JSON format: expected list, got {type(course_dicts)}")
            return None

        # Convert dictionaries to Course objects
        courses: List[Course] = []
        for course_dict in course_dicts:
            try:
                # Extract details if it exists
                details = course_dict.get("details", {})

                # Handle case where details might be a JSON string
                if isinstance(details, str):
                    details = json.loads(details)

                course = Course(
                    acy=course_dict["acy"],
                    sem=course_dict["sem"],
                    crs_no=course_dict["crs_no"],
                    name=course_dict.get("name"),
                    teacher=course_dict.get("teacher"),
                    credits=course_dict.get("credits"),
                    dept=course_dict.get("dept"),
                    time=course_dict.get("time"),
                    classroom=course_dict.get("classroom"),
                    details=details,
                )
                courses.append(course)

            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid course entry: {e}")
                continue

        logger.info(f"Successfully loaded {len(courses)} courses from {filepath}")
        return courses

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load courses from JSON: {e}", exc_info=True)
        return None


def load_csv(filepath: str) -> Optional[List[Course]]:
    """
    Load courses from a CSV file.

    Args:
        filepath: Path to the CSV file to load

    Returns:
        List of Course objects if successful, None if loading fails

    Example:
        >>> courses = load_csv("data/courses.csv")
        >>> if courses:
        ...     print(f"Loaded {len(courses)} courses")
    """
    try:
        file_path = Path(filepath)

        if not file_path.exists():
            logger.error(f"File not found: {filepath}")
            return None

        courses: List[Course] = []

        # Read CSV file
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Parse credits (might be empty string)
                    credits = None
                    if row.get("credits") and row["credits"].strip():
                        try:
                            credits = float(row["credits"])
                        except ValueError:
                            pass

                    # Parse details if present (JSON string)
                    details = {}
                    if "details" in row and row["details"].strip():
                        try:
                            details = json.loads(row["details"])
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in details field: {row['details'][:50]}")

                    course = Course(
                        acy=int(row["acy"]),
                        sem=int(row["sem"]),
                        crs_no=row["crs_no"],
                        name=row.get("name") or None,
                        teacher=row.get("teacher") or None,
                        credits=credits,
                        dept=row.get("dept") or None,
                        time=row.get("time") or None,
                        classroom=row.get("classroom") or None,
                        details=details,
                    )
                    courses.append(course)

                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid CSV row: {e}")
                    continue

        logger.info(f"Successfully loaded {len(courses)} courses from {filepath}")
        return courses

    except Exception as e:
        logger.error(f"Failed to load courses from CSV: {e}", exc_info=True)
        return None


def export_by_semester(
    courses: List[Course],
    output_dir: str,
    format: str = "json",
) -> Dict[tuple[int, int], bool]:
    """
    Export courses grouped by semester into separate files.

    This function groups courses by (acy, sem) and exports each semester
    to a separate file in the specified format.

    Args:
        courses: List of Course objects to export
        output_dir: Directory to write semester files
        format: Output format, either "json" or "csv" (default: "json")

    Returns:
        Dictionary mapping (acy, sem) tuples to success status (True/False)

    Example:
        >>> courses = [
        ...     Course(acy=113, sem=1, crs_no="3101"),
        ...     Course(acy=113, sem=2, crs_no="3102"),
        ... ]
        >>> results = export_by_semester(courses, "data/semesters", format="json")
        >>> print(f"Exported {sum(results.values())} semesters successfully")
    """
    # Group courses by semester
    semester_groups: Dict[tuple[int, int], List[Course]] = {}

    for course in courses:
        key = (course.acy, course.sem)
        if key not in semester_groups:
            semester_groups[key] = []
        semester_groups[key].append(course)

    logger.info(
        f"Grouped {len(courses)} courses into {len(semester_groups)} semesters"
    )

    # Export each semester
    results: Dict[tuple[int, int], bool] = {}
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for (acy, sem), semester_courses in semester_groups.items():
        filename = f"courses_{acy}_{sem}.{format}"
        filepath = output_path / filename

        if format == "json":
            success = export_json(semester_courses, str(filepath))
        elif format == "csv":
            success = export_csv(semester_courses, str(filepath))
        else:
            logger.error(f"Unsupported format: {format}")
            success = False

        results[(acy, sem)] = success

        if success:
            logger.info(
                f"Exported {len(semester_courses)} courses for "
                f"{acy}/{sem} to {filepath}"
            )

    successful_exports = sum(results.values())
    logger.info(
        f"Exported {successful_exports}/{len(semester_groups)} semesters successfully"
    )

    return results


def merge_json_files(
    input_filepaths: List[str],
    output_filepath: str,
) -> bool:
    """
    Merge multiple JSON course files into a single file.

    Args:
        input_filepaths: List of JSON file paths to merge
        output_filepath: Path for the merged output file

    Returns:
        True if merge was successful, False otherwise

    Example:
        >>> files = ["data/113_1.json", "data/113_2.json"]
        >>> success = merge_json_files(files, "data/all_courses.json")
    """
    try:
        all_courses: List[Course] = []

        for filepath in input_filepaths:
            courses = load_json(filepath)
            if courses:
                all_courses.extend(courses)
            else:
                logger.warning(f"Skipping file: {filepath}")

        if not all_courses:
            logger.error("No courses loaded from any file")
            return False

        logger.info(
            f"Merged {len(all_courses)} courses from {len(input_filepaths)} files"
        )

        return export_json(all_courses, output_filepath)

    except Exception as e:
        logger.error(f"Failed to merge JSON files: {e}", exc_info=True)
        return False
