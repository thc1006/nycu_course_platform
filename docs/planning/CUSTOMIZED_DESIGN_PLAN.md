# 🎯 NYCU Platform - Customized Design Plan

**Adapting NDHU Reference Design to NYCU Data Structure**

Date: 2025-10-17
Status: Development Plan Ready

---

## 📊 Executive Summary

NYCU has **richer course data** than NDHU but stores schedule info as **codes** instead of readable format.

**Strategy:** Apply NDHU's minimalist, clean aesthetic while building UI components optimized for NYCU's specific data format.

---

## 🔍 Data Structure Analysis

### NYCU Course Data vs Standard Format

```
NYCU Database Fields:
├── Basic Info
│   ├── crs_no: "3101" (course number)
│   ├── name: "資料結構" (course name)
│   ├── credits: 3.0
│   └── required: "Y" or "N"
│
├── Instructor & Department
│   ├── teacher: "李明" (single or multiple names)
│   └── dept: "CS" (department code)
│
├── Schedule (CODED FORMAT - needs parsing)
│   ├── day_codes: "135" (1=Mon, 3=Wed, 5=Fri)
│   ├── time_codes: "89A" (8-9am, 9-10am, etc)
│   └── classroom_codes: "A101,B202" (room locations)
│
├── Documentation
│   ├── url: "https://timetable.nycu.edu.tw/..."
│   ├── syllabus: "Course outline in English"
│   └── syllabus_zh: "課程綱要（繁體中文）"
│
├── Metadata
│   ├── permanent_crs_no: "3101X" (course tracking)
│   ├── details: JSON string
│   └── semester_id: Foreign key to semesters
```

### Challenge: Schedule Code Parsing

NYCU stores schedule as **codes**, not readable format:

```
day_codes: "135"
time_codes: "89A"
classroom_codes: "A101,B202"

Meaning:
- Day: 1=Monday, 3=Wednesday, 5=Friday → "Mon/Wed/Fri"
- Time: 8=8-9am, 9=9-10am, A=10-11am → "8:00-11:00"
- Classroom: "A101,B202" → "A101, B202"

Display: Mon/Wed/Fri 8:00-11:00 (A101, B202)
```

---

## 🛠️ Solution: Helper Functions

### Create `utils/scheduleParser.ts`

```typescript
/**
 * Parse NYCU schedule codes to human-readable format
 */

// Time code mapping (traditional Taiwan university times)
const TIME_CODE_MAP: Record<string, string> = {
  '1': '7:00-8:00',
  '2': '8:00-9:00',
  '3': '9:00-10:00',
  '4': '10:00-11:00',
  '5': '11:00-12:00',
  '6': '12:00-13:00',
  '7': '13:00-14:00',
  '8': '14:00-15:00',
  '9': '15:00-16:00',
  'A': '16:00-17:00',
  'B': '17:00-18:00',
  'C': '18:00-19:00',
  'D': '19:00-20:00',
  'E': '20:00-21:00',
  'F': '21:00-22:00',
};

// Day code mapping
const DAY_CODE_MAP: Record<string, string> = {
  '1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu', '5': 'Fri',
  '6': 'Sat', '7': 'Sun',
};

const DAY_CODE_MAP_ZH: Record<string, string> = {
  '1': '一', '2': '二', '3': '三', '4': '四', '5': '五',
  '6': '六', '7': '日',
};

export function parseTimeRange(timeCodes: string): string {
  if (!timeCodes) return 'N/A';

  const codes = timeCodes.split('');
  if (codes.length === 0) return 'N/A';

  const firstCode = codes[0];
  const lastCode = codes[codes.length - 1];

  const startTime = TIME_CODE_MAP[firstCode]?.split('-')[0] || 'Unknown';
  const endTime = TIME_CODE_MAP[lastCode]?.split('-')[1] || 'Unknown';

  return `${startTime}-${endTime}`;
}

export function parseDays(dayCodes: string, lang: 'en' | 'zh' = 'en'): string {
  if (!dayCodes) return 'N/A';

  const days = dayCodes
    .split('')
    .map(d => lang === 'en' ? DAY_CODE_MAP[d] : DAY_CODE_MAP_ZH[d])
    .filter(Boolean);

  return days.length > 0 ? days.join('/' + (lang === 'en' ? '' : '')) : 'N/A';
}

export function formatSchedule(
  dayCodes: string,
  timeCodes: string,
  classrooms: string,
  lang: 'en' | 'zh' = 'en'
): string {
  const days = parseDays(dayCodes, lang);
  const timeRange = parseTimeRange(timeCodes);
  const rooms = classrooms || 'TBA';

  return `${days} ${timeRange} (${rooms})`;
}

// Example usage:
// formatSchedule('135', '89A', 'A101,B202', 'en')
// → "Mon/Wed/Fri 14:00-17:00 (A101,B202)"
```

---

## 🎨 Component Architecture - NDHU Style with NYCU Data

### Design Principles

**From NDHU Reference:**
- ✅ Minimalist layout (clean, uncluttered)
- ✅ Clear typography hierarchy
- ✅ Responsive design
- ✅ Light/Dark mode support
- ✅ Smooth transitions

**Applied to NYCU Data:**
- ✅ Parse and display schedule codes as readable times
- ✅ Show bilingual content (zh-TW + en-US)
- ✅ Display syllabus with formatted outline
- ✅ Filter by department, teacher, credits
- ✅ Search by course name/code

---

## 📐 Page Layout Structure

### Landing Page (採用 NDHU 風格)

```
┌─────────────────────────────────────────────┐
│  NYCU Course Platform  🎓    [🌐 EN / 中文] │  ← Header (clean, minimal)
├─────────────────────────────────────────────┤
│                                             │
│  🎓 探索課程                                │  ← Hero Section
│     選擇學期，瀏覽課程，規劃你的學習路徑    │
│                                             │
│  ┌─ 選擇學期 ──────────────────────────┐   │
│  │ [113-1]  [113-2]  [114-1]  [114-2] │   │  ← Multi-select semester
│  │ [More...]                          │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─ 篩選選項 ──────────────────────────┐   │
│  │ 系別: ▼ 選擇        │                │   │  ← Filters
│  │ 搜尋: [_________]    [🔍 搜尋]      │   │
│  │ 學分: [1-4]          [5+]           │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─ 課程列表 ──────────────────────────┐   │
│  │ [Course Card 1] [Course Card 2]    │   │  ← Course Grid/Cards
│  │ [Course Card 3] [Course Card 4]    │   │
│  │ ...                                │   │
│  └─────────────────────────────────────┘   │
│                                             │
├─────────────────────────────────────────────┤
│  © 2025 NYCU Course Platform                │  ← Footer (minimal)
│  Made with ❤️ by NYCU Students             │
└─────────────────────────────────────────────┘
```

### Course Card Component (NYCU Adapted)

```
┌─────────────────────────────────────┐
│  CS3101  資料結構 (Data Structures) │ ← Code + Name (bilingual)
├─────────────────────────────────────┤
│ 👨‍🏫 李明 (Dr. Lee)                 │ ← Teacher
│ 📚 3 學分 | 必修 (Required)        │ ← Credits + Status
│ 🏢 資訊工程系                       │ ← Department
│ ⏰ Mon/Wed/Fri 14:00-17:00        │ ← Formatted Schedule
│ 📍 A101, B202                      │ ← Classrooms
│                                     │
│ 📄 課程綱要: 包含完整大綱           │ ← Syllabus indicator
│                                     │
│ [加入課表] [查看詳情]              │ ← Actions
└─────────────────────────────────────┘
```

---

## 💻 Component Implementation Examples

### 1. Schedule Parser Utility

**File:** `frontend/utils/scheduleParser.ts`

```typescript
// [See above - Time/Day Code Mapping section]
```

### 2. Course Card Component

**File:** `frontend/components/course/CourseCard.tsx`

```typescript
import React from 'react';
import Link from 'next/link';
import { formatSchedule } from '@/utils/scheduleParser';

interface CourseCardProps {
  course: {
    id: number;
    crs_no: string;
    name: string;
    teacher?: string;
    credits?: number;
    dept?: string;
    day_codes?: string;
    time_codes?: string;
    classroom_codes?: string;
    required?: string;
    syllabus?: string;
    syllabus_zh?: string;
  };
  lang?: 'en' | 'zh';
}

export const CourseCard: React.FC<CourseCardProps> = ({ course, lang = 'zh' }) => {
  const schedule = formatSchedule(
    course.day_codes || '',
    course.time_codes || '',
    course.classroom_codes || '',
    lang === 'zh' ? 'zh' : 'en'
  );

  const hasSyllabus = course.syllabus || course.syllabus_zh;

  return (
    <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-lg transition-shadow bg-white dark:bg-gray-800">
      {/* Course Header */}
      <div className="mb-3">
        <div className="flex items-start justify-between gap-2 mb-1">
          <code className="text-sm font-bold text-blue-600 dark:text-blue-400">
            {course.crs_no}
          </code>
          {course.required && (
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              course.required === 'Y'
                ? 'bg-rose-100 dark:bg-rose-900 text-rose-700 dark:text-rose-200'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200'
            }`}>
              {course.required === 'Y' ? (lang === 'zh' ? '必修' : 'Required') : (lang === 'zh' ? '選修' : 'Elective')}
            </span>
          )}
        </div>
        <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 leading-tight">
          {course.name}
        </h3>
      </div>

      {/* Course Details */}
      <div className="space-y-2 mb-4 text-sm text-gray-700 dark:text-gray-300">
        {course.teacher && (
          <div className="flex items-center gap-2">
            <span>👨‍🏫</span>
            <span>{course.teacher}</span>
          </div>
        )}

        {course.credits && (
          <div className="flex items-center gap-2">
            <span>📚</span>
            <span>
              {course.credits} {lang === 'zh' ? '學分' : 'Credits'}
            </span>
          </div>
        )}

        {course.dept && (
          <div className="flex items-center gap-2">
            <span>🏢</span>
            <span>{course.dept}</span>
          </div>
        )}

        {course.day_codes && (
          <div className="flex items-center gap-2">
            <span>⏰</span>
            <span>{schedule}</span>
          </div>
        )}
      </div>

      {/* Syllabus Indicator */}
      {hasSyllabus && (
        <div className="mb-4 p-2 bg-blue-50 dark:bg-blue-900/30 rounded text-xs text-blue-700 dark:text-blue-300 flex items-center gap-2">
          <span>📄</span>
          <span>{lang === 'zh' ? '包含完整課程綱要' : 'Course outline available'}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded font-medium transition-colors">
          {lang === 'zh' ? '加入課表' : 'Add Schedule'}
        </button>

        <Link
          href={`/course/${course.id}`}
          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded font-medium transition-colors text-center"
        >
          {lang === 'zh' ? '查看詳情' : 'Details'}
        </Link>
      </div>
    </div>
  );
};
```

### 3. Browse Page with Filters

**File:** `frontend/pages/browse.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';
import { CourseCard } from '@/components/course/CourseCard';

export default function BrowsePage() {
  const router = useRouter();
  const { t } = useTranslation('browse'); // Needs i18n file
  const lang = router.locale as 'en' | 'zh';

  // State
  const [courses, setCourses] = useState([]);
  const [selectedSemesters, setSelectedSemesters] = useState<string[]>(['113-1']);
  const [selectedDept, setSelectedDept] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch courses
  const fetchCourses = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      selectedSemesters.forEach(sem => {
        const [acy, s] = sem.split('-');
        params.append('acy', acy);
        params.append('sem', s);
      });

      if (selectedDept) params.append('dept', selectedDept);
      if (searchQuery) params.append('q', searchQuery);
      params.append('limit', '200');

      const response = await fetch(`/api/courses?${params}`);
      const data = await response.json();
      setCourses(data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, [selectedSemesters, selectedDept, searchQuery]);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
            {t('title') || '探索課程'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t('subtitle') || '選擇學期，瀏覽課程，規劃你的學習路徑'}
          </p>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Filters Section */}
        <div className="mb-8 p-6 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('filters') || '篩選選項'}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Semester Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('semester') || '學期'}
              </label>
              <div className="space-y-2">
                {['113-1', '113-2', '114-1', '114-2'].map(sem => (
                  <label key={sem} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={selectedSemesters.includes(sem)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSemesters([...selectedSemesters, sem]);
                        } else {
                          setSelectedSemesters(selectedSemesters.filter(s => s !== sem));
                        }
                      }}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{sem}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Department Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('department') || '系別'}
              </label>
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">{t('allDepts') || '全部'}</option>
                <option value="CS">資訊工程</option>
                <option value="EE">電機工程</option>
                <option value="ME">機械工程</option>
              </select>
            </div>

            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('search') || '搜尋'}
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder={t('searchPlaceholder') || '課程名稱或代碼...'}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium transition-colors">
                  🔍
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin">⏳</div>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {t('loading') || '加載中...'}
            </p>
          </div>
        )}

        {/* Course Grid */}
        {!loading && (
          <>
            <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
              {courses.length} {t('coursesFound') || '門課程'}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {courses.map((course) => (
                <CourseCard key={course.id} course={course} lang={lang} />
              ))}
            </div>

            {courses.length === 0 && (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                {t('noCourses') || '沒有找到課程'}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export async function getStaticProps() {
  return {
    props: {
      ...(await serverSideTranslations('browse', ['browse', 'common'])),
    },
  };
}
```

---

## 📝 New i18n Files Needed

### `frontend/public/locales/zh-TW/browse.json`

```json
{
  "title": "探索課程",
  "subtitle": "選擇學期，瀏覽課程，規劃你的學習路徑",
  "filters": "篩選選項",
  "semester": "學期",
  "department": "系別",
  "allDepts": "全部",
  "search": "搜尋",
  "searchPlaceholder": "課程名稱或代碼...",
  "loading": "加載中...",
  "coursesFound": "門課程",
  "noCourses": "沒有找到課程",
  "addSchedule": "加入課表",
  "courseDetails": "查看詳情"
}
```

### `frontend/public/locales/en-US/browse.json`

```json
{
  "title": "Explore Courses",
  "subtitle": "Select a semester, browse courses, and plan your learning path",
  "filters": "Filter Options",
  "semester": "Semester",
  "department": "Department",
  "allDepts": "All",
  "search": "Search",
  "searchPlaceholder": "Course name or code...",
  "loading": "Loading...",
  "coursesFound": "courses found",
  "noCourses": "No courses found",
  "addSchedule": "Add to Schedule",
  "courseDetails": "View Details"
}
```

---

## 🎯 Implementation Priority

### Phase 1: Data Utilities (30 minutes)
1. ✅ Create `scheduleParser.ts` with time/day code mappings
2. ✅ Add helper functions for formatting

### Phase 2: Components (2-3 hours)
1. ✅ Create `CourseCard.tsx` component
2. ✅ Create `SemesterSelector.tsx` component
3. ✅ Update `BrowsePage.tsx` with filters
4. ✅ Add i18n browse translations

### Phase 3: Styling & Polish (1-2 hours)
1. ✅ Apply NDHU-style color scheme
2. ✅ Ensure dark mode support
3. ✅ Add responsive design
4. ✅ Add smooth animations

### Phase 4: Data Population (1-2 hours)
1. ✅ Complete course outline scraper
2. ✅ Import syllabus data to database
3. ✅ Verify data integrity

### Phase 5: Testing (1-2 hours)
1. ✅ Test all filters
2. ✅ Test language switching
3. ✅ Test responsive design
4. ✅ Test syllabus display

---

## 🎨 NDHU-Style Color Scheme (Customized for NYCU)

```css
/* Light Mode (Default) */
--primary: #3B82F6 (Blue) - for course cards, highlights
--accent: #EC4899 (Rose) - for actions, highlights, tags
--bg-main: #FFFFFF (White)
--bg-secondary: #F9FAFB (Light Gray)
--text-primary: #1F2937 (Dark Gray)
--text-secondary: #6B7280 (Medium Gray)
--border: #E5E7EB (Light Gray)

/* Dark Mode */
--primary: #60A5FA (Light Blue)
--accent: #F472B6 (Light Rose)
--bg-main: #0F172A (Dark Gray-Blue)
--bg-secondary: #1E293B (Dark Gray)
--text-primary: #F1F5F9 (Light Gray)
--text-secondary: #CBD5E1 (Medium Gray)
--border: #334155 (Dark Gray)
```

---

## 📊 Data Flow Architecture

```
User Interaction
    ↓
Browse Page (with semester/dept/search filters)
    ↓
API Call: /api/courses?acy=113&sem=1&dept=CS&q=...
    ↓
Backend (FastAPI)
    - Query database
    - Filter by semester, department, search query
    - Return 200 courses max
    ↓
Course Array
    ↓
Map to CourseCard Components
    ↓
Course Card
    - Parse day_codes → "Mon/Wed/Fri"
    - Parse time_codes → "14:00-17:00"
    - Display: Mon/Wed/Fri 14:00-17:00 (A101,B202)
    - Show: Code, Name, Teacher, Credits, Dept
    - Show: Required/Elective status
    - Show: Syllabus indicator
    ↓
User Actions
    - Add to Schedule
    - View Details (→ CourseDetail page with full syllabus)
```

---

## 🚀 Customization Summary

### What We're Borrowing from NDHU
✅ Minimalist, clean aesthetic
✅ Light/Dark mode support
✅ Clear typography hierarchy
✅ Responsive grid layout
✅ Smooth animations

### What We're Customizing for NYCU
✅ Schedule code parsing (day/time codes)
✅ Bilingual content (zh-TW + en-US)
✅ Additional data fields (credits, dept, syllabus)
✅ Richer filtering options
✅ Full syllabus display

### Data Source Optimization
✅ NYCU has 70,239 courses (vs NDHU's ~3000)
✅ NYCU has explicit syllabus fields (bonus!)
✅ NYCU has bilingual support from scraper
✅ NYCU has richer course metadata (dept, credits, etc)

---

## ✨ Next Steps

### Immediate (Next 2 Hours)
1. Create `frontend/utils/scheduleParser.ts`
2. Create `frontend/components/course/CourseCard.tsx`
3. Create `frontend/public/locales/*/browse.json`
4. Update `frontend/pages/browse.tsx`

### Short Term (Next 4 Hours)
1. Complete course outline scraper
2. Import syllabus data to database
3. Test all language switching
4. Polish animations and styling

### Medium Term (Next 8 Hours)
1. Add search/filter backend endpoints
2. Implement department selector
3. Add schedule builder UI
4. Comprehensive end-to-end testing

---

**Report Generated:** 2025-10-17
**Status:** Ready for Implementation
**Data Optimization:** NYCU-specific adaptations applied
**Design Reference:** NDHU aesthetic (customized for NYCU data)

