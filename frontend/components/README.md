# NYCU Course Platform Components

This directory contains all reusable React components for the NYCU Course Platform frontend.

## Directory Structure

```
components/
├── common/          # Shared UI components
├── course/          # Course-related components
├── form/            # Form inputs and filters
├── schedule/        # Schedule display components
├── index.ts         # Central export file
└── README.md        # This file
```

## Component Categories

### Common Components

#### Header.tsx
Main navigation header with logo, menu, and search functionality.

**Features:**
- Logo/brand name (NYCU Course Platform)
- Navigation menu (Home, Schedule, About)
- Integrated search box
- Responsive mobile menu with hamburger icon
- Active route highlighting

**Usage:**
```tsx
import { Header } from '@/components';

<Header />
```

#### Footer.tsx
Site footer with copyright and links.

**Features:**
- Copyright notice
- Quick links (About, Contact, GitHub)
- Social media links
- Responsive design

**Usage:**
```tsx
import { Footer } from '@/components';

<Footer />
```

#### Loading.tsx
Loading state indicators with animations.

**Features:**
- Animated spinner
- Customizable message
- Full-screen overlay variant
- Inline loading variant
- Skeleton components

**Usage:**
```tsx
import { Loading, InlineLoading, SkeletonText } from '@/components';

// Basic loading
<Loading />

// With custom message
<Loading message="Loading courses..." />

// Full-screen overlay
<Loading message="Processing..." fullScreen />

// Inline variant
<InlineLoading message="Saving..." />

// Skeleton text
<SkeletonText lines={3} />
```

#### Error.tsx
Error display with retry functionality.

**Features:**
- Error icon with visual feedback
- Customizable error message
- Optional retry button
- Different variants (error, warning, info)
- Expandable details section

**Usage:**
```tsx
import { Error, InlineError } from '@/components';

// Basic error
<Error message="Failed to load courses" />

// With retry handler
<Error
  message="Failed to load data"
  onRetry={() => refetch()}
/>

// Warning variant
<Error
  message="Some data may be outdated"
  variant="warning"
/>

// Inline error
<InlineError message="Invalid input" />
```

### Course Components

#### CourseCard.tsx
Card component for displaying course information.

**Features:**
- Course name, number, teacher, credits
- Click handler for navigation
- Hover effects and animations
- Selection state
- Responsive design

**Usage:**
```tsx
import { CourseCard } from '@/components';

<CourseCard
  course={course}
  onClick={(id) => router.push(`/course/${id}`)}
  selected={selectedIds.includes(course.id)}
/>
```

#### CourseList.tsx
Container for displaying multiple course cards.

**Features:**
- Grid layout of CourseCard components
- Loading state with skeletons
- Empty state message
- Error state with retry
- Results summary

**Usage:**
```tsx
import { CourseList } from '@/components';

<CourseList
  courses={courses}
  loading={isLoading}
  error={error}
  onRetry={refetch}
  onCourseClick={(id) => router.push(`/course/${id}`)}
  selectedCourses={selectedIds}
/>
```

#### CourseDetail.tsx
Detailed view of a single course.

**Features:**
- All course fields displayed
- Parsed JSON details
- Back navigation button
- Share button
- Add to schedule button

**Usage:**
```tsx
import { CourseDetail } from '@/components';

<CourseDetail
  course={course}
  onBack={() => router.back()}
  onAddToSchedule={(course) => addToSchedule(course)}
/>
```

#### CourseSkeleton.tsx
Loading skeleton placeholders for courses.

**Features:**
- Animated shimmer effect
- Matches CourseCard layout
- Multiple skeleton cards
- Variants for different layouts

**Usage:**
```tsx
import { CourseSkeleton, CompactCourseSkeleton, ShimmerBox } from '@/components';

// Default skeleton
<CourseSkeleton count={6} />

// Compact variant
<CompactCourseSkeleton count={3} />

// Custom shimmer
<ShimmerBox height="h-8" width="w-3/4" />
```

### Form Components

#### SemesterSelect.tsx
Dropdown selector for academic semesters.

**Features:**
- List of available semesters
- Highlight selected semester
- Format display (e.g., "113 Fall")
- Clear functionality with badge
- Compact variant

**Usage:**
```tsx
import { SemesterSelect, CompactSemesterSelect } from '@/components';

// Standard select
<SemesterSelect
  semesters={semesters}
  value={selectedSemester}
  onChange={(semester) => setSelectedSemester(semester)}
  label="Academic Semester"
/>

// Compact variant
<CompactSemesterSelect
  semesters={semesters}
  value={selectedSemester}
  onChange={setSemester}
/>
```

#### SearchInput.tsx
Text input with debouncing for search functionality.

**Features:**
- Search icon
- Debounced onChange (300ms default)
- Clear button
- Loading indicator
- Keyboard shortcuts (Escape to clear)

**Usage:**
```tsx
import { SearchInput, CompactSearchInput } from '@/components';

// Standard input
<SearchInput
  value={query}
  onChange={(query) => setQuery(query)}
  placeholder="Search courses..."
  loading={isSearching}
/>

// Compact variant
<CompactSearchInput
  value={query}
  onChange={setQuery}
/>
```

#### DepartmentFilter.tsx
Dropdown filter for department selection.

**Features:**
- Alphabetically sorted departments
- "All Departments" option
- Selected department badge
- Multi-select variant
- Compact variant

**Usage:**
```tsx
import { DepartmentFilter, MultiDepartmentFilter } from '@/components';

// Single select
<DepartmentFilter
  departments={['CS', 'EE', 'MATH', 'PHYS']}
  value={selectedDept}
  onChange={(dept) => setSelectedDept(dept)}
  label="Department"
/>

// Multi-select variant
<MultiDepartmentFilter
  departments={departments}
  value={selectedDepts}
  onChange={(depts) => setSelectedDepts(depts)}
  label="Departments"
/>
```

### Schedule Components

#### ScheduleGrid.tsx
Weekly schedule grid display.

**Features:**
- 7 columns (Monday-Sunday)
- Time slots (8:00-22:00)
- Course placement by time
- Click handlers
- Mobile-responsive view
- Empty state

**Usage:**
```tsx
import { ScheduleGrid } from '@/components';

<ScheduleGrid
  courses={scheduledCourses}
  onCourseClick={(course) => viewCourse(course)}
  onRemoveCourse={(course) => removeCourse(course)}
/>
```

#### CourseSlot.tsx
Individual course slot in schedule.

**Features:**
- Color coding by course ID
- Course information display
- Remove button on hover
- Multiple size variants
- Click handler

**Usage:**
```tsx
import { CourseSlot, LargeCourseSlot, MinimalCourseSlot } from '@/components';

// Standard slot
<CourseSlot
  course={course}
  onClick={() => viewCourse(course)}
  onRemove={() => removeCourse(course)}
/>

// Large variant with more details
<LargeCourseSlot course={course} />

// Minimal variant
<MinimalCourseSlot course={course} />
```

#### ConflictWarning.tsx
Display schedule conflicts.

**Features:**
- Visual conflict indicators
- List of conflicting courses
- Resolution actions
- Conflict detection utility
- Badge and compact variants

**Usage:**
```tsx
import { ConflictWarning, ConflictBadge, detectConflicts } from '@/components';

// Detect conflicts
const conflicts = detectConflicts(courses);

// Display full warning
<ConflictWarning
  conflicts={conflicts}
  onResolve={(course) => removeCourse(course)}
/>

// Compact badge
<ConflictBadge
  count={conflicts.length}
  onClick={() => showConflicts()}
/>
```

## Styling

All components use Tailwind CSS for styling with:
- Responsive design (mobile-first)
- Consistent color scheme
- Hover and focus states
- Smooth transitions
- Accessibility features

## TypeScript

All components are fully typed with:
- Proper TypeScript interfaces
- JSDoc comments
- Type exports from `@/lib/types`

## Best Practices

1. **Import from index**: Use the central export file
   ```tsx
   import { Header, Footer, CourseList } from '@/components';
   ```

2. **Provide required props**: All components have clear prop interfaces
   ```tsx
   // ✅ Good
   <CourseCard course={course} onClick={handleClick} />

   // ❌ Missing required prop
   <CourseCard onClick={handleClick} />
   ```

3. **Handle loading states**: Use skeleton components during data fetching
   ```tsx
   {loading ? <CourseSkeleton count={6} /> : <CourseList courses={courses} />}
   ```

4. **Error handling**: Always provide error state and retry functionality
   ```tsx
   <CourseList
     courses={courses}
     loading={loading}
     error={error}
     onRetry={refetch}
   />
   ```

## Component Variants

Many components offer variants for different use cases:

- **Compact**: Smaller versions for inline use or tight spaces
- **Inline**: Minimal versions for use within other components
- **Large**: Expanded versions with more details
- **Minimal**: Bare-bones versions for dense displays

Choose the appropriate variant based on your layout needs.

## Accessibility

All interactive components include:
- Proper ARIA labels
- Keyboard navigation support
- Focus indicators
- Screen reader friendly markup

## Performance

Components are optimized with:
- React.memo where appropriate
- useCallback for event handlers
- useMemo for expensive computations
- Lazy loading support

## Contributing

When adding new components:
1. Place in appropriate category directory
2. Follow existing naming conventions
3. Include TypeScript types
4. Add comprehensive JSDoc comments
5. Export from `index.ts`
6. Update this README
