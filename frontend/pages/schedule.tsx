/**
 * Schedule Page - Course Schedule Builder
 *
 * Page for building and managing personal course schedules.
 * Features:
 * - Display schedule grid
 * - Add/remove courses
 * - Detect and display conflicts
 * - Save schedule to localStorage
 * - Export schedule functionality
 * - Responsive calendar view
 */

import React, { useState, useEffect, useMemo } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import {
  Header,
  Footer,
  ScheduleGrid,
  ConflictWarning,
  NoConflictMessage,
  detectConflicts,
  Loading,
  Error,
} from '@/components';
import { useCourses } from '@/lib/hooks/useCourses';
import type { Course } from '@/lib/types';

/**
 * Schedule page component
 */
export default function SchedulePage() {
  const [scheduleIds, setScheduleIds] = useState<number[]>([]);
  const [isClient, setIsClient] = useState(false);

  // Fetch all courses (needed to resolve IDs to course objects)
  const { courses: allCourses, loading, error } = useCourses();

  /**
   * Load schedule from localStorage on mount
   */
  useEffect(() => {
    setIsClient(true);
    const stored = localStorage.getItem('schedule');
    if (stored) {
      try {
        const ids = JSON.parse(stored);
        setScheduleIds(Array.isArray(ids) ? ids : []);
      } catch (err) {
        console.error('Failed to parse schedule:', err);
        setScheduleIds([]);
      }
    }
  }, []);

  /**
   * Get courses in schedule
   */
  const scheduledCourses = useMemo(() => {
    if (!allCourses.length || !scheduleIds.length) return [];
    return allCourses.filter((course) => scheduleIds.includes(course.id));
  }, [allCourses, scheduleIds]);

  /**
   * Detect conflicts
   */
  const conflicts = useMemo(() => {
    return detectConflicts(scheduledCourses);
  }, [scheduledCourses]);

  /**
   * Remove course from schedule
   */
  const handleRemoveCourse = (course: Course) => {
    const updatedIds = scheduleIds.filter((id) => id !== course.id);
    setScheduleIds(updatedIds);
    localStorage.setItem('schedule', JSON.stringify(updatedIds));
  };

  /**
   * Clear entire schedule
   */
  const handleClearSchedule = () => {
    if (confirm('Are you sure you want to clear your entire schedule?')) {
      setScheduleIds([]);
      localStorage.setItem('schedule', JSON.stringify([]));
    }
  };

  /**
   * Export schedule as JSON
   */
  const handleExportJSON = () => {
    const data = {
      exported_at: new Date().toISOString(),
      courses: scheduledCourses.map((course) => ({
        id: course.id,
        crs_no: course.crs_no,
        name: course.name,
        teacher: course.teacher,
        credits: course.credits,
        time: course.time,
        classroom: course.classroom,
      })),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nycu-schedule-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  /**
   * Export schedule as text
   */
  const handleExportText = () => {
    let text = 'NYCU Course Schedule\n';
    text += '='.repeat(50) + '\n';
    text += `Exported: ${new Date().toLocaleString()}\n\n`;

    if (scheduledCourses.length === 0) {
      text += 'No courses in schedule.\n';
    } else {
      scheduledCourses.forEach((course, index) => {
        text += `${index + 1}. ${course.name || 'Untitled Course'}\n`;
        text += `   Course No: ${course.crs_no}\n`;
        if (course.teacher) text += `   Teacher: ${course.teacher}\n`;
        if (course.credits) text += `   Credits: ${course.credits}\n`;
        if (course.time) text += `   Time: ${course.time}\n`;
        if (course.classroom) text += `   Classroom: ${course.classroom}\n`;
        text += '\n';
      });
    }

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nycu-schedule-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  /**
   * Calculate total credits
   */
  const totalCredits = useMemo(() => {
    return scheduledCourses.reduce((sum, course) => {
      return sum + (course.credits || 0);
    }, 0);
  }, [scheduledCourses]);

  // Don't render until client-side to avoid hydration mismatch
  if (!isClient) {
    return null;
  }

  return (
    <>
      <Head>
        <title>My Schedule - NYCU Course Platform</title>
        <meta
          name="description"
          content="View and manage your NYCU course schedule"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />

        <main className="flex-1 container mx-auto px-4 py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
              My Schedule
            </h1>
            <p className="text-gray-600 text-lg">
              Build and manage your course schedule
            </p>
          </div>

          {/* Action Bar */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              {/* Stats */}
              <div className="flex flex-wrap items-center gap-6">
                <div>
                  <p className="text-sm text-gray-600">Total Courses</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {scheduledCourses.length}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Credits</p>
                  <p className="text-2xl font-bold text-gray-900">{totalCredits}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Conflicts</p>
                  <p className="text-2xl font-bold text-red-600">
                    {conflicts.length}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3">
                <Link
                  href="/"
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                >
                  <svg
                    className="mr-2 w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Add Courses
                </Link>

                {scheduledCourses.length > 0 && (
                  <>
                    <div className="relative group">
                      <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition">
                        <svg
                          className="mr-2 w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                          />
                        </svg>
                        Export
                        <svg
                          className="ml-2 w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                          />
                        </svg>
                      </button>
                      <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 hidden group-hover:block z-10">
                        <div className="py-1">
                          <button
                            onClick={handleExportJSON}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            Export as JSON
                          </button>
                          <button
                            onClick={handleExportText}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            Export as Text
                          </button>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={handleClearSchedule}
                      className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition"
                    >
                      <svg
                        className="mr-2 w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                      Clear All
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Conflict Warning */}
          {conflicts.length > 0 && (
            <div className="mb-6">
              <ConflictWarning
                conflicts={conflicts}
                onResolve={handleRemoveCourse}
              />
            </div>
          )}

          {/* No Conflicts Message */}
          {scheduledCourses.length > 0 && conflicts.length === 0 && (
            <div className="mb-6">
              <NoConflictMessage />
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="bg-white rounded-lg shadow-md p-12">
              <Loading message="Loading schedule..." />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-white rounded-lg shadow-md p-12">
              <Error
                message="Failed to load courses"
                onRetry={() => window.location.reload()}
              />
            </div>
          )}

          {/* Schedule Grid */}
          {!loading && !error && (
            <div className="bg-white rounded-lg shadow-md p-6">
              {scheduledCourses.length > 0 ? (
                <ScheduleGrid
                  courses={scheduledCourses}
                  onRemoveCourse={handleRemoveCourse}
                />
              ) : (
                // Empty State
                <div className="py-12 text-center">
                  <svg
                    className="w-24 h-24 mx-auto text-gray-300 mb-4"
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
                    Your Schedule is Empty
                  </h3>
                  <p className="text-gray-500 mb-6">
                    Start building your schedule by adding courses
                  </p>
                  <Link
                    href="/"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                  >
                    <svg
                      className="mr-2 w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                    Browse Courses
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Course List (below schedule) */}
          {scheduledCourses.length > 0 && (
            <div className="mt-6 bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Course List ({scheduledCourses.length})
              </h2>
              <div className="space-y-3">
                {scheduledCourses.map((course) => (
                  <div
                    key={course.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition"
                  >
                    <div className="flex-1 min-w-0">
                      <Link href={`/course/${course.id}`} className="block hover:text-blue-600">
                        <h3 className="text-base font-semibold text-gray-900 truncate">
                          {course.name || 'Untitled Course'}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {course.crs_no}
                          {course.teacher && ` · ${course.teacher}`}
                          {course.credits && ` · ${course.credits} credits`}
                        </p>
                        <p className="text-sm text-gray-500">
                          {course.time || 'Time TBA'}
                          {course.classroom && ` · ${course.classroom}`}
                        </p>
                      </Link>
                    </div>
                    <button
                      onClick={() => handleRemoveCourse(course)}
                      className="ml-4 inline-flex items-center px-3 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition"
                      aria-label={`Remove ${course.name}`}
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>

        <Footer />
      </div>
    </>
  );
}
