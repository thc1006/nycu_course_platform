/**
 * ScheduleGrid Component
 *
 * Displays a weekly schedule grid with courses in their time slots.
 * Features:
 * - 7 columns (Monday-Sunday)
 * - Time slots from 8:00 to 22:00
 * - Course placement based on time strings
 * - Click handler for courses
 * - Responsive design with mobile view
 * - Color-coded courses
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <ScheduleGrid
 *   courses={selectedCourses}
 *   onCourseClick={(course) => handleCourseClick(course)}
 * />
 * ```
 */

import React, { useMemo } from 'react';
import { Course } from '../../lib/types';
import CourseSlot from './CourseSlot';

/**
 * Props for the ScheduleGrid component
 */
interface ScheduleGridProps {
  /** Array of courses to display in schedule */
  courses: Course[];
  /** Optional click handler for course slots */
  onCourseClick?: (course: Course) => void;
  /** Optional handler to remove a course */
  onRemoveCourse?: (course: Course) => void;
}

/**
 * Days of the week
 */
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

/**
 * Time slots (8:00 to 22:00)
 */
const TIME_SLOTS = Array.from({ length: 15 }, (_, i) => i + 8); // 8 to 22

/**
 * Parse time string to extract day and time information
 * Handles formats like "Mon 10:00-12:00", "M1M2", "T3T4", etc.
 */
const parseTimeString = (timeStr: string | null): Array<{ day: number; startHour: number; endHour: number }> => {
  if (!timeStr) return [];

  const slots: Array<{ day: number; startHour: number; endHour: number }> = [];

  // Try to match format like "Mon 10:00-12:00" or "Monday 10:00-12:00"
  const dayTimeMatch = timeStr.match(/(\w+)\s+(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})/);
  if (dayTimeMatch) {
    const [, dayName, startHour, , endHour] = dayTimeMatch;
    const dayIndex = DAYS.findIndex(d => dayName.toLowerCase().startsWith(d.toLowerCase()));
    if (dayIndex !== -1) {
      slots.push({
        day: dayIndex,
        startHour: parseInt(startHour, 10),
        endHour: parseInt(endHour, 10),
      });
    }
    return slots;
  }

  // Try to match format like "M1M2" (Monday periods 1-2)
  // M=Monday, T=Tuesday, W=Wednesday, R=Thursday, F=Friday, S=Saturday, U=Sunday
  const periodPattern = /([MTWRFSU])(\d)/g;
  let match;
  while ((match = periodPattern.exec(timeStr)) !== null) {
    const [, dayCode, period] = match;
    const dayMap: { [key: string]: number } = {
      M: 0, // Monday
      T: 1, // Tuesday
      W: 2, // Wednesday
      R: 3, // Thursday
      F: 4, // Friday
      S: 5, // Saturday
      U: 6, // Sunday
    };
    const dayIndex = dayMap[dayCode];
    const periodNum = parseInt(period, 10);

    // Each period is typically 1 hour, starting at 8:00
    const startHour = 7 + periodNum;
    const endHour = startHour + 1;

    if (dayIndex !== undefined) {
      slots.push({ day: dayIndex, startHour, endHour });
    }
  }

  return slots;
};

/**
 * Schedule grid component
 *
 * @param {ScheduleGridProps} props - Component props
 * @returns {JSX.Element} The rendered schedule grid
 */
const ScheduleGrid: React.FC<ScheduleGridProps> = ({
  courses,
  onCourseClick,
  onRemoveCourse,
}) => {
  /**
   * Parse all courses and organize by day and time
   */
  const scheduleData = useMemo(() => {
    const data: { [key: string]: Course[] } = {};

    courses.forEach((course, index) => {
      const slots = parseTimeString(course.time);

      slots.forEach((slot) => {
        const key = `${slot.day}-${slot.startHour}`;
        if (!data[key]) {
          data[key] = [];
        }
        data[key].push({
          ...course,
          // Add index for consistent color assignment
          _colorIndex: index % 10,
        } as any);
      });
    });

    return data;
  }, [courses]);

  /**
   * Get courses for a specific day and time slot
   */
  const getCoursesForSlot = (day: number, hour: number): Course[] => {
    const key = `${day}-${hour}`;
    return scheduleData[key] || [];
  };

  return (
    <div className="w-full overflow-x-auto">
      <div className="min-w-max">
        {/* Desktop view */}
        <div className="hidden md:block">
          <table className="w-full border-collapse border border-gray-300 bg-white shadow-lg rounded-lg overflow-hidden">
            <thead>
              <tr className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                <th className="border border-gray-300 px-4 py-3 text-left font-semibold min-w-[80px]">
                  Time
                </th>
                {DAYS.map((day) => (
                  <th key={day} className="border border-gray-300 px-4 py-3 text-center font-semibold min-w-[120px]">
                    {day}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {TIME_SLOTS.map((hour) => (
                <tr key={hour} className="hover:bg-gray-50 transition-colors">
                  <td className="border border-gray-300 px-4 py-2 font-medium text-gray-700 bg-gray-50">
                    {hour}:00
                  </td>
                  {DAYS.map((_, dayIndex) => {
                    const coursesInSlot = getCoursesForSlot(dayIndex, hour);
                    return (
                      <td
                        key={dayIndex}
                        className="border border-gray-300 p-1 align-top min-h-[60px]"
                      >
                        {coursesInSlot.length > 0 && (
                          <div className="space-y-1">
                            {coursesInSlot.map((course, idx) => (
                              <CourseSlot
                                key={`${course.id}-${idx}`}
                                course={course}
                                onClick={() => onCourseClick?.(course)}
                                onRemove={() => onRemoveCourse?.(course)}
                              />
                            ))}
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile view */}
        <div className="md:hidden space-y-4">
          {DAYS.map((day, dayIndex) => (
            <div key={day} className="bg-white rounded-lg shadow border border-gray-200">
              <div className="bg-blue-600 text-white px-4 py-3 rounded-t-lg font-semibold">
                {day}
              </div>
              <div className="p-2 space-y-2">
                {TIME_SLOTS.map((hour) => {
                  const coursesInSlot = getCoursesForSlot(dayIndex, hour);
                  if (coursesInSlot.length === 0) return null;
                  return (
                    <div key={hour} className="border-l-4 border-blue-500 pl-3">
                      <div className="text-xs text-gray-500 mb-1">{hour}:00</div>
                      <div className="space-y-1">
                        {coursesInSlot.map((course, idx) => (
                          <CourseSlot
                            key={`${course.id}-${idx}`}
                            course={course}
                            onClick={() => onCourseClick?.(course)}
                            onRemove={() => onRemoveCourse?.(course)}
                          />
                        ))}
                      </div>
                    </div>
                  );
                })}
                {TIME_SLOTS.every((hour) => getCoursesForSlot(dayIndex, hour).length === 0) && (
                  <div className="text-center py-4 text-gray-400 text-sm">
                    No classes scheduled
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Empty state */}
      {courses.length === 0 && (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <svg
            className="w-20 h-20 mx-auto text-gray-300 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            No Courses in Schedule
          </h3>
          <p className="text-gray-500">
            Add courses to your schedule to see them here
          </p>
        </div>
      )}
    </div>
  );
};

export default ScheduleGrid;
