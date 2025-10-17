/**
 * CourseList Component
 *
 * Container component for displaying a list of course cards.
 * Features:
 * - Renders array of CourseCard components
 * - Loading state with skeletons
 * - Empty state message
 * - Error state with retry functionality
 * - Responsive grid layout
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <CourseList
 *   courses={courses}
 *   loading={isLoading}
 *   error={error}
 *   onRetry={refetch}
 *   onCourseClick={(id) => router.push(`/course/${id}`)}
 * />
 * ```
 */

import React, { useCallback } from 'react';
import { Course } from '../../lib/types';
import CourseCard from './CourseCard';
import Loading from '../common/Loading';
import Error from '../common/Error';
import CourseSkeleton from './CourseSkeleton';

/**
 * Props for the CourseList component
 */
interface CourseListProps {
  /** Array of courses to display */
  courses: Course[];
  /** Whether the courses are currently loading */
  loading: boolean;
  /** Error object if loading failed */
  error?: Error | string | null;
  /** Optional callback when retry is triggered */
  onRetry?: () => void;
  /** Optional callback when a course card is clicked */
  onCourseClick?: (id: number) => void;
  /** Optional array of selected course IDs */
  selectedCourses?: number[];
  /** Optional custom empty state message */
  emptyMessage?: string;
}

/**
 * List container component for displaying courses
 *
 * @param {CourseListProps} props - Component props
 * @returns {JSX.Element} The rendered course list
 */
const CourseList: React.FC<CourseListProps> = ({
  courses,
  loading,
  error,
  onRetry,
  onCourseClick,
  selectedCourses = [],
  emptyMessage = 'No courses found',
}) => {
  /**
   * Check if a course is selected
   */
  const isCourseSelected = useCallback(
    (courseId: number): boolean => {
      return selectedCourses.includes(courseId);
    },
    [selectedCourses]
  );

  /**
   * Get error message from error object or string
   */
  const getErrorMessage = (): string => {
    if (!error) return '';
    if (typeof error === 'string') return error;
    return error.message || 'Failed to load courses';
  };

  // Loading state
  if (loading) {
    return (
      <div>
        <CourseSkeleton count={6} />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Error
          message={getErrorMessage()}
          onRetry={onRetry}
          variant="error"
        />
      </div>
    );
  }

  // Empty state
  if (!courses || courses.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <svg
          className="w-24 h-24 text-gray-300 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">
          {emptyMessage}
        </h3>
        <p className="text-gray-500 text-center max-w-md">
          Try adjusting your search filters or semester selection to find courses.
        </p>
      </div>
    );
  }

  // Course list
  return (
    <div>
      {/* Results summary */}
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing <span className="font-semibold">{courses.length}</span>{' '}
          {courses.length === 1 ? 'course' : 'courses'}
        </p>
        {selectedCourses.length > 0 && (
          <p className="text-sm text-blue-600 font-medium">
            {selectedCourses.length} selected
          </p>
        )}
      </div>

      {/* Course grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        {courses.map((course) => (
          <CourseCard
            key={course.id}
            course={course}
            onClick={onCourseClick}
            selected={isCourseSelected(course.id)}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * Compact variant of CourseList for smaller displays
 */
export const CompactCourseList: React.FC<CourseListProps> = (props) => {
  const { courses, loading, error, onRetry, onCourseClick } = props;

  if (loading) {
    return <Loading message="Loading courses..." />;
  }

  if (error) {
    const errorMessage = typeof error === 'string' ? error : error.message;
    return <Error message={errorMessage} onRetry={onRetry} />;
  }

  if (!courses || courses.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No courses found
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {courses.map((course) => (
        <div
          key={course.id}
          onClick={() => onCourseClick?.(course.id)}
          className="border rounded-lg p-4 hover:shadow-md transition cursor-pointer"
        >
          <h4 className="font-semibold text-gray-900 mb-1">
            {course.name || 'Untitled Course'}
          </h4>
          <p className="text-sm text-gray-600">
            {course.crs_no}
            {course.teacher && ` · ${course.teacher}`}
          </p>
        </div>
      ))}
    </div>
  );
};

export default CourseList;
