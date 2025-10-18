"""
API Routes Package

Contains FastAPI router definitions for all API endpoints.
"""

# Import routers here for easy access
from app.routes import courses, semesters

__all__ = ["courses", "semesters"]
