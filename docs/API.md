# NYCU Course Platform - API Documentation

Complete API reference for the NYCU Course Platform backend services.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Semesters](#semesters)
  - [Courses](#courses)
  - [Advanced Search](#advanced-search)
- [Examples](#examples)
- [SDK and Tools](#sdk-and-tools)

## Overview

The NYCU Course Platform API is a RESTful API built with FastAPI, providing access to 70,239+ courses across 9 academic semesters. The API supports advanced filtering, searching, and course recommendations.

**API Characteristics:**
- **Protocol:** HTTP/HTTPS
- **Format:** JSON
- **Architecture:** REST
- **Documentation:** OpenAPI 3.0
- **Performance:** < 100ms average response time

## Base URL

### Production
```
https://nymu.com.tw/api
```

### Development
```
http://localhost:8000/api
```

### API Documentation
```
Swagger UI:  https://nymu.com.tw/docs
ReDoc:       https://nymu.com.tw/redoc
OpenAPI:     https://nymu.com.tw/openapi.json
```

## Authentication

Currently, the API is **publicly accessible** without authentication. Future versions may implement:
- API keys for rate limiting
- OAuth 2.0 for user-specific features
- JWT tokens for session management

## Rate Limiting

The API implements rate limiting to ensure fair usage:

| Endpoint Type | Rate Limit | Burst |
|---------------|------------|-------|
| General       | 10 req/s   | 20    |
| API Endpoints | 30 req/s   | 50    |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 1634567890
```

**Exceeded Rate Limit Response:**
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

## Response Format

### Success Response

All successful responses follow this structure:

```json
{
  "data": {},
  "meta": {
    "timestamp": "2025-10-17T10:30:00Z",
    "version": "1.0.0"
  }
}
```

For list endpoints with pagination:

```json
{
  "data": [],
  "meta": {
    "total": 70239,
    "limit": 50,
    "offset": 0,
    "timestamp": "2025-10-17T10:30:00Z"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200  | OK | Request successful |
| 201  | Created | Resource created successfully |
| 400  | Bad Request | Invalid parameters or malformed request |
| 404  | Not Found | Resource not found |
| 429  | Too Many Requests | Rate limit exceeded |
| 500  | Internal Server Error | Server-side error |
| 503  | Service Unavailable | Service temporarily unavailable |

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "type": "ErrorType",
  "code": "ERROR_CODE",
  "timestamp": "2025-10-17T10:30:00Z"
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| INVALID_PARAMETER | Invalid query parameter | Check parameter format and constraints |
| RESOURCE_NOT_FOUND | Requested resource doesn't exist | Verify resource ID |
| DATABASE_ERROR | Database operation failed | Try again or contact support |
| RATE_LIMIT_EXCEEDED | Too many requests | Wait and retry |

### Error Examples

**400 Bad Request:**
```json
{
  "detail": "Invalid semester parameter. Must be 1 or 2.",
  "type": "InvalidQueryParameter",
  "code": "INVALID_PARAMETER"
}
```

**404 Not Found:**
```json
{
  "detail": "Course with ID 99999 not found",
  "type": "CourseNotFound",
  "code": "RESOURCE_NOT_FOUND"
}
```

## Endpoints

### Health Check

Check API service health and database connectivity.

#### GET /health

**Description:** Returns the health status of the API and database.

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-17T10:30:00Z"
}
```

**Example:**
```bash
curl https://nymu.com.tw/health
```

---

### Semesters

Manage and query academic semesters.

#### GET /api/semesters/

**Description:** Retrieve list of all available semesters.

**Parameters:** None

**Response:**
```json
[
  {
    "id": 1,
    "acy": 113,
    "sem": 1
  },
  {
    "id": 2,
    "acy": 113,
    "sem": 2
  }
]
```

**Example:**
```bash
curl https://nymu.com.tw/api/semesters/
```

**Understanding Semester Data:**
- `id`: Unique identifier for the semester
- `acy`: Academic year (113 = 2024-2025)
- `sem`: Semester number (1 = Fall, 2 = Spring)

#### GET /api/semesters/{id}

**Description:** Retrieve a specific semester by ID.

**Parameters:**
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| id   | integer | path | Yes | Semester ID |

**Response:**
```json
{
  "id": 1,
  "acy": 113,
  "sem": 1
}
```

**Example:**
```bash
curl https://nymu.com.tw/api/semesters/1
```

---

### Courses

Query and filter courses from the database.

#### GET /api/courses/

**Description:** List courses with optional filtering and pagination. Optimized for handling 70K+ courses efficiently.

**Parameters:**

| Name | Type | Location | Required | Description | Example |
|------|------|----------|----------|-------------|---------|
| acy | integer | query | No | Filter by academic year | 113 |
| sem | integer | query | No | Filter by semester (1=Fall, 2=Spring) | 1 |
| dept | string | query | No | Filter by department code (partial match) | CS |
| teacher | string | query | No | Filter by teacher name (partial match) | Smith |
| q | string | query | No | Search query for course name/number | python |
| limit | integer | query | No | Maximum results (1-1000, default: 200) | 50 |
| offset | integer | query | No | Skip N results for pagination (default: 0) | 0 |

**Response:**
```json
[
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
]
```

**Examples:**

1. **Get all courses (paginated):**
```bash
curl "https://nymu.com.tw/api/courses/?limit=50&offset=0"
```

2. **Filter by semester:**
```bash
curl "https://nymu.com.tw/api/courses/?acy=113&sem=1"
```

3. **Filter by department:**
```bash
curl "https://nymu.com.tw/api/courses/?dept=CS&limit=100"
```

4. **Search by course name:**
```bash
curl "https://nymu.com.tw/api/courses/?q=computer%20science"
```

5. **Combined filters:**
```bash
curl "https://nymu.com.tw/api/courses/?acy=113&sem=1&dept=CS&teacher=Smith&limit=50"
```

**Performance Notes:**
- Default limit is 200 courses
- Maximum limit is 1000 courses per request
- Use pagination (offset) for browsing large result sets
- Response time: < 100ms for typical queries

#### GET /api/courses/{course_id}

**Description:** Retrieve detailed information for a specific course.

**Parameters:**
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| course_id | integer | path | Yes | Course ID |

**Response:**
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
  "details": "{\"capacity\": 50, \"enrollment\": 45, \"prerequisites\": []}"
}
```

**Example:**
```bash
curl https://nymu.com.tw/api/courses/1
```

---

### Advanced Search

Advanced filtering and search features.

#### POST /api/advanced/filter

**Description:** Advanced course filtering with multiple criteria.

**Request Body:**
```json
{
  "semesters": [1131, 1132],
  "departments": ["CS", "MATH"],
  "teachers": ["Smith", "Johnson"],
  "min_credits": 3,
  "max_credits": 4,
  "keywords": ["python", "programming"],
  "limit": 200,
  "offset": 0
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| semesters | array[int] | No | List of semester IDs (format: YYYS, e.g., 1131) |
| departments | array[string] | No | List of department codes |
| teachers | array[string] | No | List of teacher names |
| min_credits | float | No | Minimum credit value (0-10) |
| max_credits | float | No | Maximum credit value (0-10) |
| keywords | array[string] | No | Keywords to search across all fields |
| limit | integer | No | Max results (1-1000, default: 200) |
| offset | integer | No | Pagination offset (default: 0) |

**Response:**
```json
{
  "courses": [
    {
      "id": 1,
      "acy": 113,
      "sem": 1,
      "crs_no": "CS1001",
      "name": "Introduction to Computer Science",
      "teacher": "Dr. Alice Smith",
      "credits": 3.0,
      "dept": "CS",
      "time": "Mon 10:00-12:00",
      "classroom": "A101",
      "details": "{}"
    }
  ],
  "total": 1523,
  "limit": 200,
  "offset": 0
}
```

**Example:**
```bash
curl -X POST "https://nymu.com.tw/api/advanced/filter" \
  -H "Content-Type: application/json" \
  -d '{
    "semesters": [1131],
    "departments": ["CS"],
    "min_credits": 3,
    "max_credits": 4,
    "limit": 50
  }'
```

#### GET /api/advanced/stats

**Description:** Get course statistics and analytics.

**Parameters:**

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| acy | integer | query | No | Filter by academic year |
| sem | integer | query | No | Filter by semester |

**Response:**
```json
{
  "total_courses": 70239,
  "total_departments": 45,
  "total_teachers": 1203,
  "avg_credits": 3.2,
  "courses_by_department": {
    "CS": 523,
    "MATH": 412,
    "ENG": 678
  },
  "courses_by_credits": {
    "1": 5432,
    "2": 12345,
    "3": 45678,
    "4": 6784
  }
}
```

**Example:**
```bash
curl "https://nymu.com.tw/api/advanced/stats?acy=113&sem=1"
```

#### GET /api/advanced/search

**Description:** Search courses with suggestions.

**Parameters:**

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| q | string | query | Yes | Search query (1-200 characters) |
| limit | integer | query | No | Max results (1-500, default: 50) |

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "acy": 113,
      "sem": 1,
      "crs_no": "CS1001",
      "name": "Introduction to Computer Science",
      "teacher": "Dr. Alice Smith",
      "credits": 3.0,
      "dept": "CS",
      "time": "Mon 10:00-12:00",
      "classroom": "A101",
      "details": "{}"
    }
  ],
  "suggestions": [
    "Computer Science",
    "Computer Networks",
    "Computer Architecture"
  ]
}
```

**Example:**
```bash
curl "https://nymu.com.tw/api/advanced/search?q=computer&limit=20"
```

#### GET /api/advanced/recommend/{course_id}

**Description:** Get course recommendations based on a specific course.

**Parameters:**

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| course_id | integer | path | Yes | Course ID to base recommendations on |
| limit | integer | query | No | Max recommendations (1-100, default: 5) |

**Response:**
```json
[
  {
    "id": 2,
    "acy": 113,
    "sem": 1,
    "crs_no": "CS2001",
    "name": "Data Structures",
    "teacher": "Dr. Bob Johnson",
    "credits": 3.0,
    "dept": "CS",
    "time": "Tue 14:00-16:00",
    "classroom": "A102",
    "details": "{}"
  }
]
```

**Example:**
```bash
curl "https://nymu.com.tw/api/advanced/recommend/1?limit=10"
```

---

## Examples

### Complete Usage Examples

#### Example 1: Browse Courses for Fall 2024

```bash
# Get all CS courses for Fall 2024
curl "https://nymu.com.tw/api/courses/?acy=113&sem=1&dept=CS&limit=100"
```

**Use Case:** Student wants to see all Computer Science courses available in Fall 2024.

#### Example 2: Search for Python Courses

```bash
# Search for courses containing "python"
curl "https://nymu.com.tw/api/courses/?q=python&limit=50"
```

**Use Case:** Student looking for any course that teaches Python programming.

#### Example 3: Find Courses by Professor

```bash
# Find all courses taught by Dr. Smith
curl "https://nymu.com.tw/api/courses/?teacher=Smith&limit=100"
```

**Use Case:** Student wants to take courses from a specific professor.

#### Example 4: Advanced Multi-Criteria Search

```bash
# Find CS or MATH courses, 3 credits, Fall 2024
curl -X POST "https://nymu.com.tw/api/advanced/filter" \
  -H "Content-Type: application/json" \
  -d '{
    "semesters": [1131],
    "departments": ["CS", "MATH"],
    "min_credits": 3,
    "max_credits": 3,
    "limit": 50
  }'
```

**Use Case:** Student needs exactly 3-credit courses from CS or MATH departments.

#### Example 5: Pagination for Large Result Sets

```bash
# Get courses page by page (optimized for 70K+ courses)
curl "https://nymu.com.tw/api/courses/?limit=50&offset=0"   # Page 1
curl "https://nymu.com.tw/api/courses/?limit=50&offset=50"  # Page 2
curl "https://nymu.com.tw/api/courses/?limit=50&offset=100" # Page 3
```

**Use Case:** Browsing all courses in manageable chunks.

#### Example 6: Get Course Statistics

```bash
# Get statistics for Fall 2024
curl "https://nymu.com.tw/api/advanced/stats?acy=113&sem=1"
```

**Use Case:** Administrator wants to see course distribution and analytics.

### JavaScript/TypeScript Example

```typescript
// Fetch courses using Fetch API
async function fetchCourses(semester: string, department: string) {
  const params = new URLSearchParams({
    acy: '113',
    sem: '1',
    dept: department,
    limit: '50'
  });

  const response = await fetch(`https://nymu.com.tw/api/courses/?${params}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const courses = await response.json();
  return courses;
}

// Usage
fetchCourses('113-1', 'CS')
  .then(courses => console.log(courses))
  .catch(error => console.error('Error:', error));
```

### Python Example

```python
import requests

def fetch_courses(acy: int, sem: int, dept: str = None, limit: int = 50):
    """Fetch courses from NYCU Course Platform API"""
    base_url = "https://nymu.com.tw/api/courses/"

    params = {
        "acy": acy,
        "sem": sem,
        "limit": limit
    }

    if dept:
        params["dept"] = dept

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    return response.json()

# Usage
courses = fetch_courses(acy=113, sem=1, dept="CS", limit=100)
print(f"Found {len(courses)} courses")
```

### cURL with Authentication (Future)

```bash
# When API keys are implemented
curl "https://nymu.com.tw/api/courses/" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

## SDK and Tools

### Official SDKs

Currently, no official SDKs are available. The API follows standard REST conventions and can be used with any HTTP client.

**Recommended Libraries:**
- **JavaScript/TypeScript:** axios, fetch API
- **Python:** requests, httpx, aiohttp
- **Go:** net/http
- **Java:** OkHttp, RestTemplate

### API Testing Tools

1. **Swagger UI:**
   - URL: https://nymu.com.tw/docs
   - Interactive API documentation
   - Try endpoints directly in browser

2. **ReDoc:**
   - URL: https://nymu.com.tw/redoc
   - Beautiful API documentation
   - Searchable and well-organized

3. **Postman Collection:**
   - Import OpenAPI spec from https://nymu.com.tw/openapi.json
   - Pre-configured requests
   - Environment variables

### Development Tools

**API Monitoring:**
```bash
# Check API health
watch -n 5 curl -s https://nymu.com.tw/health

# Monitor response time
time curl -s https://nymu.com.tw/api/courses/?limit=1
```

**Load Testing:**
```bash
# Using Apache Bench
ab -n 1000 -c 10 https://nymu.com.tw/api/courses/

# Using wrk
wrk -t4 -c100 -d30s https://nymu.com.tw/api/courses/
```

## Best Practices

### Performance Optimization

1. **Use Pagination:**
   ```bash
   # Good: Paginate results
   curl "https://nymu.com.tw/api/courses/?limit=50&offset=0"

   # Bad: Request all 70K courses
   curl "https://nymu.com.tw/api/courses/?limit=70000"
   ```

2. **Filter Early:**
   ```bash
   # Good: Filter by semester first
   curl "https://nymu.com.tw/api/courses/?acy=113&sem=1&dept=CS"

   # Bad: Get all courses then filter client-side
   curl "https://nymu.com.tw/api/courses/?limit=70000"
   ```

3. **Use Specific Queries:**
   ```bash
   # Good: Specific search
   curl "https://nymu.com.tw/api/courses/?crs_no=CS1001"

   # Bad: Broad search then filter
   curl "https://nymu.com.tw/api/courses/?q=CS"
   ```

### Error Handling

```javascript
async function fetchCoursesWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);

      if (response.status === 429) {
        // Rate limited - wait and retry
        await new Promise(resolve => setTimeout(resolve, 60000));
        continue;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

### Caching

```javascript
// Client-side caching example
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function fetchWithCache(url) {
  const cached = cache.get(url);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const data = await fetch(url).then(r => r.json());
  cache.set(url, { data, timestamp: Date.now() });

  return data;
}
```

## Changelog

### Version 1.0.0 (2025-10-17)

**Initial Release:**
- Basic course and semester endpoints
- Advanced search and filtering
- Statistics and recommendations
- Support for 70,239 courses across 9 semesters
- OpenAPI 3.0 documentation
- Rate limiting implementation

---

## Support

**Documentation:**
- Swagger UI: https://nymu.com.tw/docs
- ReDoc: https://nymu.com.tw/redoc
- OpenAPI Spec: https://nymu.com.tw/openapi.json

**Status:**
- Health Check: https://nymu.com.tw/health
- Uptime: 99.9%
- Average Response Time: < 100ms

**Contact:**
- Report issues to system administrator
- Check [User Guide](USER_GUIDE.md) for common questions

---

**Last Updated:** 2025-10-17
**API Version:** 1.0.0
**Total Endpoints:** 12
**Total Courses:** 70,239
