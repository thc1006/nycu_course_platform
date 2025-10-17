/**
 * Component Export Index
 *
 * Central export file for all NYCU Course Platform components.
 * Provides easy imports throughout the application.
 *
 * @example
 * ```tsx
 * // Import multiple components
 * import { Header, Footer, CourseList, Loading } from '@/components';
 *
 * // Or import from specific categories
 * import { CourseCard, CourseList } from '@/components/course';
 * ```
 */

// Common Components
export { default as Header } from './common/Header';
export { default as Footer } from './common/Footer';
export { default as Loading, InlineLoading, SkeletonText, SkeletonBox } from './common/Loading';
export { default as Error, InlineError, ErrorFallback } from './common/Error';

// Course Components
export { default as CourseCard } from './course/CourseCard';
export { default as CourseList, CompactCourseList } from './course/CourseList';
export { default as CourseDetail } from './course/CourseDetail';
export {
  default as CourseSkeleton,
  CompactCourseSkeleton,
  CourseDetailSkeleton,
  TableRowSkeleton,
  ShimmerBox,
  ImageSkeleton,
} from './course/CourseSkeleton';

// Form Components
export { default as SemesterSelect, CompactSemesterSelect } from './form/SemesterSelect';
export { default as SearchInput, CompactSearchInput } from './form/SearchInput';
export {
  default as DepartmentFilter,
  CompactDepartmentFilter,
  MultiDepartmentFilter,
} from './form/DepartmentFilter';

// Schedule Components
export { default as ScheduleGrid } from './schedule/ScheduleGrid';
export {
  default as CourseSlot,
  LargeCourseSlot,
  MinimalCourseSlot,
} from './schedule/CourseSlot';
export {
  default as ConflictWarning,
  ConflictBadge,
  NoConflictMessage,
  detectConflicts,
} from './schedule/ConflictWarning';
