"""
FastAPI main application module.

Entry point for the NYCU Course Platform backend API.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database.session import init_db, close_db
from backend.app.routes import courses, semesters, advanced_search, search
from backend.app.middleware.performance import setup_performance_middleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting NYCU Course Platform API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down NYCU Course Platform API...")
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_title,
    description="NYCU Course Platform API for browsing and searching university courses",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup performance middleware (compression, rate limiting, monitoring)
setup_performance_middleware(app)

# Include routers
app.include_router(semesters.router, prefix="/api/semesters", tags=["semesters"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(search.router, prefix="/api/courses", tags=["search"])
app.include_router(advanced_search.router, prefix="/api/advanced", tags=["advanced"])


@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Root endpoint providing API information.

    Returns:
        dict: API metadata
    """
    return {
        "name": settings.app_title,
        "version": settings.app_version,
        "description": "NYCU Course Platform API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "database": "connected",
    }


# Error handlers (can be extended)
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    General exception handler.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}")
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
