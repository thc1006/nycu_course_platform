/**
 * CourseCard Component
 *
 * Displays a single course in card format.
 * Features:
 * - Course name, number, teacher, credits
 * - Click handler for navigation
 * - Hover effects and animations
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <CourseCard
 *   course={course}
 *   onClick={(id) => router.push(`/course/${id}`)}
 * />
 * ```
 */

import React, { useCallback } from 'react';
import { Course } from '../../lib/types';

/**
 * Props for the CourseCard component
 */
interface CourseCardProps {
  /** Course data to display */
  course: Course;
  /** Optional click handler called when card is clicked */
  onClick?: (id: number) => void;
  /** Whether the card is currently selected */
  selected?: boolean;
}

/**
 * Card component for displaying course information
 *
 * @param {CourseCardProps} props - Component props
 * @returns {JSX.Element} The rendered course card
 */
const CourseCard: React.FC<CourseCardProps> = ({ course, onClick, selected = false }) => {
  /**
   * Handle card click event
   */
  const handleClick = useCallback(() => {
    if (onClick) {
      onClick(course.id);
    }
  }, [onClick, course.id]);

  /**
   * Handle keyboard interaction for accessibility
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleClick();
      }
    },
    [handleClick]
  );

  return (
    <div
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      className={`
        relative border-2 rounded-lg p-5 shadow-sm transition-all duration-200
        ${onClick ? 'cursor-pointer hover:shadow-lg hover:border-blue-300 hover:-translate-y-1' : ''}
        ${selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'}
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
      `}
    >
      {/* Selected indicator */}
      {selected && (
        <div className="absolute top-3 right-3">
          <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      )}

      {/* Course Header */}
      <div className="mb-3">
        <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">
          {course.name || 'Untitled Course'}
        </h3>
        <p className="text-sm font-medium text-blue-600">{course.crs_no}</p>
      </div>

      {/* Course Details */}
      <div className="space-y-2">
        {/* Teacher */}
        {course.teacher && (
          <div className="flex items-center text-sm text-gray-700">
            <svg className="w-4 h-4 mr-2 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <span className="truncate">{course.teacher}</span>
          </div>
        )}

        {/* Credits */}
        {course.credits !== null && course.credits !== undefined && (
          <div className="flex items-center text-sm text-gray-700">
            <svg className="w-4 h-4 mr-2 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>{course.credits} Credits</span>
          </div>
        )}

        {/* Department */}
        {course.dept && (
          <div className="flex items-center text-sm text-gray-700">
            <svg className="w-4 h-4 mr-2 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
            <span>{course.dept}</span>
          </div>
        )}

        {/* Time and Classroom */}
        <div className="flex flex-wrap gap-2 mt-3">
          {course.time && (
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {course.time}
            </span>
          )}
          {course.classroom && (
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              {course.classroom}
            </span>
          )}
        </div>
      </div>

      {/* Semester Badge */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <span className="text-xs text-gray-500">
          {course.acy} {course.sem === 1 ? 'Fall' : 'Spring'}
        </span>
      </div>
    </div>
  );
};

export default CourseCard;
