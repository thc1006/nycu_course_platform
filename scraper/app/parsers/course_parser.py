"""
HTML parser for NYCU course data.

This module provides functions to parse HTML content from NYCU timetable
pages and extract structured course information.
"""

import logging
import re
from typing import Dict, List, Optional, Any

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def parse_course_html(html: str) -> Dict[str, Any]:
    """
    Parse HTML from a course detail page and extract course information.

    This function parses the HTML content of a course syllabus/detail page
    and extracts structured information including course name, teacher,
    credits, department, schedule, and other details.

    Args:
        html: HTML content as a string

    Returns:
        Dictionary containing extracted course data. Returns empty dict
        if parsing fails. Common keys include:
        - name: Course name/title
        - teacher: Instructor name(s)
        - credits: Number of credits
        - dept: Department code
        - time: Schedule/time information
        - classroom: Classroom location
        - permanent_crs_no: Permanent course number
        - required: Whether course is required
        - description: Course description
        - evaluation: Evaluation methods
        - capacity: Class capacity
        - current_enrollment: Current number of enrolled students

    Example:
        >>> html = "<html>...</html>"
        >>> data = parse_course_html(html)
        >>> print(data.get('name', 'Unknown'))
        'Introduction to Computer Science'
    """
    if not html or not html.strip():
        logger.warning("Empty HTML provided to parser")
        return {}

    try:
        soup = BeautifulSoup(html, "html.parser")
        data: Dict[str, Any] = {}

        # Parse course title
        # Common patterns: <h2>, <h3>, or element with class "course-title"
        title_elem = (
            soup.find("h2")
            or soup.find("h3", class_=re.compile(r"(course|title)", re.I))
            or soup.find(class_=re.compile(r"course.*title", re.I))
        )
        if title_elem:
            data["name"] = title_elem.get_text(strip=True)
            logger.debug(f"Parsed course name: {data['name']}")

        # Parse teacher/instructor
        # Look for elements with keywords like "teacher", "instructor", "授課教師"
        teacher_elem = soup.find(
            text=re.compile(r"(teacher|instructor|授課教師|教師)", re.I)
        )
        if teacher_elem:
            # Get the next sibling or parent's next element
            parent = teacher_elem.parent
            if parent:
                # Try to find the value in next sibling or same row
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    data["teacher"] = value_elem.get_text(strip=True)
                    logger.debug(f"Parsed teacher: {data['teacher']}")

        # Parse credits
        # Look for patterns like "3.0 credits", "學分: 3", etc.
        credits_text = soup.find(
            text=re.compile(r"(credit|學分|credits)", re.I)
        )
        if credits_text:
            parent = credits_text.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    credits_str = value_elem.get_text(strip=True)
                    # Extract numeric value
                    match = re.search(r"(\d+\.?\d*)", credits_str)
                    if match:
                        try:
                            data["credits"] = float(match.group(1))
                            logger.debug(f"Parsed credits: {data['credits']}")
                        except ValueError:
                            pass

        # Parse department
        dept_elem = soup.find(
            text=re.compile(r"(department|dept|系所|開課系所)", re.I)
        )
        if dept_elem:
            parent = dept_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    data["dept"] = value_elem.get_text(strip=True)
                    logger.debug(f"Parsed department: {data['dept']}")

        # Parse time/schedule
        time_elem = soup.find(
            text=re.compile(r"(time|schedule|上課時間|時間)", re.I)
        )
        if time_elem:
            parent = time_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    data["time"] = value_elem.get_text(strip=True)
                    logger.debug(f"Parsed time: {data['time']}")

        # Parse classroom
        classroom_elem = soup.find(
            text=re.compile(r"(classroom|room|教室|上課教室)", re.I)
        )
        if classroom_elem:
            parent = classroom_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    data["classroom"] = value_elem.get_text(strip=True)
                    logger.debug(f"Parsed classroom: {data['classroom']}")

        # Parse permanent course number
        perm_crs_elem = soup.find(
            text=re.compile(r"(permanent.*number|永久課號)", re.I)
        )
        if perm_crs_elem:
            parent = perm_crs_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    data["permanent_crs_no"] = value_elem.get_text(strip=True)

        # Parse required/elective status
        required_elem = soup.find(
            text=re.compile(r"(required|必選修|必修|選修)", re.I)
        )
        if required_elem:
            parent = required_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    required_text = value_elem.get_text(strip=True).lower()
                    data["required"] = "required" in required_text or "必修" in required_text

        # Parse course description
        desc_elem = soup.find(
            text=re.compile(r"(description|課程描述|課程簡介)", re.I)
        )
        if desc_elem:
            parent = desc_elem.parent
            if parent:
                # Description might be in a larger text block
                value_elem = (
                    parent.find_next_sibling()
                    or parent.find_next("td")
                    or parent.find_next("div")
                )
                if value_elem:
                    data["description"] = value_elem.get_text(strip=True)

        # Parse evaluation methods
        eval_elem = soup.find(
            text=re.compile(r"(evaluation|grading|評分|成績考核)", re.I)
        )
        if eval_elem:
            parent = eval_elem.parent
            if parent:
                value_elem = (
                    parent.find_next_sibling()
                    or parent.find_next("td")
                    or parent.find_next("div")
                )
                if value_elem:
                    data["evaluation"] = value_elem.get_text(strip=True)

        # Parse capacity and enrollment
        capacity_elem = soup.find(
            text=re.compile(r"(capacity|限修人數|人數上限)", re.I)
        )
        if capacity_elem:
            parent = capacity_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    capacity_str = value_elem.get_text(strip=True)
                    match = re.search(r"(\d+)", capacity_str)
                    if match:
                        try:
                            data["capacity"] = int(match.group(1))
                        except ValueError:
                            pass

        enrollment_elem = soup.find(
            text=re.compile(r"(enrollment|current.*enroll|已選人數)", re.I)
        )
        if enrollment_elem:
            parent = enrollment_elem.parent
            if parent:
                value_elem = parent.find_next_sibling() or parent.find_next("td")
                if value_elem:
                    enrollment_str = value_elem.get_text(strip=True)
                    match = re.search(r"(\d+)", enrollment_str)
                    if match:
                        try:
                            data["current_enrollment"] = int(match.group(1))
                        except ValueError:
                            pass

        logger.info(f"Successfully parsed course data with {len(data)} fields")
        return data

    except Exception as e:
        logger.error(f"Error parsing course HTML: {e}", exc_info=True)
        return {}


def parse_course_number_list(html: str) -> List[str]:
    """
    Parse HTML from a course list/search results page and extract course numbers.

    This function parses the HTML content of a course list or search results
    page and extracts all course numbers found in the table or grid. It uses
    multiple strategies to handle different HTML structures from NYCU timetable.

    Args:
        html: HTML content as a string

    Returns:
        List of course numbers (as strings). Returns empty list if parsing
        fails or no course numbers are found.

    Example:
        >>> html = "<table>...</table>"
        >>> numbers = parse_course_number_list(html)
        >>> print(numbers)
        ['3101', '3102', '3103', '5001', '5002']
    """
    if not html or not html.strip():
        logger.warning("Empty HTML provided to course number parser")
        return []

    try:
        soup = BeautifulSoup(html, "html.parser")
        course_numbers: List[str] = []

        # Strategy 1: Look for links to course detail pages (most reliable)
        # NYCU timetable uses links with CrsNo parameter
        links = soup.find_all("a", href=re.compile(r"CrsNo=", re.I))
        for link in links:
            href = link.get("href", "")
            # Extract course number from URL parameter
            match = re.search(r"CrsNo=([A-Z0-9]+)", href, re.I)
            if match:
                crs_no = match.group(1)
                course_numbers.append(crs_no)
                logger.debug(f"Found course number from link: {crs_no}")

        # Strategy 2: Look for table with course data
        # Common patterns: table with id/class containing "course", "list", etc.
        if not course_numbers:
            tables = soup.find_all(
                "table", id=re.compile(r"(course|list)", re.I)
            ) or soup.find_all("table", class_=re.compile(r"(course|list)", re.I))

            if not tables:
                # Fallback: find all tables
                tables = soup.find_all("table")

            for table in tables:
                # Look for rows (skip header row)
                rows = table.find_all("tr")

                # Try to identify header row and data rows
                header_row = None
                data_rows = []

                for i, row in enumerate(rows):
                    cells = row.find_all(["td", "th"])
                    if not cells:
                        continue

                    # First row with th tags is likely the header
                    if i == 0 and row.find_all("th"):
                        header_row = row
                        continue

                    data_rows.append(row)

                # Process data rows
                for row in data_rows:
                    cells = row.find_all(["td", "th"])
                    if not cells:
                        continue

                    # Check each cell for course number patterns
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)

                        # NYCU course numbers are typically 4-7 alphanumeric characters
                        # Examples: 3101, DCP1234, EE101
                        match = re.match(r"^([A-Z0-9]{4,7})$", cell_text, re.I)
                        if match:
                            crs_no = match.group(1)
                            course_numbers.append(crs_no)
                            logger.debug(f"Found course number from table: {crs_no}")
                            break  # Move to next row after finding course number

        # Strategy 3: Look for divs or other elements with course data
        if not course_numbers:
            # Try to find course items in div structures
            course_divs = soup.find_all(
                "div", class_=re.compile(r"(course|item|result)", re.I)
            )
            for div in course_divs:
                # Look for course numbers in text content
                text = div.get_text(strip=True)
                matches = re.findall(r"\b([A-Z0-9]{4,7})\b", text, re.I)
                for match in matches:
                    # Validate that it looks like a course number
                    if re.match(r"^[A-Z0-9]{4,7}$", match, re.I):
                        course_numbers.append(match)
                        logger.debug(f"Found course number from div: {match}")

        # Strategy 4: Search for JSON data embedded in page
        if not course_numbers:
            # Look for script tags that might contain JSON data
            scripts = soup.find_all("script", type="application/json")
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    # Look for course numbers in JSON structure
                    if isinstance(data, dict):
                        # Common keys: courses, items, data, results
                        for key in ["courses", "items", "data", "results"]:
                            if key in data and isinstance(data[key], list):
                                for item in data[key]:
                                    if isinstance(item, dict):
                                        # Look for course number fields
                                        for field in ["crs_no", "course_no", "CrsNo", "courseNo"]:
                                            if field in item:
                                                course_numbers.append(str(item[field]))
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.debug(f"Failed to parse JSON from script tag: {e}")

        logger.info(f"Parsed {len(course_numbers)} course numbers from HTML")
        return course_numbers

    except Exception as e:
        logger.error(f"Error parsing course number list: {e}", exc_info=True)
        return []


def extract_table_data(html: str, table_selector: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Extract structured data from an HTML table.

    This is a utility function that can parse any HTML table and convert
    it into a list of dictionaries where keys are column headers.

    Args:
        html: HTML content as a string
        table_selector: Optional CSS selector to identify the table.
                       If None, uses the first table found.

    Returns:
        List of dictionaries, one per table row (excluding header).
        Each dict maps column names to cell values.

    Example:
        >>> html = '<table><tr><th>Name</th><th>Code</th></tr>...'
        >>> data = extract_table_data(html)
        >>> print(data[0])
        {'Name': 'Intro to CS', 'Code': '3101'}
    """
    if not html or not html.strip():
        return []

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Find the table
        if table_selector:
            table = soup.select_one(table_selector)
        else:
            table = soup.find("table")

        if not table:
            logger.warning("No table found in HTML")
            return []

        # Extract headers
        header_row = table.find("tr")
        if not header_row:
            return []

        headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

        # Extract data rows
        data_rows = []
        for row in table.find_all("tr")[1:]:  # Skip header row
            cells = row.find_all(["td", "th"])
            if len(cells) == len(headers):
                row_data = {
                    headers[i]: cells[i].get_text(strip=True)
                    for i in range(len(headers))
                }
                data_rows.append(row_data)

        logger.debug(f"Extracted {len(data_rows)} rows from table")
        return data_rows

    except Exception as e:
        logger.error(f"Error extracting table data: {e}", exc_info=True)
        return []
