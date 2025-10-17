# NYCU Course Platform - Architecture Documentation

Comprehensive system architecture and design documentation for the NYCU Course Platform.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagrams](#architecture-diagrams)
- [Component Design](#component-design)
- [Database Schema](#database-schema)
- [API Design](#api-design)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Scalability](#scalability)
- [Security Architecture](#security-architecture)
- [Design Decisions](#design-decisions)

## System Overview

### Platform Summary

The NYCU Course Platform is a full-stack web application designed to handle 70,000+ courses across 9 academic semesters with high performance and reliability.

**Key Metrics:**
- **Total Courses:** 70,239
- **Semesters:** 9 (110-1 through 114-1)
- **API Response Time:** < 100ms average
- **Uptime Target:** 99.9%
- **Concurrent Users:** Scalable architecture

**Technology Stack:**
```
Frontend:  Next.js 14 + React 18 + TypeScript + Tailwind CSS
Backend:   FastAPI + Python 3.10+ + SQLModel
Database:  SQLite (production), PostgreSQL (future)
Proxy:     Nginx with SSL/TLS
Hosting:   31.41.34.19 (nymu.com.tw)
```

### Design Philosophy

1. **Performance First:** Optimized for 70K+ course catalog
2. **User-Centric:** Intuitive interface for course browsing
3. **Scalable:** Architecture supports horizontal scaling
4. **Secure:** HTTPS, rate limiting, input validation
5. **Maintainable:** Clean code, comprehensive tests
6. **Developer-Friendly:** Clear APIs, good documentation

## Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Internet Users                        │
│                 https://nymu.com.tw                     │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS (Port 443)
                        │
                ┌───────▼──────────┐
                │   Cloudflare     │
                │   DNS + CDN      │
                │   DDoS Protection│
                └───────┬──────────┘
                        │
             ┌──────────▼──────────┐
             │    Load Balancer    │
             │   (Future: HAProxy) │
             └──────────┬──────────┘
                        │
        ┌───────────────▼───────────────┐
        │       Nginx Reverse Proxy     │
        │   - Port 80 (HTTP → HTTPS)    │
        │   - Port 443 (HTTPS)          │
        │   - 31 Worker Processes       │
        │   - Rate Limiting             │
        │   - SSL Termination           │
        │   - Static File Serving       │
        └───┬─────────────────────┬─────┘
            │                     │
    ┌───────▼────────┐    ┌──────▼──────────┐
    │   Frontend     │    │    Backend      │
    │   Next.js 14   │    │    FastAPI      │
    │   Port 3000    │    │    Port 8000    │
    │                │    │                 │
    │ - SSR/SSG      │    │ - REST API      │
    │ - React 18     │    │ - Uvicorn (4w)  │
    │ - Tailwind CSS │    │ - SQLModel ORM  │
    │ - TypeScript   │    │ - Async I/O     │
    └───────┬────────┘    └────────┬────────┘
            │                      │
            │         ┌────────────▼─────────┐
            │         │   SQLite Database    │
            │         │   - 70,239 courses   │
            │         │   - 9 semesters      │
            │         │   - Indexed tables   │
            │         │   - WAL mode         │
            └─────────┤   - File-based       │
                      └──────────────────────┘
```

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User Browser                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Homepage   │  │  Browse Page │  │ Schedule Page│  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
└─────────┼─────────────────┼──────────────────┼──────────┘
          │                 │                  │
          │ HTTP Request    │                  │
          │                 │                  │
     ┌────▼─────────────────▼──────────────────▼────┐
     │            Nginx (Reverse Proxy)             │
     │  ┌──────────────┐        ┌──────────────┐   │
     │  │   Route /    │        │  Route /api/ │   │
     │  │  → Frontend  │        │  → Backend   │   │
     │  └──────┬───────┘        └──────┬───────┘   │
     └─────────┼────────────────────────┼───────────┘
               │                        │
     ┌─────────▼────────┐     ┌────────▼──────────┐
     │  Next.js Server  │     │   FastAPI Server  │
     │                  │     │                   │
     │  ┌────────────┐  │     │  ┌─────────────┐ │
     │  │   Pages    │  │     │  │   Routes    │ │
     │  ├────────────┤  │     │  ├─────────────┤ │
     │  │ Components │  │     │  │  Services   │ │
     │  ├────────────┤  │     │  ├─────────────┤ │
     │  │   Hooks    │  │     │  │   Models    │ │
     │  └────────────┘  │     │  └─────┬───────┘ │
     └─────────┬────────┘     └────────┼─────────┘
               │                       │
               │  API Calls            │ SQL Queries
               │  (axios/fetch)        │
               │                       │
               └───────────┬───────────┘
                           │
                  ┌────────▼─────────┐
                  │ SQLite Database  │
                  │                  │
                  │  ┌────────────┐  │
                  │  │  semester  │  │
                  │  ├────────────┤  │
                  │  │   course   │  │
                  │  └────────────┘  │
                  └──────────────────┘
```

### Request Flow Diagram

```
User Action → Frontend → API Request → Backend → Database → Response

Example: Search for courses

1. User enters "Computer Science" in search box
   ↓
2. Frontend (pages/index.tsx)
   - Captures input change
   - Debounces input (300ms)
   - Updates React state
   ↓
3. Custom Hook (hooks/useCourses.ts)
   - Detects state change
   - Constructs API request
   - Sends HTTP GET request
   ↓
4. Nginx
   - Receives request on port 443
   - Applies rate limiting
   - Routes to backend (/api/courses/)
   ↓
5. Backend (routes/courses.py)
   - Validates query parameters
   - Calls CourseService
   ↓
6. Service Layer (services/course_service.py)
   - Implements business logic
   - Calls database layer
   ↓
7. Database Layer (database/course.py)
   - Constructs SQL query with indexes
   - Executes async query
   ↓
8. SQLite Database
   - Uses indexes for fast lookup
   - Returns matching courses
   ↓
9. Response flows back up the stack
   - Database → Service → Route → API Response
   ↓
10. Frontend receives JSON response
    - Updates state
    - Re-renders CourseList component
    - Displays results to user
```

## Component Design

### Backend Components

#### 1. API Layer (`routes/`)

**Responsibilities:**
- Handle HTTP requests/responses
- Validate input parameters
- Route requests to services
- Format responses
- Handle errors gracefully

**Pattern:** RESTful API design

```python
# routes/courses.py
@router.get("/courses/", response_model=list[CourseResponse])
async def list_courses(
    acy: Optional[int] = None,
    sem: Optional[int] = None,
    limit: int = 200,
    session: AsyncSession = Depends(get_session),
) -> list[CourseResponse]:
    """List courses with filtering."""
    service = CourseService(session)
    courses = await service.list_courses(acy=acy, sem=sem, limit=limit)
    return [CourseResponse.from_orm(c) for c in courses]
```

#### 2. Service Layer (`services/`)

**Responsibilities:**
- Implement business logic
- Coordinate between layers
- Apply business rules
- Handle complex operations

**Pattern:** Service pattern

```python
# services/course_service.py
class CourseService:
    """Business logic for course operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_courses(
        self,
        acy: Optional[int] = None,
        sem: Optional[int] = None,
        limit: int = 200,
    ) -> List[Course]:
        """List courses with optional filters."""
        query = select(Course)

        if acy:
            query = query.where(Course.acy == acy)
        if sem:
            query = query.where(Course.sem == sem)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
```

#### 3. Database Layer (`database/`)

**Responsibilities:**
- Execute database queries
- Manage connections
- Handle transactions
- Provide data access

**Pattern:** Repository pattern

```python
# database/course.py
async def get_courses_by_semester(
    session: AsyncSession,
    acy: int,
    sem: int,
) -> List[Course]:
    """Get all courses for a semester."""
    result = await session.execute(
        select(Course)
        .where(Course.acy == acy)
        .where(Course.sem == sem)
        .order_by(Course.crs_no)
    )
    return result.scalars().all()
```

#### 4. Model Layer (`models/`)

**Responsibilities:**
- Define data structures
- Map to database tables
- Provide type safety
- Validation

**Pattern:** ORM models

```python
# models/course.py
class Course(SQLModel, table=True):
    """Course database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    acy: int = Field(index=True)
    sem: int = Field(index=True)
    crs_no: str = Field(index=True)
    name: Optional[str] = None
    teacher: Optional[str] = None
    credits: Optional[float] = None
    dept: Optional[str] = Field(default=None, index=True)
    time: Optional[str] = None
    classroom: Optional[str] = None
    details: Optional[str] = None
```

### Frontend Components

#### 1. Pages (`pages/`)

**Responsibilities:**
- Define routes
- Fetch initial data (SSR/SSG)
- Compose page layouts
- Handle client-side routing

```typescript
// pages/index.tsx
export default function HomePage() {
  const { courses, loading } = useCourses();

  return (
    <MainLayout>
      <SearchInput />
      <CourseList courses={courses} loading={loading} />
    </MainLayout>
  );
}
```

#### 2. Components (`components/`)

**Responsibilities:**
- Reusable UI elements
- Encapsulated logic
- Props-based configuration
- Event handling

```typescript
// components/course/CourseCard.tsx
export const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onAddToSchedule,
}) => {
  return (
    <div className="course-card">
      <h3>{course.name}</h3>
      <p>{course.teacher}</p>
      <button onClick={() => onAddToSchedule(course.id)}>
        Add to Schedule
      </button>
    </div>
  );
};
```

#### 3. Custom Hooks (`lib/hooks/`)

**Responsibilities:**
- Data fetching
- State management
- Side effects
- Reusable logic

```typescript
// lib/hooks/useCourses.ts
export const useCourses = (filters: Filters) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses(filters).then(setCourses).finally(() => setLoading(false));
  }, [filters]);

  return { courses, loading };
};
```

## Database Schema

### Schema Design

**Philosophy:** Simple, normalized schema optimized for read-heavy workload.

### Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│           semester                  │
├─────────────────────────────────────┤
│ id          INTEGER PRIMARY KEY     │
│ acy         INTEGER NOT NULL        │
│ sem         INTEGER NOT NULL        │
└─────────────┬───────────────────────┘
              │
              │ 1:N relationship
              │
┌─────────────▼───────────────────────┐
│           course                    │
├─────────────────────────────────────┤
│ id          INTEGER PRIMARY KEY     │
│ acy         INTEGER NOT NULL (idx)  │
│ sem         INTEGER NOT NULL (idx)  │
│ crs_no      TEXT NOT NULL    (idx)  │
│ name        TEXT                    │
│ teacher     TEXT                    │
│ credits     REAL                    │
│ dept        TEXT             (idx)  │
│ time        TEXT                    │
│ classroom   TEXT                    │
│ details     TEXT (JSON)             │
└─────────────────────────────────────┘
```

### Table Definitions

#### Semester Table

```sql
CREATE TABLE semester (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acy INTEGER NOT NULL,
    sem INTEGER NOT NULL,
    UNIQUE(acy, sem)
);

CREATE INDEX idx_semester_acy ON semester(acy);
CREATE INDEX idx_semester_sem ON semester(sem);
```

**Purpose:** Store academic semester information.

**Columns:**
- `id`: Auto-incrementing primary key
- `acy`: Academic year (e.g., 113 for 2024-2025)
- `sem`: Semester number (1=Fall, 2=Spring)

**Sample Data:**
```sql
INSERT INTO semester (acy, sem) VALUES (113, 1); -- Fall 2024
INSERT INTO semester (acy, sem) VALUES (113, 2); -- Spring 2025
INSERT INTO semester (acy, sem) VALUES (114, 1); -- Fall 2025
```

#### Course Table

```sql
CREATE TABLE course (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acy INTEGER NOT NULL,
    sem INTEGER NOT NULL,
    crs_no TEXT NOT NULL,
    name TEXT,
    teacher TEXT,
    credits REAL,
    dept TEXT,
    time TEXT,
    classroom TEXT,
    details TEXT
);

-- Indexes for performance (70K+ courses)
CREATE INDEX idx_course_acy ON course(acy);
CREATE INDEX idx_course_sem ON course(sem);
CREATE INDEX idx_course_acy_sem ON course(acy, sem);
CREATE INDEX idx_course_dept ON course(dept);
CREATE INDEX idx_course_crs_no ON course(crs_no);
CREATE INDEX idx_course_teacher ON course(teacher);

-- Full-text search index (if needed)
CREATE VIRTUAL TABLE course_fts USING fts5(
    name, content=course, content_rowid=id
);
```

**Purpose:** Store course information.

**Columns:**
- `id`: Auto-incrementing primary key
- `acy`, `sem`: Semester reference (denormalized for performance)
- `crs_no`: Course number (e.g., "CS1001")
- `name`: Course name
- `teacher`: Instructor name(s)
- `credits`: Credit hours
- `dept`: Department code
- `time`: Schedule (e.g., "Mon 10:00-12:00")
- `classroom`: Room location
- `details`: JSON string with additional metadata

**Sample Data:**
```sql
INSERT INTO course (acy, sem, crs_no, name, teacher, credits, dept, time, classroom)
VALUES (113, 1, 'CS1001', 'Introduction to Computer Science', 'Dr. Smith', 3.0, 'CS', 'Mon 10:00-12:00', 'A101');
```

### Index Strategy

**Read-Heavy Optimization:**

1. **Single-column indexes:** `acy`, `sem`, `dept`, `crs_no`, `teacher`
2. **Composite indexes:** `(acy, sem)` for common semester queries
3. **Covering indexes:** Include frequently accessed columns

**Query Performance:**
- Semester filter: Uses `idx_course_acy_sem` → < 20ms
- Department filter: Uses `idx_course_dept` → < 30ms
- Combined filters: Uses multiple indexes → < 50ms
- Full table scan: Avoided with proper indexing

### Data Integrity

**Constraints:**
- Primary keys ensure uniqueness
- NOT NULL constraints on required fields
- Unique constraint on semester (acy, sem) combination

**Normalization:**
- Schema is in 3NF (Third Normal Form)
- Denormalized `acy`/`sem` in course table for performance
- Trade-off: Slight redundancy for query performance

## API Design

### RESTful Principles

The API follows REST conventions:

1. **Resource-Based URLs:** `/api/courses/`, `/api/semesters/`
2. **HTTP Methods:** GET for retrieval, POST for creation (future)
3. **Status Codes:** 200 OK, 400 Bad Request, 404 Not Found, 500 Error
4. **JSON Format:** All requests and responses use JSON
5. **Stateless:** No server-side session state

### API Endpoints

#### Semesters API

```
GET /api/semesters/
    → List all semesters
    Response: Array of semester objects

GET /api/semesters/{id}
    → Get specific semester
    Response: Single semester object
```

#### Courses API

```
GET /api/courses/
    Query Parameters:
        - acy: Filter by academic year
        - sem: Filter by semester
        - dept: Filter by department
        - teacher: Filter by teacher
        - q: Search query
        - limit: Results per page (default: 200, max: 1000)
        - offset: Pagination offset
    Response: Array of course objects

GET /api/courses/{id}
    → Get specific course
    Response: Single course object with full details
```

#### Advanced Search API

```
POST /api/advanced/filter
    Body: {
        semesters: [1131, 1132],
        departments: ["CS", "MATH"],
        min_credits: 3,
        max_credits: 4,
        keywords: ["python"],
        limit: 200,
        offset: 0
    }
    Response: {
        courses: [...],
        total: 1523,
        limit: 200,
        offset: 0
    }

GET /api/advanced/stats?acy=113&sem=1
    Response: {
        total_courses: 70239,
        total_departments: 45,
        courses_by_department: {...},
        courses_by_credits: {...}
    }

GET /api/advanced/search?q=computer&limit=50
    Response: {
        results: [...],
        suggestions: [...]
    }
```

### Response Format

**Success Response:**
```json
{
  "id": 1,
  "acy": 113,
  "sem": 1,
  "crs_no": "CS1001",
  "name": "Introduction to Computer Science",
  "teacher": "Dr. Alice Smith",
  "credits": 3.0,
  "dept": "CS",
  "time": "Mon 10:00-12:00, Wed 10:00-12:00",
  "classroom": "Engineering Building A101",
  "details": "{\"capacity\": 50, \"enrollment\": 45}"
}
```

**Error Response:**
```json
{
  "detail": "Invalid semester parameter. Must be 1 or 2.",
  "type": "InvalidQueryParameter",
  "code": "INVALID_PARAMETER"
}
```

### Rate Limiting

**Implementation:** Nginx rate limiting

```nginx
# General endpoints: 10 requests/second
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;

# API endpoints: 30 requests/second
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
```

**Behavior:**
- Requests within limit: Processed immediately
- Requests exceeding limit: Queued (burst)
- Burst exceeded: HTTP 429 Too Many Requests

## Frontend Architecture

### Component Hierarchy

```
App (_app.tsx)
├── Header
│   ├── Logo
│   ├── Navigation
│   ├── LanguageSwitcher
│   └── ThemeToggle
│
├── HomePage (index.tsx)
│   ├── HeroSection
│   ├── StatsSection
│   ├── FeaturesSection
│   ├── FeaturedCourses
│   │   └── CourseCard[]
│   └── CTASection
│
├── BrowsePage (browse.tsx)
│   ├── Header
│   ├── FilterPanel
│   │   ├── SemesterFilter
│   │   ├── DepartmentFilter
│   │   └── CreditRangeFilter
│   ├── SearchBar
│   ├── CourseGrid
│   │   └── CourseCard[]
│   └── Pagination
│
├── SchedulePage (schedule.tsx)
│   ├── ScheduleGrid
│   │   └── CourseSlot[]
│   ├── ScheduleSidebar
│   │   └── CourseList
│   └── ConflictWarning
│
└── Footer
    ├── Links
    ├── Copyright
    └── SocialMedia
```

### State Management

**Local State (useState):**
- Component-specific UI state
- Form inputs
- Temporary data

**Server State (SWR):**
- API data fetching
- Caching
- Revalidation

**Persistent State (LocalStorage):**
- User preferences (theme, language)
- Schedule data
- Filter settings

```typescript
// Example: Combined state management
export default function BrowsePage() {
  // Local state
  const [filters, setFilters] = useState<FilterState>({});

  // Server state (SWR)
  const { data: courses, error } = useSWR(
    `/api/courses?${queryString}`,
    fetcher
  );

  // Persistent state
  useEffect(() => {
    localStorage.setItem('filters', JSON.stringify(filters));
  }, [filters]);

  return <CourseGrid courses={courses} />;
}
```

### Routing Strategy

**Next.js File-based Routing:**

```
pages/
├── index.tsx           → /              (Home page)
├── browse.tsx          → /browse        (Course browsing)
├── schedule.tsx        → /schedule      (Schedule builder)
├── course/
│   └── [id].tsx        → /course/:id    (Course detail)
├── 404.tsx             → 404 errors
└── 500.tsx             → 500 errors
```

**Client-side Navigation:**
- Uses Next.js Link component
- Prefetching for faster navigation
- Smooth transitions

## Data Flow

### Course Search Flow

```
1. User Input
   ↓
[Search Component]
   - User types "Computer Science"
   - Debounce 300ms
   - Update state: searchQuery = "Computer Science"
   ↓
[useCourses Hook]
   - Detects searchQuery change
   - Constructs API URL with query params
   - Sends request: GET /api/courses/?q=Computer+Science
   ↓
[API Request (Frontend)]
   - axios.get() with query params
   - Includes headers, timeout
   ↓
[Nginx]
   - Receives HTTPS request
   - Applies rate limiting (30 req/s)
   - Routes to backend: proxy_pass backend:8000
   ↓
[FastAPI Backend]
   - Route handler: list_courses()
   - Validates query parameters
   - Calls CourseService
   ↓
[CourseService]
   - Applies business logic
   - Constructs database query
   - Calls database layer
   ↓
[Database Layer]
   - Builds SQLAlchemy query
   - Applies filters and indexes
   - Executes async query
   ↓
[SQLite Database]
   - Query: SELECT * FROM course WHERE name LIKE '%Computer Science%'
   - Uses full-text index
   - Returns matching rows
   ↓
[Response Flow (Backend)]
   - Database → Service → Route
   - Serialize to Pydantic models
   - Convert to JSON
   - Return HTTP 200 with data
   ↓
[Response Handling (Frontend)]
   - axios receives JSON response
   - useCourses hook updates state
   - React re-renders CourseList
   ↓
[UI Update]
   - CourseList maps over courses
   - Renders CourseCard for each
   - Display results to user
```

### Schedule Management Flow

```
[User Clicks "Add to Schedule"]
   ↓
[CourseCard Component]
   - onClick handler triggered
   - Calls onAddToSchedule(courseId)
   ↓
[Parent Component]
   - Receives courseId
   - Retrieves current schedule from LocalStorage
   - Checks for conflicts
   ↓
[Conflict Detection]
   - Parse course time
   - Compare with existing schedule
   - If conflict: Show warning
   - If no conflict: Continue
   ↓
[LocalStorage Update]
   - Load: localStorage.getItem('schedule')
   - Parse: JSON.parse(schedule)
   - Add: schedule.push(courseId)
   - Save: localStorage.setItem('schedule', JSON.stringify(schedule))
   ↓
[State Update]
   - setSchedule(newSchedule)
   - React re-renders ScheduleGrid
   ↓
[UI Feedback]
   - Show success notification
   - Update schedule view
   - Highlight new course
```

## Scalability

### Current Architecture (70K Courses)

**Vertical Scaling:**
- Single server handles all requests
- 31 Nginx workers
- 4 Uvicorn workers
- SQLite with optimized indexes

**Performance Metrics:**
- API response: < 100ms
- Search response: < 200ms
- Concurrent users: ~1000
- Database size: < 100MB

### Horizontal Scaling Strategy

**When to Scale:**
- Concurrent users > 5000
- API response > 500ms
- Database size > 1GB
- Complex queries slow down

**Scaling Plan:**

```
Phase 1: Database Migration (Current → PostgreSQL)
┌────────────────────────────────────────────────────┐
│  Load Balancer (HAProxy/Nginx)                    │
└────────┬──────────────────┬────────────────────────┘
         │                  │
    ┌────▼────┐        ┌────▼────┐
    │ Server 1│        │ Server 2│
    │Frontend │        │Frontend │
    │Backend  │        │Backend  │
    └────┬────┘        └────┬────┘
         │                  │
         └──────┬───────────┘
                │
        ┌───────▼────────┐
        │   PostgreSQL   │
        │   Primary DB   │
        └────────────────┘

Phase 2: Database Replication
┌────────────────────────────────────────────────────┐
│  Load Balancer                                     │
└────────┬──────────────────┬────────────────────────┘
         │                  │
    ┌────▼────┐        ┌────▼────┐
    │ Server 1│        │ Server 2│
    └────┬────┘        └────┬────┘
         │                  │
         └──────┬───────────┘
                │
        ┌───────▼────────┐
        │  PostgreSQL    │
        │  Primary (W)   │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │  PostgreSQL    │
        │  Replica (R)   │
        └────────────────┘

Phase 3: Microservices (If needed)
┌────────────────────────────────────────────────────┐
│  API Gateway                                       │
└───┬───────────┬───────────┬───────────┬────────────┘
    │           │           │           │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌──▼────┐
│Course │   │Search │   │Schedule│   │User   │
│Service│   │Service│   │Service │   │Service│
└───┬───┘   └───┬───┘   └───┬────┘   └──┬────┘
    │           │           │            │
    └───────────┴───────────┴────────────┘
                     │
            ┌────────▼────────┐
            │   PostgreSQL    │
            │   Cluster       │
            └─────────────────┘
```

### Caching Strategy

**Current: No caching (simple architecture)**

**Future Caching Layers:**

```
User Request
    ↓
[Browser Cache]
    - Static assets: 30 days
    - API responses: 5 minutes
    ↓
[CDN Cache (Cloudflare)]
    - Static files: Long TTL
    - API responses: Short TTL
    ↓
[Redis Cache]
    - Popular queries: 10 minutes
    - Course details: 1 hour
    - Semester list: 1 day
    ↓
[Database]
    - Final source of truth
```

### Load Balancing

**Future Load Balancer Configuration:**

```nginx
upstream backend {
    least_conn;  # Least connections algorithm
    server backend1:8000 weight=3;
    server backend2:8000 weight=3;
    server backend3:8000 weight=2 backup;
}

upstream frontend {
    ip_hash;  # Session affinity
    server frontend1:3000;
    server frontend2:3000;
}
```

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Network Security                          │
│  - Cloudflare DDoS Protection                       │
│  - Firewall (UFW): Ports 22, 80, 443               │
│  - Fail2ban: Brute force protection                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 2: Transport Security                        │
│  - TLS 1.2/1.3 (Let's Encrypt)                     │
│  - Strong cipher suites                             │
│  - HSTS headers                                     │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 3: Application Security                      │
│  - Rate Limiting (Nginx)                           │
│  - Input Validation (Pydantic)                     │
│  - SQL Injection Protection (ORM)                  │
│  - XSS Protection (React)                          │
│  - CSRF Protection (Future)                        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Layer 4: Data Security                             │
│  - Database file permissions                        │
│  - Backup encryption (Future)                      │
│  - Sensitive data hashing (Future)                 │
└─────────────────────────────────────────────────────┘
```

### Security Headers

```nginx
# Implemented in Nginx configuration
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Design Decisions

### Why SQLite (Not PostgreSQL)?

**Decision:** Use SQLite for initial production deployment.

**Reasoning:**
1. **Simplicity:** No separate database server needed
2. **Performance:** Fast for read-heavy workload (70K courses)
3. **Portability:** Single file, easy backups
4. **Cost:** Zero database server costs
5. **Reliability:** Proven stability for this scale

**Trade-offs:**
- Limited concurrent writes (not an issue for read-heavy app)
- No built-in replication (can be handled externally)
- Size limit theoretical (not reached at 70K courses)

**Migration Path:** PostgreSQL when:
- Concurrent writes become bottleneck
- Database size > 1GB
- Need advanced features (replication, partitioning)
- Horizontal scaling required

### Why Next.js (Not Create React App)?

**Decision:** Use Next.js for frontend.

**Reasoning:**
1. **Performance:** SSR/SSG for faster initial loads
2. **SEO:** Better search engine indexing
3. **Developer Experience:** File-based routing, API routes
4. **Production-Ready:** Built-in optimizations
5. **TypeScript:** First-class support

### Why FastAPI (Not Django/Flask)?

**Decision:** Use FastAPI for backend.

**Reasoning:**
1. **Performance:** Async/await for high concurrency
2. **Modern:** Python 3.10+ features, type hints
3. **API-First:** Built for RESTful APIs
4. **Documentation:** Auto-generated OpenAPI docs
5. **Validation:** Built-in with Pydantic

### Why Nginx (Not Built-in Servers)?

**Decision:** Use Nginx as reverse proxy.

**Reasoning:**
1. **Performance:** Highly optimized for static files
2. **Security:** SSL termination, rate limiting
3. **Load Balancing:** Ready for horizontal scaling
4. **Production-Grade:** Battle-tested reliability
5. **Flexibility:** Advanced configuration options

---

## Conclusion

The NYCU Course Platform architecture is designed for:
- **Current Scale:** 70,239 courses, moderate traffic
- **Performance:** < 100ms API response times
- **Reliability:** 99.9% uptime target
- **Maintainability:** Clean separation of concerns
- **Scalability:** Clear path to horizontal scaling

The architecture balances simplicity with production requirements, using proven technologies and patterns that can scale as the platform grows.

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
**Total Courses:** 70,239
**Architecture Status:** Production Ready
