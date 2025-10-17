# NYCU Course Platform - Developer Guide

Comprehensive development guide for contributing to the NYCU Course Platform.

## Table of Contents

- [Overview](#overview)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development Workflow](#development-workflow)
- [Running Tests](#running-tests)
- [Code Style Guide](#code-style-guide)
- [API Development](#api-development)
- [Frontend Development](#frontend-development)
- [Contributing Guidelines](#contributing-guidelines)

## Overview

The NYCU Course Platform is a full-stack web application built with modern technologies:
- **Frontend:** Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **Backend:** FastAPI + Python 3.10+ + SQLModel
- **Database:** SQLite (70,239 courses, 9 semesters)
- **Deployment:** Docker + Nginx + systemd

**Production Stats:**
- Domain: nymu.com.tw
- Courses: 70,239
- Semesters: 110-1 through 114-1
- API Response Time: < 100ms

## Development Environment Setup

### Prerequisites

**Required Software:**
- Python 3.10+ (Backend)
- Node.js 18+ (Frontend)
- Git 2.30+
- SQLite 3.31+
- Text Editor/IDE (VSCode recommended)

**Optional Tools:**
- Docker 20+ (for containerized development)
- Postman/Insomnia (API testing)
- DBeaver/DB Browser for SQLite (database management)

### Initial Setup

#### 1. Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd nycu_course_platform

# Create your feature branch
git checkout -b feature/your-feature-name
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
python -m pytest --version
black --version
mypy --version
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Install additional development tools
npm install --save-dev @types/node @types/react

# Verify installation
npm list
node --version
npm --version
```

#### 4. Database Setup

```bash
# Return to project root
cd /home/thc1006/dev/nycu_course_platform

# Option 1: Use production database (70K courses)
# Database file already exists at: nycu_course_platform.db

# Option 2: Create fresh database with seed data
cd backend/scripts
python seed_db.py

# Verify database
sqlite3 ../nycu_course_platform.db "SELECT COUNT(*) FROM course;"
```

#### 5. Environment Configuration

**Backend Environment:**

Create `backend/.env`:
```bash
# Application
APP_NAME="NYCU Course Platform"
APP_VERSION="1.0.0"
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///../nycu_course_platform.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Logging
LOG_LEVEL=DEBUG
```

**Frontend Environment:**

Create `frontend/.env.local`:
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Application
NEXT_PUBLIC_APP_NAME="NYCU Course Platform"
NEXT_PUBLIC_APP_VERSION="1.0.0"

# Environment
NODE_ENV=development
```

### Running Development Servers

#### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000

# Output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

Access:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Terminal 2: Frontend

```bash
cd frontend
npm run dev

# Output:
# ready - started server on 0.0.0.0:3000
# info  - Using webpack 5
```

Access:
- Frontend: http://localhost:3000

#### Terminal 3: Database Management (Optional)

```bash
# Open database with SQLite CLI
sqlite3 nycu_course_platform.db

# Common commands:
.tables           # List tables
.schema course    # Show table schema
SELECT * FROM course LIMIT 5;
.quit
```

## Project Structure

```
nycu_course_platform/
├── backend/                      # Backend API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── models/              # Database models (SQLModel)
│   │   │   ├── __init__.py
│   │   │   ├── course.py        # Course model
│   │   │   └── semester.py      # Semester model
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── course.py        # Course schemas
│   │   │   └── semester.py      # Semester schemas
│   │   ├── database/            # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Database base
│   │   │   ├── session.py       # Session management
│   │   │   ├── course.py        # Course queries
│   │   │   └── semester.py      # Semester queries
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── course_service.py
│   │   │   ├── semester_service.py
│   │   │   └── advanced_search_service.py
│   │   ├── routes/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── courses.py       # Course endpoints
│   │   │   ├── semesters.py     # Semester endpoints
│   │   │   └── advanced_search.py
│   │   └── utils/               # Utility functions
│   │       ├── __init__.py
│   │       ├── exceptions.py    # Custom exceptions
│   │       └── cache.py         # Caching utilities
│   ├── tests/                   # Test suite
│   │   ├── conftest.py          # Pytest configuration
│   │   ├── test_routes/         # Route tests
│   │   ├── test_services/       # Service tests
│   │   └── test_database/       # Database tests
│   ├── scripts/                 # Utility scripts
│   │   ├── seed_db.py           # Database seeding
│   │   └── import_data.py       # Data import
│   ├── requirements.txt         # Python dependencies
│   ├── requirements-dev.txt     # Development dependencies
│   └── pytest.ini               # Pytest configuration
│
├── frontend/                    # Frontend application
│   ├── pages/                   # Next.js pages
│   │   ├── _app.tsx             # Application wrapper
│   │   ├── _document.tsx        # Document wrapper
│   │   ├── index.tsx            # Home page (course explorer)
│   │   ├── browse.tsx           # Advanced browse page
│   │   ├── schedule.tsx         # Schedule builder
│   │   ├── course/
│   │   │   └── [id].tsx         # Course detail page
│   │   ├── 404.tsx              # Not found page
│   │   └── 500.tsx              # Server error page
│   ├── components/              # React components
│   │   ├── index.ts             # Component exports
│   │   ├── common/              # Common components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── Error.tsx
│   │   ├── course/              # Course components
│   │   │   ├── CourseCard.tsx
│   │   │   ├── CourseList.tsx
│   │   │   ├── CourseDetail.tsx
│   │   │   └── CourseSkeleton.tsx
│   │   ├── form/                # Form components
│   │   │   ├── SearchInput.tsx
│   │   │   ├── SemesterSelect.tsx
│   │   │   └── DepartmentFilter.tsx
│   │   ├── schedule/            # Schedule components
│   │   │   ├── ScheduleGrid.tsx
│   │   │   ├── CourseSlot.tsx
│   │   │   └── ConflictWarning.tsx
│   │   ├── Filters/             # Filter components
│   │   │   └── AdvancedFilter.tsx
│   │   └── Layout/              # Layout components
│   │       ├── MainLayout.tsx
│   │       └── Header.tsx
│   ├── lib/                     # Library code
│   │   └── hooks/               # Custom React hooks
│   │       ├── useCourses.ts
│   │       └── useSemesters.ts
│   ├── utils/                   # Utility functions
│   │   ├── scheduleExport.ts    # Schedule export
│   │   ├── courseComparison.ts  # Course comparison
│   │   ├── conflictDetection.ts # Conflict detection
│   │   └── reviews.ts           # Course reviews
│   ├── styles/                  # Styles
│   │   └── globals.css          # Global CSS
│   ├── public/                  # Static files
│   │   └── locales/             # Translations
│   │       ├── en-US/
│   │       └── zh-TW/
│   ├── __tests__/               # Tests
│   │   ├── components/          # Component tests
│   │   ├── utils/               # Utility tests
│   │   └── e2e/                 # E2E tests
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── next.config.js           # Next.js config
│   ├── tailwind.config.js       # Tailwind config
│   ├── jest.config.js           # Jest config
│   └── playwright.config.ts     # Playwright config
│
├── nycu_course_platform.db      # SQLite database (70,239 courses)
├── docker-compose.yml           # Docker compose configuration
├── Dockerfile.backend           # Backend Docker image
├── Dockerfile.frontend          # Frontend Docker image
├── nginx.conf                   # Nginx configuration
└── README.md                    # Project README
```

### Key Files and Their Purpose

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application entry point |
| `backend/app/config.py` | Application configuration |
| `backend/app/models/course.py` | Course database model |
| `backend/app/routes/courses.py` | Course API endpoints |
| `frontend/pages/index.tsx` | Home page (course explorer) |
| `frontend/components/course/CourseCard.tsx` | Course card component |
| `frontend/lib/hooks/useCourses.ts` | Custom hook for fetching courses |
| `nycu_course_platform.db` | SQLite database file |

## Technology Stack

### Backend Stack

**Framework & Core:**
- **FastAPI 0.104+:** Modern, fast web framework
- **Uvicorn:** ASGI server
- **SQLModel:** ORM combining SQLAlchemy and Pydantic
- **Pydantic:** Data validation

**Database:**
- **SQLite 3.31+:** Lightweight database (70K+ courses)
- Future: PostgreSQL for horizontal scaling

**Development Tools:**
- **pytest:** Testing framework
- **black:** Code formatter
- **mypy:** Type checker
- **flake8:** Linter

### Frontend Stack

**Framework & Core:**
- **Next.js 14:** React framework with SSR/SSG
- **React 18:** UI library
- **TypeScript 5:** Type-safe JavaScript
- **Tailwind CSS 3:** Utility-first CSS

**State & Data:**
- **SWR:** Data fetching and caching
- **Axios:** HTTP client
- **LocalStorage:** Client-side persistence

**Development Tools:**
- **Jest:** Unit testing
- **Playwright:** E2E testing
- **ESLint:** Code linter
- **Prettier:** Code formatter

### DevOps & Deployment

- **Docker:** Containerization
- **Docker Compose:** Multi-container orchestration
- **Nginx:** Reverse proxy and load balancer
- **Certbot:** SSL certificate management
- **systemd:** Service management

## Development Workflow

### Feature Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/add-course-ratings

# 2. Develop feature
# - Write code
# - Add tests
# - Update documentation

# 3. Run tests
cd backend && pytest
cd frontend && npm test

# 4. Check code quality
cd backend && black . && mypy .
cd frontend && npm run lint

# 5. Commit changes
git add .
git commit -m "feat: add course rating system"

# 6. Push to remote
git push origin feature/add-course-ratings

# 7. Create pull request
# - Describe changes
# - Link related issues
# - Request review
```

### Git Commit Convention

Follow Conventional Commits:

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

Examples:
```bash
git commit -m "feat: add course rating API endpoint"
git commit -m "fix: resolve schedule conflict detection bug"
git commit -m "docs: update API documentation for courses endpoint"
git commit -m "test: add unit tests for course service"
```

### Code Review Checklist

**Before Submitting PR:**
- [ ] All tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No console.log or debug prints
- [ ] Error handling implemented
- [ ] Performance tested (if applicable)
- [ ] Security reviewed (if applicable)

**Reviewer Checklist:**
- [ ] Code is readable and maintainable
- [ ] Tests are comprehensive
- [ ] Documentation is clear
- [ ] No obvious bugs or security issues
- [ ] Follows project conventions
- [ ] Performance is acceptable

## Running Tests

### Backend Testing

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_routes/test_course_routes.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_routes/test_course_routes.py::test_list_courses -v

# Run tests matching pattern
pytest -k "course"

# Generate coverage report
pytest --cov=app --cov-report=term-missing
```

**Test Structure:**

```python
# tests/test_routes/test_course_routes.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_courses():
    """Test listing courses endpoint."""
    response = client.get("/api/courses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_course():
    """Test getting single course."""
    response = client.get("/api/courses/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data

@pytest.mark.parametrize("acy,sem", [
    (113, 1),
    (113, 2),
    (114, 1),
])
def test_filter_by_semester(acy, sem):
    """Test filtering courses by semester."""
    response = client.get(f"/api/courses/?acy={acy}&sem={sem}")
    assert response.status_code == 200
```

### Frontend Testing

**Unit Tests (Jest):**

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test CourseCard.test.tsx

# Update snapshots
npm test -- -u
```

**E2E Tests (Playwright):**

```bash
cd frontend

# Install browsers (first time only)
npx playwright install

# Run all E2E tests
npm run e2e

# Run with UI mode
npm run e2e:ui

# Run specific test
npx playwright test home.spec.ts

# Debug test
npx playwright test --debug
```

**Test Examples:**

```typescript
// __tests__/components/CourseCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { CourseCard } from '@/components/course/CourseCard';

describe('CourseCard', () => {
  const mockCourse = {
    id: 1,
    crs_no: 'CS1001',
    name: 'Introduction to Computer Science',
    teacher: 'Dr. Smith',
    credits: 3.0,
    dept: 'CS',
    time: 'Mon 10:00-12:00',
    classroom: 'A101',
  };

  it('renders course information correctly', () => {
    render(<CourseCard {...mockCourse} onAddToSchedule={() => {}} />);

    expect(screen.getByText('CS1001')).toBeInTheDocument();
    expect(screen.getByText('Introduction to Computer Science')).toBeInTheDocument();
    expect(screen.getByText('Dr. Smith')).toBeInTheDocument();
  });

  it('calls onAddToSchedule when button clicked', () => {
    const mockAdd = jest.fn();
    render(<CourseCard {...mockCourse} onAddToSchedule={mockAdd} />);

    const addButton = screen.getByText('Add to Schedule');
    fireEvent.click(addButton);

    expect(mockAdd).toHaveBeenCalledWith(1);
  });
});
```

```typescript
// __tests__/e2e/home.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should display course explorer', async ({ page }) => {
    await page.goto('http://localhost:3000');

    // Check page title
    await expect(page).toHaveTitle(/NYCU Course Platform/);

    // Check search input exists
    const searchInput = page.locator('input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();

    // Check course cards are rendered
    const courseCards = page.locator('[data-testid="course-card"]');
    await expect(courseCards).toHaveCount(50); // Default limit
  });

  test('should filter courses by semester', async ({ page }) => {
    await page.goto('http://localhost:3000');

    // Select semester
    await page.selectOption('select[name="semester"]', '113-1');

    // Wait for results
    await page.waitForLoadState('networkidle');

    // Verify results
    const courseCards = page.locator('[data-testid="course-card"]');
    await expect(courseCards.first()).toBeVisible();
  });
});
```

## Code Style Guide

### Python (Backend) Style Guide

**Follow PEP 8 with Black formatter:**

```python
# Good: Clear, typed, documented
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_session
from backend.app.schemas.course import CourseResponse
from backend.app.services.course_service import CourseService


router = APIRouter()


@router.get("/courses/", response_model=List[CourseResponse])
async def list_courses(
    acy: Optional[int] = None,
    sem: Optional[int] = None,
    limit: int = 200,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> List[CourseResponse]:
    """
    List courses with optional filtering.

    Args:
        acy: Academic year filter
        sem: Semester filter (1=Fall, 2=Spring)
        limit: Maximum results (1-1000)
        offset: Pagination offset
        session: Database session

    Returns:
        List of courses matching criteria

    Raises:
        HTTPException: If query fails
    """
    try:
        service = CourseService(session)
        courses = await service.list_courses(
            acy=acy,
            sem=sem,
            limit=limit,
            offset=offset,
        )
        return [CourseResponse.from_orm(c) for c in courses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Key Principles:**
- Use type hints for all function parameters and returns
- Write docstrings for all public functions/classes
- Use async/await for I/O operations
- Handle exceptions appropriately
- Keep functions focused and single-purpose

### TypeScript (Frontend) Style Guide

**Follow Airbnb TypeScript Style Guide:**

```typescript
// Good: Typed, documented, organized
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Course {
  id: number;
  crs_no: string;
  name: string;
  teacher: string;
  credits: number;
  dept: string;
  time: string;
  classroom: string;
}

interface CourseCardProps {
  course: Course;
  onAddToSchedule: (id: number) => void;
}

/**
 * Course card component displaying course information
 *
 * @param props Component props
 * @returns React component
 */
export const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onAddToSchedule,
}) => {
  const [isAdded, setIsAdded] = useState(false);

  const handleAdd = () => {
    onAddToSchedule(course.id);
    setIsAdded(true);
  };

  return (
    <div className="border rounded-lg p-4 shadow-md">
      <h3 className="text-lg font-bold">{course.crs_no}</h3>
      <p className="text-gray-700">{course.name}</p>
      <p className="text-sm text-gray-500">{course.teacher}</p>
      <button
        onClick={handleAdd}
        disabled={isAdded}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        {isAdded ? 'Added' : 'Add to Schedule'}
      </button>
    </div>
  );
};
```

**Key Principles:**
- Define interfaces for all props and data structures
- Use functional components with hooks
- Destructure props for clarity
- Use meaningful variable and function names
- Add JSDoc comments for complex components

### CSS/Tailwind Style Guide

```tsx
// Good: Organized, responsive, semantic
<div className="
  container mx-auto px-4 py-8
  max-w-7xl
  bg-white dark:bg-gray-900
  rounded-lg shadow-lg
  hover:shadow-xl transition-shadow
  sm:px-6 lg:px-8
">
  <h1 className="
    text-3xl font-bold text-gray-900 dark:text-white
    mb-4
    sm:text-4xl
  ">
    Course Catalog
  </h1>
  <p className="text-gray-600 dark:text-gray-400">
    Browse 70,000+ courses
  </p>
</div>
```

**Key Principles:**
- Group related utilities together
- Use responsive modifiers (sm:, md:, lg:)
- Support dark mode with dark: modifier
- Use semantic class names when creating custom classes
- Keep utility classes organized and readable

## API Development

### Adding a New API Endpoint

1. **Define Model (if needed):**

```python
# backend/app/models/rating.py
from typing import Optional
from sqlmodel import Field, SQLModel

class Rating(SQLModel, table=True):
    """Course rating model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id")
    user_id: int
    rating: float = Field(ge=0, le=5)
    comment: Optional[str] = None
```

2. **Define Schema:**

```python
# backend/app/schemas/rating.py
from typing import Optional
from pydantic import BaseModel, Field

class RatingCreate(BaseModel):
    """Schema for creating rating."""
    course_id: int
    user_id: int
    rating: float = Field(ge=0, le=5)
    comment: Optional[str] = None

class RatingResponse(BaseModel):
    """Schema for rating response."""
    id: int
    course_id: int
    user_id: int
    rating: float
    comment: Optional[str]

    class Config:
        from_attributes = True
```

3. **Create Service:**

```python
# backend/app/services/rating_service.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.rating import Rating
from backend.app.schemas.rating import RatingCreate

class RatingService:
    """Service for rating operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_rating(self, data: RatingCreate) -> Rating:
        """Create new rating."""
        rating = Rating(**data.dict())
        self.session.add(rating)
        await self.session.commit()
        await self.session.refresh(rating)
        return rating

    async def get_course_ratings(self, course_id: int) -> List[Rating]:
        """Get all ratings for a course."""
        result = await self.session.execute(
            select(Rating).where(Rating.course_id == course_id)
        )
        return result.scalars().all()
```

4. **Create Route:**

```python
# backend/app/routes/ratings.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_session
from backend.app.schemas.rating import RatingCreate, RatingResponse
from backend.app.services.rating_service import RatingService

router = APIRouter()

@router.post("/ratings/", response_model=RatingResponse)
async def create_rating(
    data: RatingCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new course rating."""
    service = RatingService(session)
    rating = await service.create_rating(data)
    return RatingResponse.from_orm(rating)

@router.get("/courses/{course_id}/ratings", response_model=List[RatingResponse])
async def get_course_ratings(
    course_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get all ratings for a course."""
    service = RatingService(session)
    ratings = await service.get_course_ratings(course_id)
    return [RatingResponse.from_orm(r) for r in ratings]
```

5. **Register Router:**

```python
# backend/app/main.py
from backend.app.routes import courses, semesters, ratings

app.include_router(ratings.router, prefix="/api", tags=["ratings"])
```

6. **Write Tests:**

```python
# tests/test_routes/test_ratings.py
def test_create_rating(client):
    response = client.post("/api/ratings/", json={
        "course_id": 1,
        "user_id": 1,
        "rating": 4.5,
        "comment": "Great course!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 4.5

def test_get_course_ratings(client):
    response = client.get("/api/courses/1/ratings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Frontend Development

### Creating a New Component

1. **Define Component:**

```typescript
// components/rating/RatingCard.tsx
import React from 'react';

interface Rating {
  id: number;
  user_id: number;
  rating: number;
  comment?: string;
}

interface RatingCardProps {
  rating: Rating;
}

export const RatingCard: React.FC<RatingCardProps> = ({ rating }) => {
  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={i < rating ? 'text-yellow-400' : 'text-gray-300'}>
        ★
      </span>
    ));
  };

  return (
    <div className="border rounded-lg p-4 shadow-sm">
      <div className="flex items-center mb-2">
        <div className="flex">{renderStars(Math.floor(rating.rating))}</div>
        <span className="ml-2 text-sm text-gray-600">{rating.rating.toFixed(1)}</span>
      </div>
      {rating.comment && (
        <p className="text-gray-700 text-sm">{rating.comment}</p>
      )}
    </div>
  );
};
```

2. **Create Custom Hook:**

```typescript
// lib/hooks/useRatings.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

interface Rating {
  id: number;
  user_id: number;
  rating: number;
  comment?: string;
}

export const useRatings = (courseId: number) => {
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchRatings = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/courses/${courseId}/ratings`
        );
        setRatings(response.data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchRatings();
  }, [courseId]);

  return { ratings, loading, error };
};
```

3. **Use in Page:**

```typescript
// pages/course/[id].tsx
import { useRouter } from 'next/router';
import { RatingCard } from '@/components/rating/RatingCard';
import { useRatings } from '@/lib/hooks/useRatings';

export default function CoursePage() {
  const router = useRouter();
  const { id } = router.query;
  const { ratings, loading, error } = useRatings(Number(id));

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Course Ratings</h1>
      {ratings.map(rating => (
        <RatingCard key={rating.id} rating={rating} />
      ))}
    </div>
  );
}
```

4. **Write Tests:**

```typescript
// __tests__/components/rating/RatingCard.test.tsx
import { render, screen } from '@testing-library/react';
import { RatingCard } from '@/components/rating/RatingCard';

describe('RatingCard', () => {
  const mockRating = {
    id: 1,
    user_id: 1,
    rating: 4.5,
    comment: 'Great course!',
  };

  it('renders rating correctly', () => {
    render(<RatingCard rating={mockRating} />);

    expect(screen.getByText('4.5')).toBeInTheDocument();
    expect(screen.getByText('Great course!')).toBeInTheDocument();
  });

  it('renders stars correctly', () => {
    const { container } = render(<RatingCard rating={mockRating} />);
    const stars = container.querySelectorAll('.text-yellow-400');
    expect(stars).toHaveLength(4); // 4 filled stars for 4.5 rating
  });
});
```

## Contributing Guidelines

### How to Contribute

1. **Fork the Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Write Tests**
5. **Submit Pull Request**

### Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Follow code style guidelines
5. Write clear commit messages
6. Request review from maintainers

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on code quality
- Help others learn and grow

---

## Resources

**Documentation:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

**Tools:**
- [VSCode](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/)
- [DBeaver](https://dbeaver.io/)
- [GitHub Desktop](https://desktop.github.com/)

**Learning Resources:**
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React Hooks](https://react.dev/reference/react)
- [Testing Best Practices](https://testingjavascript.com/)

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
**Maintainers:** NYCU Platform Team
**License:** MIT
