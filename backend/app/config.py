"""
Application Configuration

Settings management using pydantic-settings for environment-based configuration.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: Database connection string (defaults to SQLite)
        SQLALCHEMY_ECHO: Enable SQL query logging
        API_TITLE: API title for documentation
        API_VERSION: API version string
        API_PREFIX: API route prefix
        DEBUG: Enable debug mode
        CORS_ORIGINS: Allowed CORS origins
        SECRET_KEY: Secret key for JWT and encryption
    """

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./nycu_course_platform.db"
    SQLALCHEMY_ECHO: bool = False

    # API Configuration
    API_TITLE: str = "NYCU Course Platform API"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    # Application Configuration
    DEBUG: bool = False
    SECRET_KEY: str = "changeme-in-production"

    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ]

    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.DATABASE_URL

    @property
    def sqlalchemy_echo(self) -> bool:
        """Get SQLAlchemy echo setting."""
        return self.SQLALCHEMY_ECHO

    @property
    def app_title(self) -> str:
        """Get application title."""
        return self.API_TITLE

    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.API_VERSION

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins."""
        return self.CORS_ORIGINS


# Create a global settings instance
settings = Settings()
