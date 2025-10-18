/**
 * Timetable View Component - Visual Course Schedule Display
 *
 * Displays courses in a weekly timetable format similar to traditional class schedules.
 * Shows courses in their correct time slots with visual indicators.
 */

import React, { useMemo } from 'react';
import { parseCourseTime, TIME_SLOTS, DAY_NAMES_EN } from '@/lib/utils/timeParser';

interface Course {
  id: number;
  crs_no: string;
  name: string;
  teacher?: string;
  credits?: number;
  time?: string;
  classroom?: string;
}

interface ScheduleCourse {
  id: number;
  course: Course;
}

interface TimetableViewProps {
  courses: ScheduleCourse[];
  onClose: () => void;
}

// Color palette for different courses
const COURSE_COLORS = [
  'bg-blue-100 border-blue-300 text-blue-900 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-100',
  'bg-green-100 border-green-300 text-green-900 dark:bg-green-900/30 dark:border-green-700 dark:text-green-100',
  'bg-purple-100 border-purple-300 text-purple-900 dark:bg-purple-900/30 dark:border-purple-700 dark:text-purple-100',
  'bg-pink-100 border-pink-300 text-pink-900 dark:bg-pink-900/30 dark:border-pink-700 dark:text-pink-100',
  'bg-yellow-100 border-yellow-300 text-yellow-900 dark:bg-yellow-900/30 dark:border-yellow-700 dark:text-yellow-100',
  'bg-indigo-100 border-indigo-300 text-indigo-900 dark:bg-indigo-900/30 dark:border-indigo-700 dark:text-indigo-100',
  'bg-red-100 border-red-300 text-red-900 dark:bg-red-900/30 dark:border-red-700 dark:text-red-100',
  'bg-teal-100 border-teal-300 text-teal-900 dark:bg-teal-900/30 dark:border-teal-700 dark:text-teal-100',
];

interface GridCell {
  course: Course;
  colorClass: string;
  rowSpan: number;
  isStart: boolean;
}

export default function TimetableView({ courses, onClose }: TimetableViewProps) {
  // Build grid: 7 days (Mon-Sun) x 13 periods
  const timetableGrid = useMemo(() => {
    const grid: (GridCell | null)[][] = Array(7)
      .fill(null)
      .map(() => Array(13).fill(null));

    // Assign colors to courses
    const courseColors = new Map<number, string>();
    courses.forEach((sc, index) => {
      courseColors.set(sc.course.id, COURSE_COLORS[index % COURSE_COLORS.length]);
    });

    // Place courses in grid
    courses.forEach((sc) => {
      const slots = parseCourseTime(sc.course.time);

      slots.forEach((slot) => {
        const [start, end] = slot.periodRange;
        const day = slot.day;
        const colorClass = courseColors.get(sc.course.id) || COURSE_COLORS[0];

        // Mark the starting cell
        if (grid[day][start - 1] === null) {
          grid[day][start - 1] = {
            course: sc.course,
            colorClass,
            rowSpan: end - start + 1,
            isStart: true,
          };
        }

        // Mark intermediate cells as occupied (but not rendered)
        for (let p = start + 1; p <= end; p++) {
          if (grid[day][p - 1] === null) {
            grid[day][p - 1] = {
              course: sc.course,
              colorClass,
              rowSpan: 0,
              isStart: false,
            };
          }
        }
      });
    });

    return grid;
  }, [courses]);

  // Stop propagation when clicking on the timetable itself
  const handleTimetableClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-auto"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-7xl w-full max-h-[90vh] overflow-auto"
        onClick={handleTimetableClick}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                課表預覽
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                點擊外部區域關閉 • {courses.length} 門課程
              </p>
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
            >
              關閉
            </button>
          </div>
        </div>

        {/* Timetable Grid */}
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse min-w-[900px]">
              <thead>
                <tr>
                  <th className="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 p-2 text-sm font-semibold text-gray-700 dark:text-gray-300 w-20">
                    節次
                  </th>
                  {DAY_NAMES_EN.map((day) => (
                    <th
                      key={day}
                      className="border border-gray-300 dark:border-gray-600 bg-indigo-50 dark:bg-indigo-900/30 p-2 text-sm font-semibold text-indigo-700 dark:text-indigo-300"
                    >
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((timeSlot, periodIndex) => (
                  <tr key={timeSlot.period} className="h-16">
                    {/* Time column */}
                    <td className="border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 p-2 text-center">
                      <div className="text-xs font-semibold text-gray-900 dark:text-white">
                        {timeSlot.period}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {timeSlot.time}
                      </div>
                    </td>

                    {/* Day columns */}
                    {timetableGrid.map((dayColumn, dayIndex) => {
                      const cell = dayColumn[periodIndex];

                      // Skip if this cell is part of a multi-period course (but not the start)
                      if (cell && !cell.isStart) {
                        return null;
                      }

                      // Empty cell
                      if (!cell) {
                        return (
                          <td
                            key={`${dayIndex}-${periodIndex}`}
                            className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 p-1"
                          />
                        );
                      }

                      // Course cell
                      return (
                        <td
                          key={`${dayIndex}-${periodIndex}`}
                          rowSpan={cell.rowSpan}
                          className={`border-2 ${cell.colorClass} p-2 align-top relative group cursor-pointer hover:shadow-lg transition-shadow`}
                        >
                          <div className="text-xs font-bold truncate">
                            {cell.course.name}
                          </div>
                          {cell.course.teacher && (
                            <div className="text-xs opacity-75 truncate mt-1">
                              {cell.course.teacher}
                            </div>
                          )}
                          {cell.course.classroom && (
                            <div className="text-xs opacity-75 truncate mt-1">
                              📍 {cell.course.classroom}
                            </div>
                          )}

                          {/* Tooltip on hover */}
                          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-20">
                            <div className="bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded-lg py-2 px-3 shadow-lg whitespace-nowrap">
                              <div className="font-bold">{cell.course.name}</div>
                              <div className="mt-1">{cell.course.crs_no}</div>
                              {cell.course.teacher && <div className="mt-1">教師: {cell.course.teacher}</div>}
                              {cell.course.credits && <div className="mt-1">學分: {cell.course.credits}</div>}
                              <div className="mt-1">{cell.course.time}</div>
                              <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                                <div className="border-4 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
                              </div>
                            </div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Legend */}
          {courses.length > 0 && (
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                課程列表
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {courses.map((sc, index) => (
                  <div
                    key={sc.id}
                    className={`flex items-center gap-2 p-2 rounded border ${
                      COURSE_COLORS[index % COURSE_COLORS.length]
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold truncate">
                        {sc.course.name}
                      </div>
                      <div className="text-xs opacity-75">
                        {sc.course.crs_no}
                        {sc.course.credits && ` • ${sc.course.credits}學分`}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {courses.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400 text-lg">
                課表中沒有課程
              </p>
              <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
                請先添加課程到課表
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
