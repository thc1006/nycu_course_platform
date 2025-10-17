/**
 * CourseSlot Component
 *
 * Displays a single course in a schedule time slot.
 * Features:
 * - Course name and number display
 * - Color coding for different courses
 * - Click handler
 * - Remove/edit button
 * - Hover effects
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <CourseSlot
 *   course={course}
 *   onClick={() => viewCourse(course)}
 *   onRemove={() => removeCourse(course)}
 * />
 * ```
 */

import React, { useCallback } from 'react';
import { Course } from '../../lib/types';

/**
 * Props for the CourseSlot component
 */
interface CourseSlotProps {
  /** Course to display in the slot */
  course: Course;
  /** Optional click handler for the slot */
  onClick?: () => void;
  /** Optional remove handler */
  onRemove?: () => void;
  /** Whether the slot is compact */
  compact?: boolean;
}

/**
 * Color palette for course slots
 */
const COLOR_PALETTE = [
  { bg: 'bg-blue-100', border: 'border-blue-400', text: 'text-blue-800', hover: 'hover:bg-blue-200' },
  { bg: 'bg-green-100', border: 'border-green-400', text: 'text-green-800', hover: 'hover:bg-green-200' },
  { bg: 'bg-purple-100', border: 'border-purple-400', text: 'text-purple-800', hover: 'hover:bg-purple-200' },
  { bg: 'bg-pink-100', border: 'border-pink-400', text: 'text-pink-800', hover: 'hover:bg-pink-200' },
  { bg: 'bg-yellow-100', border: 'border-yellow-400', text: 'text-yellow-800', hover: 'hover:bg-yellow-200' },
  { bg: 'bg-indigo-100', border: 'border-indigo-400', text: 'text-indigo-800', hover: 'hover:bg-indigo-200' },
  { bg: 'bg-red-100', border: 'border-red-400', text: 'text-red-800', hover: 'hover:bg-red-200' },
  { bg: 'bg-teal-100', border: 'border-teal-400', text: 'text-teal-800', hover: 'hover:bg-teal-200' },
  { bg: 'bg-orange-100', border: 'border-orange-400', text: 'text-orange-800', hover: 'hover:bg-orange-200' },
  { bg: 'bg-cyan-100', border: 'border-cyan-400', text: 'text-cyan-800', hover: 'hover:bg-cyan-200' },
];

/**
 * Get color scheme for a course based on its ID
 */
const getColorScheme = (courseId: number) => {
  const index = courseId % COLOR_PALETTE.length;
  return COLOR_PALETTE[index];
};

/**
 * Course slot component for schedule display
 *
 * @param {CourseSlotProps} props - Component props
 * @returns {JSX.Element} The rendered course slot
 */
const CourseSlot: React.FC<CourseSlotProps> = ({
  course,
  onClick,
  onRemove,
  compact = false,
}) => {
  const colors = getColorScheme(course.id);

  /**
   * Handle click event
   */
  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      // Don't trigger onClick if clicking the remove button
      if ((e.target as HTMLElement).closest('.remove-button')) {
        return;
      }
      onClick?.();
    },
    [onClick]
  );

  /**
   * Handle remove button click
   */
  const handleRemove = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onRemove?.();
    },
    [onRemove]
  );

  if (compact) {
    return (
      <div
        onClick={handleClick}
        className={`
          relative border-l-4 ${colors.border} ${colors.bg} px-2 py-1 rounded
          ${onClick ? 'cursor-pointer' : ''}
          transition-colors ${colors.hover}
        `}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <p className={`text-xs font-semibold truncate ${colors.text}`}>
              {course.name || 'Untitled'}
            </p>
          </div>
          {onRemove && (
            <button
              onClick={handleRemove}
              className="remove-button ml-1 p-0.5 hover:bg-red-100 rounded"
              aria-label="Remove course"
            >
              <svg className="w-3 h-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={handleClick}
      className={`
        relative border-l-4 ${colors.border} ${colors.bg} p-2 rounded shadow-sm
        ${onClick ? 'cursor-pointer' : ''}
        transition-all ${colors.hover}
        group
      `}
    >
      {/* Remove button */}
      {onRemove && (
        <button
          onClick={handleRemove}
          className="remove-button absolute top-1 right-1 p-1 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50"
          aria-label="Remove course"
        >
          <svg className="w-3 h-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      {/* Course info */}
      <div className="pr-6">
        <h4 className={`text-xs font-bold mb-0.5 line-clamp-2 ${colors.text}`}>
          {course.name || 'Untitled Course'}
        </h4>
        <p className={`text-xs ${colors.text} opacity-80`}>
          {course.crs_no}
        </p>
        {course.classroom && (
          <p className={`text-xs ${colors.text} opacity-70 mt-1`}>
            {course.classroom}
          </p>
        )}
      </div>
    </div>
  );
};

/**
 * Large variant for detailed schedule view
 */
export const LargeCourseSlot: React.FC<CourseSlotProps> = ({
  course,
  onClick,
  onRemove,
}) => {
  const colors = getColorScheme(course.id);

  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      if ((e.target as HTMLElement).closest('.remove-button')) {
        return;
      }
      onClick?.();
    },
    [onClick]
  );

  const handleRemove = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onRemove?.();
    },
    [onRemove]
  );

  return (
    <div
      onClick={handleClick}
      className={`
        relative border-2 ${colors.border} ${colors.bg} p-3 rounded-lg shadow-md
        ${onClick ? 'cursor-pointer' : ''}
        transition-all hover:shadow-lg ${colors.hover}
        group
      `}
    >
      {/* Remove button */}
      {onRemove && (
        <button
          onClick={handleRemove}
          className="remove-button absolute top-2 right-2 p-1.5 bg-white rounded-full shadow opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50"
          aria-label="Remove course"
        >
          <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      {/* Course details */}
      <div className="pr-8">
        <h3 className={`text-sm font-bold mb-1 ${colors.text}`}>
          {course.name || 'Untitled Course'}
        </h3>
        <div className={`space-y-1 text-xs ${colors.text} opacity-80`}>
          <p className="font-medium">{course.crs_no}</p>
          {course.teacher && <p>{course.teacher}</p>}
          {course.classroom && (
            <p className="flex items-center">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
              </svg>
              {course.classroom}
            </p>
          )}
          {course.time && (
            <p className="flex items-center">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {course.time}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Minimal slot for very compact displays
 */
export const MinimalCourseSlot: React.FC<CourseSlotProps> = ({ course }) => {
  const colors = getColorScheme(course.id);

  return (
    <div className={`h-full ${colors.bg} border-l-2 ${colors.border} px-1 py-0.5`}>
      <p className={`text-xs font-semibold truncate ${colors.text}`}>
        {course.crs_no}
      </p>
    </div>
  );
};

export default CourseSlot;
