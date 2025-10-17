/**
 * ConflictWarning Component
 *
 * Displays warnings for conflicting course schedules.
 * Features:
 * - Visual highlight of conflicts
 * - List of conflicting courses
 * - Detailed conflict information
 * - Action buttons to resolve conflicts
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <ConflictWarning
 *   conflicts={[
 *     [course1, course2],
 *     [course3, course4]
 *   ]}
 *   onResolve={(courses) => handleResolve(courses)}
 * />
 * ```
 */

import React, { useMemo } from 'react';
import { Course } from '../../lib/types';

/**
 * Props for the ConflictWarning component
 */
interface ConflictWarningProps {
  /** Array of conflict groups, where each group contains courses that conflict */
  conflicts: Course[][];
  /** Optional callback to resolve a conflict by removing a course */
  onResolve?: (course: Course) => void;
  /** Whether to show in compact mode */
  compact?: boolean;
}

/**
 * Conflict warning component
 *
 * @param {ConflictWarningProps} props - Component props
 * @returns {JSX.Element} The rendered conflict warning
 */
const ConflictWarning: React.FC<ConflictWarningProps> = ({
  conflicts,
  onResolve,
  compact = false,
}) => {
  /**
   * Calculate total number of conflicts
   */
  const totalConflicts = useMemo(() => {
    return conflicts.reduce((sum, group) => sum + (group.length > 1 ? 1 : 0), 0);
  }, [conflicts]);

  /**
   * Get all conflicting course IDs
   */
  const conflictingCourseIds = useMemo(() => {
    const ids = new Set<number>();
    conflicts.forEach((group) => {
      if (group.length > 1) {
        group.forEach((course) => ids.add(course.id));
      }
    });
    return ids;
  }, [conflicts]);

  // No conflicts
  if (totalConflicts === 0) {
    return null;
  }

  // Compact view
  if (compact) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <p className="text-sm font-medium text-yellow-800">
            {totalConflicts} schedule {totalConflicts === 1 ? 'conflict' : 'conflicts'} detected
          </p>
        </div>
      </div>
    );
  }

  // Full view
  return (
    <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6 shadow-md">
      {/* Header */}
      <div className="flex items-start mb-4">
        <div className="flex-shrink-0">
          <svg className="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-lg font-bold text-yellow-800 mb-1">
            Schedule Conflicts Detected
          </h3>
          <p className="text-sm text-yellow-700">
            {totalConflicts} {totalConflicts === 1 ? 'course has' : 'courses have'} conflicting time slots.
            Please review and resolve the conflicts below.
          </p>
        </div>
      </div>

      {/* Conflict details */}
      <div className="space-y-4">
        {conflicts.map((group, groupIndex) => {
          if (group.length <= 1) return null;

          return (
            <div
              key={groupIndex}
              className="bg-white rounded-lg border-2 border-yellow-200 p-4"
            >
              <div className="flex items-center mb-3">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Conflict #{groupIndex + 1}
                </span>
                <span className="ml-2 text-sm text-gray-600">
                  {group[0].time}
                </span>
              </div>

              <div className="space-y-2">
                {group.map((course) => (
                  <div
                    key={course.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-semibold text-gray-900 truncate">
                        {course.name || 'Untitled Course'}
                      </h4>
                      <p className="text-xs text-gray-600">
                        {course.crs_no}
                        {course.teacher && ` · ${course.teacher}`}
                        {course.classroom && ` · ${course.classroom}`}
                      </p>
                    </div>

                    {onResolve && (
                      <button
                        onClick={() => onResolve(course)}
                        className="ml-3 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-yellow-200">
        <p className="text-xs text-yellow-700">
          <strong>Tip:</strong> Remove one of the conflicting courses from each group to resolve the conflict.
        </p>
      </div>
    </div>
  );
};

/**
 * Inline conflict badge for compact displays
 */
export const ConflictBadge: React.FC<{ count: number; onClick?: () => void }> = ({
  count,
  onClick,
}) => {
  if (count === 0) return null;

  return (
    <button
      onClick={onClick}
      className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 hover:bg-red-200 transition-colors"
    >
      <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      {count} {count === 1 ? 'Conflict' : 'Conflicts'}
    </button>
  );
};

/**
 * Success message when no conflicts exist
 */
export const NoConflictMessage: React.FC = () => {
  return (
    <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded">
      <div className="flex items-center">
        <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-sm font-medium text-green-800">
          No schedule conflicts detected
        </p>
      </div>
    </div>
  );
};

/**
 * Detect conflicts in a list of courses
 * @param courses - Array of courses to check
 * @returns Array of conflict groups
 */
export const detectConflicts = (courses: Course[]): Course[][] => {
  const conflicts: Course[][] = [];
  const timeSlotMap = new Map<string, Course[]>();

  // Group courses by time slots
  courses.forEach((course) => {
    if (!course.time) return;

    const timeKey = course.time.toLowerCase().replace(/\s+/g, '');
    if (!timeSlotMap.has(timeKey)) {
      timeSlotMap.set(timeKey, []);
    }
    timeSlotMap.get(timeKey)!.push(course);
  });

  // Find conflicts (more than one course in the same time slot)
  timeSlotMap.forEach((coursesInSlot) => {
    if (coursesInSlot.length > 1) {
      conflicts.push(coursesInSlot);
    }
  });

  return conflicts;
};

export default ConflictWarning;
