# Phase 3: UI/UX Design Guide - Frontend Redesign
## NDHU-Inspired Modern Course Discovery Platform

**Date**: 2025-10-17
**Target**: NDHU-style (https://ndhu-course.dstw.dev/) educational platform
**Framework**: Next.js 14 + React + Tailwind CSS
**Design System**: shadcn/ui + Custom Components

---

## 1. Design Philosophy

### Core Principles
- **Simplicity**: Make course selection intuitive and enjoyable ("讓選課變得更簡單")
- **Accessibility**: Ensure all users can navigate effectively
- **Modern Aesthetics**: Clean, minimalist design with playful branding elements
- **Performance**: Fast load times and responsive interactions
- **Mobile-First**: Optimize for mobile before desktop

### Color Scheme
- **Light Mode**: Clean whites and grays with accent colors
  - Background: #FFFFFF or #F8F9FA
  - Text: #1F2937 (dark gray)
  - Accent: Blue (#3B82F6) or University brand color
  - Secondary: Slate variations for hierarchy

- **Dark Mode**: NDHU uses "dark:bg-slate-900/90" pattern
  - Background: #0F172A (slate-900 with opacity)
  - Text: #F1F5F9 (light gray)
  - Accent: Adjusted bright blue (#60A5FA)

---

## 2. Layout Architecture

### Header/Navigation
```
┌─────────────────────────────────────────┐
│  NYCU 課程平台 / NYCU Course Platform   │
│  [Browse] [My Schedule] [Dark Mode] [Lang] │
└─────────────────────────────────────────┘
```

**Components**:
- Platform logo/branding (left)
- Navigation links (center)
- Theme toggle (dark/light)
- Language selector (英文/中文)
- User profile (if auth enabled)

### Main Layout Structure

```
┌─────────────────────────────────────────────┐
│ Header / Navigation Bar                      │
├──────────────┬──────────────────────────────┤
│              │                              │
│  Filters     │  Main Content                │
│  Sidebar     │  (Course List / Detail)      │
│              │                              │
│  • Semester  │  Results:                    │
│  • Dept      │  [Course Cards in Grid]      │
│  • Teacher   │                              │
│  • Credits   │  [Pagination Controls]       │
│  • Keyword   │                              │
│              │                              │
└──────────────┴──────────────────────────────┘
│ Footer (Credits, Links)                      │
└─────────────────────────────────────────────┘
```

### Mobile Layout (Responsive)
```
On mobile (<768px):
- Filters move to collapsible drawer (hamburger menu)
- Course cards display in single column
- Sticky filter toggle at top
- Bottom sheet for advanced options
```

---

## 3. Key Components

### A. Semester Selector (Multi-Select)
**Pattern**: Multi-select dropdown or toggle buttons

**Design**:
```
┌─ Semesters ─────────────────┐
│ Select one or more:         │
│                             │
│ [✓ 110-1] [  110-2]        │
│ [✓ 111-1] [  111-2]        │
│ [  112-1] [  112-2]        │
│                             │
│ [Clear All] [Apply]        │
└─────────────────────────────┘
```

**Implementation**: Use shadcn/ui Checkbox components in a scrollable list

### B. Department/Category Filter
**Pattern**: Multi-select with grouping

**Design**:
```
┌─ Department ────────────────┐
│ ☐ All Departments          │
│                             │
│ ☐ Computer Science         │
│ ☐ Electrical Engineering   │
│ ☐ Mathematics              │
│ ☐ Physics                  │
│ ... (more options)         │
└─────────────────────────────┘
```

**Implementation**: Checkbox group or combobox with search

### C. Credits Range Slider
**Pattern**: Dual-input range slider

**Design**:
```
┌─ Credits ───────────────────┐
│ Range: 0 to 10             │
│ ├─ 0 ──●─────── 10        │
│                             │
│ Min: [  0 ] Max: [ 10 ]   │
└─────────────────────────────┘
```

**Implementation**: Radix UI Slider or react-range

### D. Search/Keyword Input
**Pattern**: Autocomplete with suggestions

**Design**:
```
┌──────────────────────────────┐
│ 🔍 Search courses...         │
│    (Type to search)          │
│                              │
│ Suggestions:                 │
│ • Data Science              │
│ • Web Development           │
│ • Machine Learning          │
└──────────────────────────────┘
```

**Implementation**: Combobox with debounced search, connect to /api/advanced/search

### E. Course Card
**Pattern**: Modern card with course details

**Design**:
```
┌────────────────────────────────┐
│ CS0290 - Computer Networks     │
│ ⭐ 4.2/5.0 (23 reviews)       │
│                                │
│ Prof. Frank Lin | 3 Credits    │
│ Fri 09:00-12:00 | EE201       │
│                                │
│ Full-stack networking course  │
│ covering TCP/IP and routing  │
│                                │
│ [Add to Schedule] [Details >>] │
└────────────────────────────────┘
```

**Information Hierarchy**:
1. Course Code + Name (large, bold)
2. Rating (stars) + Review count
3. Instructor name
4. Credits + Time + Location
5. Brief description
6. Action buttons

**Implementation**: Custom React component with Tailwind CSS

### F. Course Detail Modal/Page
**Pattern**: Expanded view with all course information

**Sections**:
- Course Header (title, code, rating)
- Basic Info (credits, instructor, time, location)
- Description
- Prerequisites (if available)
- Related Courses
- Schedule Conflict Check
- Add to Schedule Button

### G. Schedule Builder (Enhanced)
**Pattern**: Weekly calendar grid

**Design**:
```
┌─ My Schedule ──────────────────┐
│  Mon    Tue    Wed    Thu    Fri │
├────────────────────────────────┤
│  09-10 |      | CS   | CS   | EE │
│        |      | 01   | 02   | 01 │
│        |                         │
│  10-11 | MATH | MATH | ENG  | EE │
│        |  01  |  01  |  02  | 02 │
│                                  │
│ [Conflict detected: CS01 & EE01]│
│                                  │
│ [Export] [Share] [Add Course]  │
└────────────────────────────────┘
```

**Features**:
- Drag-and-drop course rearrangement
- Visual conflict highlighting (red background)
- Time conflict warnings
- Export options (iCal, Google Calendar, JSON)

---

## 4. Filter Display Strategy

### Strategy 1: Collapsible Sidebar (Desktop + Large Tablet)
- Always visible but can be collapsed
- Takes ~25% of screen width when expanded
- "Filters" button to toggle on mobile

### Strategy 2: Bottom Sheet (Mobile)
- Filters hidden by default
- Tap "Filter" button to open bottom sheet
- Apply/Clear buttons
- Show active filter count as badge

### Active Filter Display
```
Active Filters:
[Semester: 110-1 ✕] [Credits: 3-4 ✕] [Dept: CS ✕]
[Clear All]
```

---

## 5. Dark Mode Implementation

**Approach**: Use Next.js theme provider with Tailwind CSS

```typescript
// In tailwind.config.js
module.exports = {
  darkMode: 'class', // Use class strategy
  theme: {
    extend: {
      colors: {
        // Custom dark mode colors if needed
      }
    }
  }
}
```

**Color Mapping**:
- Light mode: Standard Tailwind colors
- Dark mode: Use `dark:` prefix in Tailwind

**Example**:
```html
<div class="bg-white dark:bg-slate-900">
  <p class="text-gray-900 dark:text-gray-100">Content</p>
</div>
```

**Theme Toggle**: Simple icon button in header
- Sun icon (☀️) when in dark mode
- Moon icon (🌙) when in light mode

---

## 6. Responsive Design Breakpoints

| Breakpoint | Width | Layout |
|-----------|-------|--------|
| Mobile | <640px | Single column, filter drawer |
| Tablet | 640px-1024px | Sidebar filter, 2-col course grid |
| Desktop | >1024px | Fixed sidebar, 3-4 col grid |

**Mobile Optimizations**:
- Touch-friendly button sizes (48px minimum)
- Swipe to navigate
- Bottom sheet for filters
- Vertical scrolling for course cards

---

## 7. Search & Autocomplete UX

**Flow**:
1. User types in search box
2. Debounce input (300ms)
3. Query `/api/advanced/search?q=<query>&limit=10`
4. Display suggestions with highlighting
5. Show full results on Enter or click suggestion

**Suggestions Display**:
```
Search Results for "programming"
─────────────────────────────
Courses:
• Introductory Programming (CS)
• Advanced Programming (CS)

Suggestions:
• Web Programming
• Competitive Programming
```

---

## 8. Component Libraries & Tools

### Primary Stack
- **shadcn/ui**: For base components (Button, Checkbox, Slider, etc.)
- **Radix UI**: Underlying headless components
- **React Hook Form**: Form state management
- **react-query**: Data fetching and caching
- **Framer Motion**: Smooth animations

### Installation
```bash
# shadcn/ui components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add slider
npx shadcn-ui@latest add combobox
npx shadcn-ui@latest add multi-select
```

---

## 9. Animation & Interactions

### Smooth Transitions
- Page transitions: 200-300ms fade
- Filter collapse/expand: 250ms ease
- Dark mode switch: 300ms transition
- Course card hover: Scale 1.02, shadow increase

### Loading States
- Skeleton screens for course cards
- Spinner for search results
- Progress indicator for schedule building

### Micro-interactions
- Hover effects on cards
- Ripple effect on buttons
- Input validation feedback (inline)
- Toast notifications for actions

---

## 10. Accessibility Standards

### WCAG 2.1 AA Compliance
- ✓ Color contrast ratio ≥ 4.5:1 for text
- ✓ Keyboard navigation support (Tab, Arrow keys)
- ✓ ARIA labels for all interactive elements
- ✓ Form validation with error messages
- ✓ Screen reader friendly

### Implementation
```html
<!-- Example: Semantic HTML + ARIA -->
<div role="region" aria-label="Course Filters">
  <button aria-expanded="false" aria-controls="filters">
    Show Filters
  </button>
  <div id="filters" aria-hidden="true">
    <!-- Filter content -->
  </div>
</div>
```

---

## 11. Performance Optimizations

### Image Optimization
- Lazy load course thumbnails
- WebP format with fallback
- Responsive images with srcset

### Code Splitting
- Separate bundles for filters, schedule builder, course details
- Dynamic imports for heavy components

### Caching Strategy
- Cache API responses in react-query
- LocalStorage for user preferences (theme, filters)
- Service Worker for offline support

### Lighthouse Targets
- Performance: >90
- Accessibility: >90
- Best Practices: >90
- SEO: >90

---

## 12. File Structure

```
frontend/
├── components/
│   ├── Course/
│   │   ├── CourseCard.tsx
│   │   ├── CourseDetail.tsx
│   │   └── CourseComparison.tsx
│   ├── Filters/
│   │   ├── FilterSidebar.tsx
│   │   ├── SemesterFilter.tsx
│   │   ├── DepartmentFilter.tsx
│   │   ├── CreditsFilter.tsx
│   │   └── SearchFilter.tsx
│   ├── Schedule/
│   │   ├── ScheduleBuilder.tsx
│   │   ├── ConflictDetection.tsx
│   │   └── ScheduleExport.tsx
│   ├── Common/
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   ├── ThemeToggle.tsx
│   │   └── LanguageSelector.tsx
│   └── Layout/
│       └── MainLayout.tsx
├── pages/
│   ├── index.tsx (Home/Browse)
│   ├── schedule.tsx (My Schedule)
│   ├── course/[id].tsx (Course Details)
│   └── search.tsx (Advanced Search)
├── styles/
│   └── globals.css
└── utils/
    ├── api.ts
    ├── hooks.ts
    └── filters.ts
```

---

## 13. Development Phases (Phase 3)

### Week 1: Foundation (Days 1-2)
- [ ] Set up component library (shadcn/ui)
- [ ] Create layout structure (Header, Sidebar, Main)
- [ ] Build basic course card component
- [ ] Implement theme toggle (dark/light mode)

### Week 2: Filters & Search (Days 3-4)
- [ ] Build advanced filter components
- [ ] Implement search with autocomplete
- [ ] Wire up to backend API
- [ ] Add filter state management

### Week 3: Features (Days 5-6)
- [ ] Schedule builder with drag-drop
- [ ] Conflict detection visualization
- [ ] Course detail modal/page
- [ ] Export functionality

### Week 4: Polish (Day 7-8)
- [ ] Animations and micro-interactions
- [ ] Mobile responsiveness testing
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Dark mode refinement

---

## 14. Success Metrics

### Design Quality
- ✓ Lighthouse score >90
- ✓ Mobile responsiveness on all devices
- ✓ WCAG 2.1 AA compliance
- ✓ <2.5s Time to Interactive

### User Experience
- ✓ <100ms API response times
- ✓ Smooth animations (60fps)
- ✓ Intuitive filtering workflow
- ✓ Clear visual hierarchy

### Technical
- ✓ TypeScript strict mode
- ✓ 80%+ component test coverage
- ✓ <50KB CSS bundle
- ✓ No console warnings/errors

---

## References & Resources

1. **NDHU Platform**: https://ndhu-course.dstw.dev/
2. **shadcn/ui Components**: https://ui.shadcn.com/
3. **Radix UI Primitives**: https://radix-ui.com/
4. **Tailwind CSS**: https://tailwindcss.com/
5. **UX Patterns for Discovery**: https://smart-interface-design-patterns.com/
6. **Accessibility**: https://www.w3.org/WAI/WCAG21/quickref/

---

**Status**: ✅ Design Guide Ready for Implementation
**Next**: Begin Phase 3 Frontend Development
