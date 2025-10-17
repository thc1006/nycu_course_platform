# 🌍 Localization & Design Adjustment Plan
## Based on NYCU Data Structure, Format & Content Properties

**Date:** October 17, 2025
**Status:** 📋 Design Analysis & Planning
**Priority:** 🔴 Critical for User Experience

---

## 📊 Analysis: NYCU Data Structure vs Display Requirements

### 1. **Course Data Attributes (Backend Model)**

From `/backend/app/models/course.py`, our course data includes:

```
Core Fields:
├── crs_no (Course Number) - String, indexed
├── name (Course Name) - String
├── credits - Float/Optional
├── required - String ('Y'/'N' or '1'/'0')
├── teacher - String, optional
├── dept - Department code, optional
│
Schedule Encoding (Our Unique Challenge):
├── day_codes - String (numeric codes: '1'=Mon, '2'=Tue, etc.)
├── time_codes - String (alphanumeric: 'A'=7:00, 'B'=8:00, ... 'F'=17:00)
├── classroom_codes - String (multiple classrooms separated by commas)
│
Bilingual Content Fields (NEW):
├── syllabus - String (English course outline)
├── syllabus_zh - String (Traditional Chinese course outline)
│
Metadata:
├── semester_id - Foreign key to semesters table
├── acy (Academic Year) - Computed from semester (110-114)
├── sem (Semester) - Computed from semester (1 or 2)
└── details - JSON string with additional metadata
```

### 2. **Data Format Peculiarities**

**Challenge #1: Schedule Code Decoding**
- Raw format: `day_codes="135"` means Mon(1), Wed(3), Fri(5)
- Raw format: `time_codes="89A"` means 14:00(8), 15:00(9), 16:00(A)
- Expected display: "Mon/Wed/Fri 14:00-16:00" (readable)
- **Solution:** `scheduleParser.ts` utility converts codes to human-readable format

**Challenge #2: Bilingual Consistency**
- Chinese (zh-TW): Traditional Chinese (繁體中文)
- English (en-US): American English
- **Issue:** Not all course names are translated in source data
- **Solution:** Display original course name + optional Chinese when available

**Challenge #3: Required/Elective Status**
- Database stores as: 'Y'/'N' or '1'/'0'
- Display requirement: Badge with color coding (必修/選修)
- **Implementation:** Frontend parsing with conditional rendering

**Challenge #4: Semester Representation**
- Database: `acy` (110-114) + `sem` (1-2)
- Display format: "114-1", "114-2", "113-1" (user-friendly)
- **Current:** 9 semesters available in system

---

## 🎨 Localization Adjustments by Component

### **Component 1: HomePage (index.tsx) - NDHU-Inspired Landing**

**Current Status:** ✅ REDESIGNED to match NDHU

**Localization Adjustments:**
```
✅ DONE:
- Bilingual navigation (English/Chinese toggle)
- Semester selector with 9 options
- "Explore Courses" / "探索課程" headline
- Multi-language error messages

📋 NEEDED:
- i18n namespace: 'home'
- Keys to add:
  * hero_title (English: "Explore Courses", Chinese: "探索課程")
  * hero_subtitle (bilingual subtitle)
  * semester_label (bilingual "Semester"/"學期")
  * select_semester_cta (bilingual CTA text)
  * browse_cta (bilingual "Browse Courses")
  * empty_state_message (bilingual error message when no semester selected)
  * footer_tagline (bilingual footer text)
```

**File:** `/frontend/pages/index.tsx`
**Current Features:**
- Semester multi-select with dropdown (9 semesters: 110-1 to 114-1)
- Validation: Browse button disabled until semester selected
- Responsive design (mobile-first)
- Dark/light mode ready

---

### **Component 2: CourseCard (course/CourseCard.tsx)**

**Current Status:** ✅ ENHANCED with NDHU design + schedule parsing

**Data Format Handling:**
```typescript
Props Interface:
{
  course: {
    id: number
    crs_no: string              // "3101"
    name: string                // "Introduction to CS"
    teacher?: string            // "Dr. Smith"
    credits?: number            // 3.0
    dept?: string               // "CS"
    day_codes?: string          // "135" → Mon/Wed/Fri
    time_codes?: string         // "89A" → 14:00-16:00
    classroom_codes?: string    // "A101,B202"
    required?: string           // "Y"/"N" or "1"/"0"
    syllabus?: string           // English outline
    syllabus_zh?: string        // Chinese outline
  }
}
```

**Localization Features:**
```
✅ Already Implemented:
- Schedule parsing: `formatSchedule(day_codes, time_codes, classroom_codes, lang)`
  * English: "Mon/Wed/Fri 14:00-16:00 (A101, B202)"
  * Chinese: "一/三/五 14:00-16:00 (A101, B202)"
- Required/Elective badges (必修/選修 or Required/Elective)
- Bilingual UI text (Add to Schedule, Details, etc.)
- Syllabus indicator with bilingual label

✅ Translation Namespace: 'common'
- Keys: required, elective, credits, teacher, schedule, classroom

📋 FUTURE ENHANCEMENTS:
- Syllabus preview on hover/click
- Department name translation (CS → 資工系)
- Teacher name formatting for common names
```

**File:** `/frontend/components/course/CourseCard.tsx`
**Lines:** 1-190

---

### **Component 3: Browse Page (pages/browse.tsx)**

**Current Status:** ✅ VERIFIED production-ready

**Translation Requirements:**
```
Namespace: 'browse'

Current Keys (30+ translations):
- filters, semester, department, search
- courseCode, courseName, teacher, schedule
- addSchedule, courseDetails, required, elective
- sort, clearFilters, noResults
- day_monday through day_sunday (Mon/一, Tue/二, etc.)

Data Filtering Flow:
User selects semester(s) → API filters courses
  ├── semester_id matching
  ├── Optional: department filter
  ├── Optional: search by name/code
  └── Returns: Course[] with all fields

Display: CourseCard grid (1 col mobile, 2 cols tablet, 3 cols desktop)
```

**Files:**
- `/frontend/pages/browse.tsx`
- `/frontend/public/locales/zh-TW/browse.json` (43 lines)
- `/frontend/public/locales/en-US/browse.json` (43 lines)

---

### **Component 4: Schedule Parser Utility (utils/scheduleParser.ts)**

**Current Status:** ✅ COMPLETE 350+ lines

**Data Format Mapping:**

```typescript
// Day Codes Mapping:
1 → Monday (Mon / 一)
2 → Tuesday (Tue / 二)
3 → Wednesday (Wed / 三)
4 → Thursday (Thu / 四)
5 → Friday (Fri / 五)
6 → Saturday (Sat / 六)
7 → Sunday (Sun / 日)

// Time Codes Mapping (15 slots: 7:00-22:00):
1 → 07:00
2 → 08:00
3 → 09:00
4 → 10:00
5 → 11:00
6 → 12:00
7 → 13:00
8 → 14:00
9 → 15:00
A → 16:00
B → 17:00
C → 18:00
D → 19:00
E → 20:00
F → 21:00

// Example:
Input:  day_codes="135", time_codes="89A"
Output (EN): "Mon/Wed/Fri 14:00-16:00"
Output (ZH): "一/三/五 14:00-16:00"
```

**Classroom Codes:**
- Format: Comma-separated list (e.g., "A101,B202,C303")
- Display: "(A101, B202, C303)" at end of schedule

---

## 🔄 Translation Workflow & File Structure

### **Translation Namespace Organization:**

```
frontend/public/locales/
├── en-US/
│   ├── common.json      (Common UI text)
│   ├── home.json        (Homepage-specific)
│   ├── browse.json      (Browse page)
│   ├── course.json      (Course detail page)
│   ├── schedule.json    (My Schedule page)
│   └── error.json       (Error messages)
│
└── zh-TW/
    ├── common.json      (Common UI text - Traditional Chinese)
    ├── home.json        (Homepage-specific)
    ├── browse.json      (Browse page)
    ├── course.json      (Course detail page)
    ├── schedule.json    (My Schedule page)
    └── error.json       (Error messages)
```

### **Key Usage Pattern:**

```typescript
// In React Component:
const { t } = useTranslation(['common', 'browse']);
const lang = (router.locale || 'en') as 'en' | 'zh';

// Usage:
<span>{t('browse:required')}</span>  // Auto-detects lang from router.locale

// For programmatic use:
const label = lang === 'zh' ? '必修' : 'Required';
```

---

## 📋 Content Localization Checklist

### **Phase 1: Core UI Localization (CURRENT)**
- [x] Navigation bars (Browse Courses, My Schedule)
- [x] Homepage hero section (title, subtitle, CTA)
- [x] Semester selector UI
- [x] Course card UI labels
- [x] Day/time display (Mon/一, 14:00, etc.)
- [x] Badge labels (Required/必修, Elective/選修)
- [x] Button labels (Add to Schedule, View Details)
- [x] Empty state messages
- [x] Error messages

### **Phase 2: Pending Localizations**
- [ ] **Course Syllabus Content** - When scraper completes:
  - English syllabus from source (course_outline_scraper.py)
  - Chinese syllabus from source (course_outline_scraper.py)
  - Display in course detail page with toggle

- [ ] **Dynamic Content:**
  - Department names (CS → 資工系)
  - Building/location names (A Building → A棟)
  - Teacher name format preferences
  - Course codes with department prefixes

- [ ] **Search & Filter Labels:**
  - "Filter by Department" / "按系別篩選"
  - "Filter by Teacher" / "按講師篩選"
  - Sort options (by name, code, credits)

---

## 🚀 Implementation Priorities (Based on Data Format)

### **Priority 1: CRITICAL (Blocks Functionality)**
1. **Schedule Parsing Display** ✅ DONE
   - Converts day_codes + time_codes to readable format
   - Bilingual day names (Mon/一, etc.)

2. **Required/Elective Display** ✅ DONE
   - Database stores as Y/N or 1/0
   - Display as badges with color coding
   - Bilingual labels (Required/必修, Elective/選修)

3. **Semester Selector** ✅ DONE
   - Multi-select dropdown
   - Format: "114-1", "114-2", etc.
   - Navigation to /browse?semester=114-1&semester=114-2

### **Priority 2: HIGH (Enhances UX)**
1. **Classroom Display** (from classroom_codes)
   - Parse comma-separated building codes
   - Format: "(A101, B202)" at end of schedule

2. **Department Filter** (from dept field)
   - Populate unique departments from course data
   - Filter by selected department(s)

3. **Teacher Filter** (from teacher field)
   - Populate unique teachers from selected semesters
   - Filter by selected teacher(s)

### **Priority 3: MEDIUM (Polish & Details)**
1. **Syllabus Integration** (when scraper completes)
   - Display syllabus + syllabus_zh fields
   - Toggle between English/Chinese versions
   - Show "Has Outline" indicator in course card

2. **Search Functionality**
   - Search by course name (English + Chinese)
   - Search by course code
   - Search by teacher name

3. **Course Detail Page**
   - Full course information
   - Bilingual syllabus display
   - Enrollment status
   - Schedule conflict detection

---

## 🎯 Localization Best Practices for NYCU Data

### **1. Code Field Handling**
```
Rule: Never display raw codes to users
Examples:
- ❌ day_codes: "135"
- ✅ Schedule: "Mon/Wed/Fri"

- ❌ time_codes: "89A"
- ✅ Time: "14:00-16:00"

- ❌ classroom_codes: "A101,B202"
- ✅ Classroom: "(A101, B202)"
```

### **2. Bilingual Strategy**
```
Rule: Show content in selected language, fall back to source language if translation unavailable

Example (Course Name):
- If Chinese translation available: Show Chinese
- Else: Show English source
- Both visible on hover/expand

Implementation:
<span title={course.name}>
  {lang === 'zh' && course.name_zh ? course.name_zh : course.name}
</span>
```

### **3. Date/Time Localization**
```
Rule: Use locale-aware formatting

Schedule Display:
- EN: "Mon/Wed/Fri 14:00-16:00 (A101, B202)"
- ZH: "一/三/五 14:00-16:00 (A101, B202)"

Time Format:
- EN: 24-hour (14:00)
- ZH: 24-hour (14:00)
```

### **4. Numeric Display**
```
Credits:
- EN: "3 Credits" or "3 Cr"
- ZH: "3 學分"

Classroom Codes:
- Keep building names as-is (e.g., "A101", "B202")
- No translation needed for building codes
```

---

## 📈 Frontend Architecture for i18n

### **Language Detection & Routing**

```typescript
// Next.js i18next Configuration:
next-i18next.config.js
├── defaultLanguage: 'en'
├── languages: ['en', 'zh']
├── namespaces: ['common', 'home', 'browse', 'course', 'schedule', 'error']
└── detection: router-based locale

// URL Structure:
- /en/browse        (English browse page)
- /zh/browse        (Chinese browse page)
- /browse           (Default: en)

// Component Usage:
const lang = router.locale || 'en'
const { t } = useTranslation(namespace)
```

### **Bidirectional Text (RTL) Consideration**
- **Current:** Not needed (English + Chinese Traditional)
- **Future:** If Arabic/Hebrew support needed, update Tailwind config

---

## 💾 Database & API Localization

### **Backend API Response Format**

```json
{
  "id": 1,
  "crs_no": "3101",
  "name": "Introduction to Computer Science",
  "name_zh": "計算機科學導論",
  "teacher": "Dr. Smith",
  "credits": 3.0,
  "dept": "CS",
  "required": "Y",
  "day_codes": "135",
  "time_codes": "89A",
  "classroom_codes": "A101,B202",
  "syllabus": "This course introduces...",
  "syllabus_zh": "本課程介紹...",
  "acy": 114,
  "sem": 1
}
```

### **API Endpoint Localization**
```
GET /api/courses
  ?semester=114-1
  &lang=zh                    (Optional: backend includes both)
  &filter[dept]=CS
  &filter[teacher]=Smith
  &search=Introduction

Response includes both en/zh content - frontend selects based on router.locale
```

---

## 🔍 Verification Checklist

### **Before Production Deployment:**

- [ ] All 30+ translation keys present in both en-US and zh-TW
- [ ] Schedule parser correctly converts all 15 time slots (7:00-21:00)
- [ ] Day codes correctly map to bilingual names
- [ ] Required/Elective badges display correct colors and labels
- [ ] Classroom codes parse correctly with comma separation
- [ ] Bilingual UI renders without layout shift
- [ ] Dark mode properly applies to all translated text
- [ ] Mobile layout scales correctly for both languages
- [ ] Language switcher works across all pages
- [ ] Syllabus content displays without encoding issues

---

## 📚 Related Documentation

| File | Purpose | Status |
|------|---------|--------|
| `/frontend/utils/scheduleParser.ts` | Convert NYCU schedule codes | ✅ Complete |
| `/frontend/components/course/CourseCard.tsx` | Display individual course with bilingual support | ✅ Complete |
| `/frontend/pages/index.tsx` | NDHU-inspired landing page | ✅ Redesigned |
| `/frontend/pages/browse.tsx` | Course browsing with filters | ✅ Verified |
| `/frontend/public/locales/en-US/browse.json` | English browse translations | ✅ Created |
| `/frontend/public/locales/zh-TW/browse.json` | Chinese browse translations | ✅ Created |
| `/backend/app/models/course.py` | Database schema | ✅ Reference |
| `/scraper/course_outline_scraper.py` | Syllabus data collection | 🔄 Running |

---

## 🎓 Design Principles Summary

**Based on NYCU's unique data structure:**

1. **Code → Content Conversion**: Raw database codes (day_codes, time_codes) must be converted to user-friendly text via `scheduleParser`

2. **Bilingual Parity**: All UI text available in both English and Traditional Chinese with equal prominence

3. **Data-Driven Display**: Component displays adapt based on available data fields (optional fields handled gracefully)

4. **Mobile-First Responsive**: Content flows responsively from 1 column (mobile) to 3 columns (desktop)

5. **NDHU Aesthetic**: Minimalist design with clear hierarchy, focus on semester-first interaction model

6. **Accessibility**: All text visible and readable, schedule information concise but complete

---

**Last Updated:** October 17, 2025 10:50 UTC
**Next Phase:** Syllabus data import and bilingual display verification
