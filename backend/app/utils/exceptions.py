"""
Custom exception classes for the NYCU Course Platform.

This module defines domain-specific exceptions used throughout the application
to handle various error conditions in a consistent and meaningful way.
"""


class CourseNotFound(Exception):
    """
    Exception raised when a requested course cannot be found in the database.

    This exception should be raised when:
    - A course ID does not exist
    - A course with specific criteria cannot be found

    Attributes:
        message: Human-readable error message
        course_id: Optional course ID that was not found
    """

    def __init__(self, message: str = "Course not found", course_id: int | None = None):
        """
        Initialize CourseNotFound exception.

        Args:
            message: Error message to display
            course_id: Optional ID of the course that was not found
        """
        self.message = message
        self.course_id = course_id
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.course_id:
            return f"{self.message}: Course ID {self.course_id}"
        return self.message


class SemesterNotFound(Exception):
    """
    Exception raised when a requested semester cannot be found in the database.

    This exception should be raised when:
    - A semester ID does not exist
    - A semester with specific academic year and semester number cannot be found

    Attributes:
        message: Human-readable error message
        semester_id: Optional semester ID that was not found
        acy: Optional academic year
        sem: Optional semester number
    """

    def __init__(
        self,
        message: str = "Semester not found",
        semester_id: int | None = None,
        acy: int | None = None,
        sem: int | None = None,
    ):
        """
        Initialize SemesterNotFound exception.

        Args:
            message: Error message to display
            semester_id: Optional ID of the semester that was not found
            acy: Optional academic year
            sem: Optional semester number
        """
        self.message = message
        self.semester_id = semester_id
        self.acy = acy
        self.sem = sem
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.semester_id:
            return f"{self.message}: Semester ID {self.semester_id}"
        elif self.acy and self.sem:
            return f"{self.message}: Academic Year {self.acy}, Semester {self.sem}"
        return self.message


class InvalidQueryParameter(Exception):
    """
    Exception raised when invalid query parameters are provided to an API endpoint.

    This exception should be raised when:
    - Query parameters fail validation
    - Query parameters contain invalid values or formats
    - Required query parameters are missing

    Attributes:
        message: Human-readable error message
        parameter_name: Name of the invalid parameter
        parameter_value: Value that was provided
    """

    def __init__(
        self,
        message: str = "Invalid query parameter",
        parameter_name: str | None = None,
        parameter_value: str | None = None,
    ):
        """
        Initialize InvalidQueryParameter exception.

        Args:
            message: Error message to display
            parameter_name: Name of the invalid parameter
            parameter_value: Value that was provided
        """
        self.message = message
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.parameter_name and self.parameter_value:
            return f"{self.message}: {self.parameter_name}={self.parameter_value}"
        elif self.parameter_name:
            return f"{self.message}: {self.parameter_name}"
        return self.message


class DatabaseError(Exception):
    """
    Exception raised when a database operation fails.

    This exception should be raised when:
    - Database connection fails
    - Query execution fails
    - Transaction fails or is rolled back
    - Database integrity constraints are violated

    Attributes:
        message: Human-readable error message
        original_error: Optional original exception that was caught
    """

    def __init__(
        self,
        message: str = "Database operation failed",
        original_error: Exception | None = None,
    ):
        """
        Initialize DatabaseError exception.

        Args:
            message: Error message to display
            original_error: Optional original exception that caused this error
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.original_error:
            return f"{self.message}: {str(self.original_error)}"
        return self.message
