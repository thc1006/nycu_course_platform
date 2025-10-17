"""
Semester Pydantic schemas for API serialization.

Defines request and response schemas for semester endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SemesterBase(BaseModel):
    """Base semester schema with common fields."""

    acy: int = Field(..., description="Academic year", gt=0)
    sem: int = Field(..., description="Semester (1=Fall, 2=Spring)", ge=1, le=2)


class SemesterCreate(SemesterBase):
    """Schema for creating a new semester."""

    pass


class SemesterUpdate(BaseModel):
    """Schema for updating a semester."""

    acy: Optional[int] = Field(None, description="Academic year", gt=0)
    sem: Optional[int] = Field(None, description="Semester", ge=1, le=2)


class SemesterResponse(SemesterBase):
    """Schema for semester API responses."""

    id: int = Field(..., description="Semester ID")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "acy": 113,
                "sem": 1,
            }
        }
