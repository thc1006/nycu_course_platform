# 📊 Reference Website Analysis & Platform Alignment Strategy

**Analysis Date:** 2025-10-17
**Reference Website:** https://ndhu-course.dstw.dev/
**Target Platform:** NYCU Course Platform
**Goal:** Align NYCU platform to match NDHU reference design and functionality

---

## 🎯 Executive Summary

The NDHU course platform (ndhu-course.dstw.dev) serves as an excellent reference design for student course exploration. It focuses on **simplicity, speed, and user-centric design**. Your NYCU platform should adopt similar principles while integrating course syllabus data.

### Key Takeaway
> "讓選課變得更簡單 · 讓學習變得更有趣🦐✨"
> (Make course selection simpler, learning more fun)

---

## 📐 Architecture Analysis

### NDHU Reference Platform
- **Framework:** Next.js + TypeScript
- **Styling:** Tailwind CSS
- **Language:** Traditional Chinese (zh-TW) primary
- **Database:** Modern course/schedule system
- **Key Features:**
  - Semester-based course browsing
  - Personal schedule building
  - Minimalist, responsive design
  - Light/Dark mode support

### Your NYCU Platform (Current State)
- ✅ **Framework:** Next.js 14 + TypeScript (MATCH)
- ✅ **Styling:** Tailwind CSS (MATCH)
- ✅ **Language:** zh-TW + en-US support (EXCEEDS - bilingual)
- ✅ **Database:** 70,239 courses ready
- ⏳ **Features:** Similar structure, needs UI/UX refinement

---

## 🎨 UI/UX Design Elements

### NDHU Reference Design

#### Color Palette
- **Primary:** Clean slate grays
- **Accent:** Rose/pink tones
- **Secondary:** White backgrounds
- **Dark Mode:** Inverted for accessibility

#### Typography
- **Logo:** "NDHU Course 東華查課拉" (friendly, modern)
- **Section Headers:** "探索課程" (Explore Courses)
- **Instructions:** Clear, task-oriented text
- **Hierarchy:** Bold titles, regular body text

#### Components
1. **Header:** Minimal navigation with branding
2. **Navigation:** Two main links
   - "瀏覽課表" (Browse Courses)
   - "我的課表" (My Schedule)
3. **Main Section:** Centered content area
4. **Semester Selector:** Multi-select dropdown/button group
5. **Footer:** Tagline + tech stack + copyright

#### Visual Elements
- Backdrop blur effects for depth
- Semi-transparent overlays
- Smooth transitions and animations
- Responsive grid layouts
- Clean spacing and alignment

### Your NYCU Platform (Needed Adjustments)

#### Current State
- ✅ Basic structure exists
- ✅ Next.js + Tailwind CSS ready
- ✅ Header component with language switcher
- ⏳ **Needs:** UI refinement to match NDHU's minimalist aesthetic

#### Recommended Adjustments

**1. Header Design**
```typescript
// Current: Language switcher with Globe icon (good)
// Needed:
// - Simplify header layout
// - Keep branding prominent: "NYCU Course Platform"
// - Place language switcher in cleaner position (top-right corner)
// - Reduce visual clutter
```

**2. Navigation Structure**
```
CURRENT:
├── Logo
├── Language Switcher (Globe icon + dropdown)
└── [Other elements]

RECOMMENDED (following NDHU):
├── Logo / Branding (left)
├── Navigation Links (center)
│  ├── 瀏覽課程 (Browse Courses)
│  └── 我的課表 (My Schedule)
└── Language Selector (right, minimal)
```

**3. Main Content Area**
```
RECOMMENDED LAYOUT:
┌─────────────────────────────────────┐
│       探索課程 (Explore Courses)     │
│  選擇學期，瀏覽課程，建立課表       │
│                                     │
│  ┌─ 學期選擇器 (Multi-select) ─┐   │
│  │ [113-1] [113-2] [114-1]  ... │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─ 課程列表 ──────────────────┐   │
│  │ [Course Cards/Table]         │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

**4. Course Display Format**
- **Option A:** Card-based layout (recommended)
  - Course code + name
  - Instructor
  - Time & location
  - Credits
  - Quick action buttons (Add to schedule, View details)

- **Option B:** Table layout
  - Compact, sortable columns
  - Better for large datasets

**5. Color Scheme**
```
Primary Colors:
- Background: #FFFFFF (light) / #0F172A (dark)
- Text: #1F2937 (dark mode) / #F9FAFB (light mode)
- Accent: #EC4899 (rose) or #8B5CF6 (purple)
- Borders: #E5E7EB (light) / #374151 (dark)

Recommend: Use rose (#EC4899) as accent for NYCU branding
```

**6. Typography**
```
Font Stack: Inter or Geist (match NDHU/modern style)

Hierarchy:
- Logo: 24px, bold, primary color
- Section Title: 28px, bold (e.g., "探索課程")
- Subsection: 16px, semibold
- Body: 14px, regular
- Small Text: 12px, regular, muted
```

---

## 🔄 Core Functionality Comparison

### NDHU Reference
1. **Browse Courses**
   - Select one or more semesters
   - View courses in list/grid
   - Filter by department/requirements
   - Search by course name/code

2. **Personal Schedule**
   - Add/remove courses from schedule
   - View schedule in timetable format
   - Time conflict detection
   - Export or share schedule

3. **Course Details**
   - Course info (code, name, credits, instructor)
   - Syllabus/outline (if available)
   - Schedule information
   - Prerequisites (if applicable)

### Your NYCU Platform

**Completed:**
- ✅ Course database (70,239 courses)
- ✅ Browse page structure
- ✅ Course detail component
- ✅ Schedule page
- ✅ Language switcher

**To Add (Priority Order):**
1. ⏳ **Course outline/syllabus display** (already implemented in CourseDetail.tsx, needs data population)
2. ⏳ **Semester selector** (multi-select)
3. ⏳ **Improved course display** (cards vs current format)
4. ⏳ **Search/filter enhancement**
5. ⏳ **Schedule management** (add/remove courses)

---

## 🚀 Implementation Roadmap

### Phase 1: UI/UX Refinement (2-3 hours)

**Priority 1:** Header & Navigation
- Refactor Header.tsx to match NDHU's clean design
- Position language switcher more elegantly
- Simplify navigation structure

**Priority 2:** Browse Page Layout
```typescript
// Key Components Needed:
1. HeroSection: Title + tagline
2. SemesterSelector: Multi-select component
3. CourseGrid/Table: Display courses
4. FilterSidebar: Category filters
5. SearchBar: Course search
```

**Priority 3:** Color & Typography
- Update Tailwind config with NDHU-inspired palette
- Apply consistent font sizes and weights
- Add smooth transitions

### Phase 2: Course Display Enhancement (2 hours)

**Components to Update:**
- `HomePage.tsx` - Hero section + tagline
- `BrowsePage.tsx` - Course list with cards
- `CourseDetail.tsx` - Syllabus display (already done!)
- Create `SemesterSelector.tsx` - Multi-select

### Phase 3: Data Population (1-2 hours)

**Complete course outline scraper:**
- Run `course_outline_scraper.py` to fetch all syllabus data
- Import data into `syllabus` and `syllabus_zh` fields
- Verify data integrity

### Phase 4: Polish & Testing (1-2 hours)

**Testing:**
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Language switching (all pages)
- ✅ Course display (card layouts, filters)
- ✅ Syllabus rendering (English & Chinese)
- ✅ Dark/Light mode toggle

---

## 📱 Responsive Design

### NDHU Reference Approach
- Mobile-first design
- Tailwind CSS responsive utilities
- Flexible layouts (grid/flex)
- Touch-friendly buttons and spacing

### Your Platform Adjustments
- ✅ Already uses Tailwind CSS
- ✅ Next.js responsive routing
- **Needed:** Explicit mobile optimizations
  - Larger touch targets (48px minimum)
  - Vertical layout for mobile
  - Simplified navigation drawer for mobile

---

## 🌙 Dark Mode Implementation

### NDHU Reference
- Light/Dark mode toggle
- Tailwind CSS `dark:` utilities
- Persistent user preference

### Your Platform Status
- ✅ Tailwind supports dark mode
- ✅ ThemeToggle.tsx component exists
- **Action:** Ensure all components use dark mode utilities

---

## 🔑 Key Implementation Details

### 1. Semester Selector Component
```typescript
// Location: frontend/components/SemesterSelector.tsx (create new)
// Feature: Multi-select for years 110-114
// Display: Button group or dropdown
// Returns: Selected semesters for course filtering
```

### 2. Enhanced Browse Page
```typescript
// Location: frontend/pages/browse.tsx
// Changes:
// - Add HeroSection with "探索課程" title
// - Add SemesterSelector
// - Filter course list by selected semesters
// - Display in card format (not just list)
// - Add search/filter sidebar
```

### 3. Course Card Component
```typescript
// Location: frontend/components/course/CourseCard.tsx (create new)
// Display:
// - Course code + name
// - Instructor
// - Time + location
// - Credits
// - "View Details" button
// - "Add to Schedule" button
```

### 4. Improved Course Detail Page
```typescript
// Location: frontend/components/course/CourseDetail.tsx (update existing)
// Already has:
// ✅ Syllabus display (both languages)
// Needed:
// - Better layout/formatting
// - Related courses section
// - Prerequisite information
```

---

## 🎯 Comparison Matrix

| Feature | NDHU Reference | Your NYCU Platform | Status |
|---------|---------------|--------------------|--------|
| Framework | Next.js + TS | Next.js 14 + TS | ✅ Match |
| Styling | Tailwind CSS | Tailwind CSS | ✅ Match |
| Language Support | zh-TW only | zh-TW + en-US | ✅ Exceed |
| Light/Dark Mode | Yes | Has component | ✅ Need polish |
| Course Database | ~3000+ | 70,239 (!) | ✅ Exceed |
| Syllabus Support | Limited | Planned | ⏳ In progress |
| Course Cards | Yes | Basic | ⏳ Need refinement |
| Semester Selector | Multi-select | Basic | ⏳ Need enhancement |
| Schedule Builder | Yes | Yes | ✅ Have it |
| Responsive Design | Mobile-first | Implemented | ✅ Maintain |
| Visual Polish | High | Medium | ⏳ Need work |
| Minimalist Design | Yes (goal) | Somewhat | ⏳ Simplify |

---

## 💡 Quick Wins (Easy Wins First)

### Can Do Immediately (30 minutes)
1. Add "東華查課拉"-style tagline to NYCU platform
2. Simplify header navigation
3. Update footer with tagline + tech stack
4. Apply consistent color scheme

### Can Do in 1-2 Hours
1. Create course card component
2. Update browse page layout
3. Add semester selector
4. Improve visual hierarchy

### Can Do in 2-4 Hours
1. Complete course outline scraper
2. Import syllabus data to database
3. Test bilingual display
4. Polish animations/transitions

---

## 📝 Recommended Action Plan

### Week 1: Foundation (This Week)
1. **Day 1:** Analyze and understand NDHU design
2. **Day 2:** Refactor UI components to match aesthetic
3. **Day 3:** Implement course card components
4. **Day 4:** Complete course outline scraping and import data

### Week 2: Enhancement
1. Add search and filtering
2. Improve schedule builder UI
3. Add more course information fields
4. Performance optimization

### Week 3: Polish & Launch
1. Comprehensive testing
2. Mobile responsiveness verification
3. Bug fixes and refinements
4. Production deployment

---

## 🔗 File References

### Frontend Components to Update
- `frontend/components/Header.tsx` - Navigation structure
- `frontend/pages/index.tsx` - Home/landing page
- `frontend/pages/browse.tsx` - Course browsing
- `frontend/components/course/CourseDetail.tsx` - Course details (✅ already enhanced)
- `frontend/public/locales/{locale}/*.json` - Translations (✅ already created)

### Backend Files to Update
- `backend/app/routers/courses.py` - API endpoints
- `backend/app/schemas/course.py` - Data schemas (✅ already updated)
- Database population scripts

### Scraper Files to Complete
- `scraper/course_outline_scraper.py` - Fetch all syllabi (⏳ in progress)
- `scraper/import_syllabus_to_database.py` - Import script (needed)

---

## 🎓 Success Criteria

Your platform will be successful when:

✅ **Design**
- [ ] Layout matches NDHU reference (minimalist, clean)
- [ ] Colors consistent throughout
- [ ] Typography hierarchy clear
- [ ] Responsive on all devices
- [ ] Dark mode fully functional

✅ **Functionality**
- [ ] Browse courses by semester
- [ ] Search/filter courses
- [ ] View course syllabus (English & Chinese)
- [ ] Add/remove courses from schedule
- [ ] Switch languages seamlessly

✅ **Data**
- [ ] All 70,239 courses loaded
- [ ] Syllabus data for all courses populated
- [ ] Both languages fully supported
- [ ] Schedule builder functional

✅ **Performance**
- [ ] Page load < 2 seconds
- [ ] Search response < 500ms
- [ ] Smooth animations and transitions

---

## 🚀 Next Steps

### Immediate Actions (Next 2 Hours)
1. **Review & approve** this analysis
2. **Start UI/UX refactoring** with Header and layout components
3. **Monitor course outline scraper** progress
4. **Create course card component** for browse page

### Then Continue With
1. Implement semester selector
2. Update browse page layout
3. Complete data population
4. End-to-end testing

---

**Report Generated:** 2025-10-17
**Analysis Depth:** Deep (UI/UX, Architecture, Components, Roadmap)
**Recommendation Level:** Comprehensive implementation plan ready

