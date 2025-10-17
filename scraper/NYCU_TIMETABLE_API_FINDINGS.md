# NYCU Timetable API Investigation Results

## Summary
Successfully investigated the NYCU timetable website (https://timetable.nycu.edu.tw) using Playwright browser automation to understand how course data is loaded and structured.

## Key Findings

### 1. Main Course Data Endpoint

**Endpoint:** `https://timetable.nycu.edu.tw/?r=main/get_cos_list`

**Method:** POST

**Content-Type:** application/x-www-form-urlencoded

**Response Format:** JSON array

### 2. Request Parameters

Based on JavaScript analysis (`timetable.js`), the following parameters are sent:

```
m_acy         - Academic year (e.g., "114" for 2025-2026)
m_sem         - Semester (1=Fall, 2=Spring, 3=Summer)
m_acyend      - End academic year (for range queries)
m_semend      - End semester (for range queries)
m_dep_uid     - Department/College UID (e.g., "1601" for CS)
m_group       - Group filter ("**" for all)
m_grade       - Grade/Year filter ("**" for all)
m_class       - Class filter ("**" for all)
m_option      - Option filter ("**" for all)
m_crsname     - Course name search (empty string for all)
m_teaname     - Teacher name search (empty string for all)
m_cos_id      - Course ID filter (empty for all)
m_cos_code    - Course code filter (empty for all)
m_crstime     - Course time filter (empty for all)
m_crsoutline  - Course outline filter (empty for all)
m_costype     - Course type filter (empty for all)
m_selcampus   - Selected campus filter (empty for all)
```

### 3. Supporting AJAX Endpoints

The page makes multiple AJAX calls during initialization:

```
POST /?r=main/get_default_lang      - Get default language
POST /?r=main/getViewHtmlContents   - Get view HTML content
POST /?r=main/get_time_code         - Get time codes
POST /?r=main/get_acysem            - Get academic year/semester options
POST /?r=main/get_type              - Get course types
POST /?r=main/get_category          - Get categories
POST /?r=main/get_college           - Get colleges
POST /?r=main/get_dep               - Get departments
POST /?r=main/get_group             - Get groups
POST /?r=main/get_grade             - Get grades
POST /?r=main/get_class             - Get classes
POST /?r=main/getCouserTypeCampus   - Get course type campus
POST /?r=main/get_classroom_code    - Get classroom codes
POST /?r=main/get_cos_list          - **Main endpoint - Get course list**
```

### 4. Course Data Structure

From the browser page snapshot, courses are displayed in an HTML table with the following fields:

- **Semester** - Academic semester (e.g., "114 Fall Semester")
- **Course no** - Course number (e.g., "112500", "112504")
- **Permanent Course ID** - Permanent course identifier (e.g., "LSLS00003", "LSLS10027")
- **Summary** - Additional summary/notes
- **Course Name** - Full course name (e.g., "Career Development and Preparation Ⅰ", "Life Science Laboratory")
- **Size limits** - Enrollment limit (e.g., "Unlimited", "60")
- **Registered numbers** - Current enrollment count (e.g., "49", "62")
- **Class Time/Room** - Schedule and location (e.g., "W34-YL402[YM]", "R5678-YED109[YM]")
  - Format: `<Day><Time>-<Room>[<Campus>]`
  - Day codes: M=Monday, T=Tuesday, W=Wednesday, R=Thursday, F=Friday, S=Saturday, U=Sunday
  - Time codes: 1-9, a-d, n, y, z (see time code table)
  - Campus codes: YM=Yang-Ming, BA=Bo-Ai, GF=Guang-Fu, etc.
- **credit** - Credit hours (e.g., "1.00", "2.00", "4.00")
- **hours** - Contact hours (e.g., "2.00", "4.00")
- **Lecturers** - Instructor names (Chinese characters, comma-separated)
- **Type** - Course type (e.g., "Required", "Elective")
- **memo** - Additional notes/remarks (e.g., "導師時間，分組上課")

### 5. Example Course Record

```
Semester: 114 Fall Semester
Course no: 112504
Permanent Course ID: LSLS10027
Course Name: Life Science Laboratory
Size limits: Unlimited
Registered numbers: 62
Class Time/Room: R5678-YED109[YM]
credit: 2.00
hours: 4.00
Lecturers: 李曉暉、李勇陞、鄭浩民、陳儀聰
Type: Required
memo: 生科一、不分系一、醫學系B組合班上課
```

### 6. Time Code Reference

The system uses encoded time slots:

- **Early morning:** y (6:00-6:50), z (7:00-7:50)
- **Morning:** 1 (8:00-8:50), 2 (9:00-9:50), 3 (10:10-11:00), 4 (11:10-12:00)
- **Noon:** n (12:20-13:10)
- **Afternoon:** 5 (13:20-14:10), 6 (14:20-15:10), 7 (15:30-16:20), 8 (16:30-17:20), 9 (17:30-18:20)
- **Evening:** a (18:30-19:20), b (19:30-20:20), c (20:30-21:20), d (21:30-22:20)

### 7. Campus Codes

- **YM** - Yang-Ming Campus
- **BA** - Bo-Ai Campus
- **GF** - Guang-Fu Campus
- **BM** - Bei-Men Campus
- **GR** - Guei-Ren Campus (Tainan)
- **LJ** - Liu-Jia Campus
- **KS** - Kaohsiung Campus

### 8. Department/College Codes (Observed)

Based on the form options:

- **11** - School of Medicine (School Level)
- **12** - School of Dentistry
- **13** - School of Nursing
- **14** - School of Pharmaceutical Sciences
- **15** - School of Biomedical Science and Engineering
- **16** - College of Computer Science
- **17** - College Of Engineering
- **18** - College Of Science
- **19** - College Of Management
- etc.

### 9. Important Notes

1. **Data Format:** The endpoint returns data in JSON format, but it appears to be processed client-side and rendered as HTML tables
2. **Client-Side Rendering:** The actual course table HTML is generated via JavaScript using the `getViewHtmlContents` endpoint
3. **Bilingual Support:** The site supports both English and Chinese (zh-tw)
4. **Session/Cookies:** The requests appear to work without authentication, but may require session cookies
5. **Rate Limiting:** Unknown - should implement respectful scraping with delays

### 10. Network Request Flow

1. User loads page with query params (e.g., `?Acy=113&Sem=1`)
2. Page loads static resources (CSS, JS)
3. JavaScript makes multiple AJAX calls to populate dropdowns:
   - get_default_lang
   - get_acysem (semester options)
   - get_type (degree types)
   - get_college (college list)
   - get_dep (department list)
   - etc.
4. User selects filters and clicks "Search"
5. JavaScript calls `get_cos_list` with selected parameters
6. Response (JSON array) is stored in `Cos_Data_List` variable
7. JavaScript calls `getViewHtmlContents` to render the table

### 11. HTML vs JSON Response

The `get_cos_list` endpoint returns JSON, but the page uses another endpoint `getViewHtmlContents` to convert this data into HTML tables. For scraping purposes, we should:

**Option A:** Use the JSON endpoint directly (cleaner, structured data)
**Option B:** Parse the HTML tables (more fragile, but guaranteed to match what users see)

**Recommendation:** Use the JSON endpoint (`get_cos_list`) as it provides structured data that's easier to parse and validate.

## Next Steps for Scraper Implementation

1. **Test API Access:** Create a Python script using `requests` library to test the `get_cos_list` endpoint with various parameters
2. **Handle Parameters:** Build functions to generate proper parameter combinations for different departments/semesters
3. **Parse JSON Response:** Create data models (using Pydantic or dataclasses) to structure the course data
4. **Error Handling:** Implement retry logic and error handling for network issues
5. **Rate Limiting:** Add delays between requests to be respectful of the server
6. **Data Validation:** Validate the parsed data against expected schemas
7. **Storage:** Design database schema to store the course data efficiently
8. **Incremental Updates:** Implement logic to only fetch new/changed courses

## API Testing Example

```python
import requests

url = "https://timetable.nycu.edu.tw/"
params = {"r": "main/get_cos_list"}

data = {
    "m_acy": "114",          # Academic year 2025-2026
    "m_sem": "1",            # Fall semester
    "m_acyend": "114",
    "m_semend": "1",
    "m_dep_uid": "1601",     # CS department
    "m_group": "**",
    "m_grade": "**",
    "m_class": "**",
    "m_option": "**",
    "m_crsname": "",
    "m_teaname": "",
    "m_cos_id": "",
    "m_cos_code": "",
    "m_crstime": "",
    "m_crsoutline": "",
    "m_costype": "",
    "m_selcampus": ""
}

headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(url, params=params, data=data, headers=headers)
courses = response.json()
```

## Potential Challenges

1. **Department UIDs:** Need to map department names to their UIDs (may need to scrape the dropdown options first)
2. **Chinese Text:** Course names and instructor names are in Chinese - need proper Unicode handling
3. **Session Requirements:** Unknown if cookies/sessions are required for API access
4. **Data Completeness:** Some fields may be optional or vary between courses
5. **Schedule Changes:** Course data may change frequently during registration periods

## Conclusion

The NYCU timetable system uses a straightforward AJAX-based architecture with JSON responses. The main course data endpoint (`get_cos_list`) appears to be the primary target for scraping, returning structured JSON data that can be easily parsed and stored.
