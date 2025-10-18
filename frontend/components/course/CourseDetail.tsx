/**
 * CourseDetail Component
 *
 * Displays comprehensive details for a single course.
 * Features:
 * - All course fields (name, teacher, credits, dept, time, classroom)
 * - Parsed JSON details with formatted display
 * - Back navigation button
 * - Share button
 * - Responsive layout
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <CourseDetail
 *   course={course}
 *   onBack={() => router.back()}
 * />
 * ```
 */

import React, { useMemo } from 'react';
import { useTranslation } from 'next-i18next';
import { Course } from '../../lib/types';
import {
  parseCourseDetails,
  formatScheduleDisplay,
  formatClassroomDisplay,
} from '@/utils/nycuParser';

/**
 * Props for the CourseDetail component
 */
interface CourseDetailProps {
  /** Course data to display */
  course: Course;
  /** Optional callback for back navigation */
  onBack?: () => void;
  /** Optional callback for adding to schedule */
  onAddToSchedule?: (course: Course) => void;
}

/**
 * Detailed view component for a single course
 *
 * @param {CourseDetailProps} props - Component props
 * @returns {JSX.Element} The rendered course detail view
 */
const CourseDetail: React.FC<CourseDetailProps> = ({
  course,
  onBack,
  onAddToSchedule,
}) => {
  const { t, i18n } = useTranslation('course');

  /**
   * Parse and format the details JSON field
   */
  const parsedDetails = useMemo(() => {
    if (!course.details) return null;

    try {
      return JSON.parse(course.details);
    } catch (error) {
      console.error('Failed to parse course details:', error);
      return null;
    }
  }, [course.details]);

  /**
   * Parse time and classroom information from course.details
   */
  const timeClassroomInfo = useMemo(() => {
    return parseCourseDetails(course.details);
  }, [course.details]);

  /**
   * Copy current URL to clipboard
   */
  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      // You might want to show a toast notification here
      alert('Link copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy link:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header with back button */}
      <div className="mb-6 flex items-center justify-between">
        {onBack && (
          <button
            onClick={onBack}
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back
          </button>
        )}
        <button
          onClick={handleShare}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
            />
          </svg>
          Share
        </button>
      </div>

      {/* Main content card */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-8">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">
                {course.name || 'Untitled Course'}
              </h1>
              <p className="text-blue-100 text-lg font-medium">
                {course.crs_no}
              </p>
            </div>
            <div className="ml-4">
              <span className="inline-block bg-blue-500 bg-opacity-50 rounded-full px-4 py-2 text-sm font-medium">
                {course.acy} {course.sem === 1 ? 'Fall' : 'Spring'}
              </span>
            </div>
          </div>
        </div>

        {/* Details section */}
        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Teacher */}
            {course.teacher && (
              <DetailItem
                icon={
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                }
                label="Instructor"
                value={course.teacher}
              />
            )}

            {/* Credits */}
            {course.credits !== null && course.credits !== undefined && (
              <DetailItem
                icon={
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                }
                label="Credits"
                value={`${course.credits}`}
              />
            )}

            {/* Department */}
            {course.dept && (
              <DetailItem
                icon={
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                }
                label="Department"
                value={course.dept}
              />
            )}

            {/* Course Code */}
            {course.crs_no && (
              <DetailItem
                icon={
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
                  />
                }
                label="Course Code"
                value={course.crs_no}
              />
            )}

            {/* Schedule - Parse from details.time_classroom */}
            {timeClassroomInfo && timeClassroomInfo.schedule.length > 0 && (
              <DetailItem
                icon={
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                }
                label="Schedule"
                value={formatScheduleDisplay(timeClassroomInfo.schedule, i18n.language === 'zh' ? 'zh' : 'en')}
              />
            )}

            {/* Classroom - Parse from details.time_classroom */}
            {timeClassroomInfo && timeClassroomInfo.classroom && (
              <DetailItem
                icon={
                  <>
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
                  </>
                }
                label="Classroom"
                value={formatClassroomDisplay(timeClassroomInfo.classroom, i18n.language === 'zh' ? 'zh' : 'en')}
              />
            )}
          </div>

          {/* Official Syllabus Links */}
          {(course.syllabus_url_zh || course.syllabus_url_en) && (
            <div className="border-t pt-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Official Syllabus
              </h2>
              <div className="flex flex-wrap gap-3">
                {course.syllabus_url_zh && (
                  <a
                    href={course.syllabus_url_zh}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition shadow-sm"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    查看中文大綱 (View Chinese Syllabus)
                  </a>
                )}
                {course.syllabus_url_en && (
                  <a
                    href={course.syllabus_url_en}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition shadow-sm"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    View English Syllabus
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Course Syllabus / Outline Section */}
          {(course.syllabus || course.syllabus_zh) && (
            <div className="border-t pt-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                {t('syllabus') || 'Course Syllabus'}
              </h2>

              <div className="space-y-6">
                {/* English Syllabus */}
                {course.syllabus && (
                  <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                    <h3 className="text-lg font-semibold text-blue-900 mb-3">📖 English (English)</h3>
                    <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {course.syllabus}
                    </div>
                  </div>
                )}

                {/* Chinese Syllabus */}
                {course.syllabus_zh && (
                  <div className="bg-amber-50 rounded-lg p-6 border border-amber-200">
                    <h3 className="text-lg font-semibold text-amber-900 mb-3">📖 繁體中文 (Traditional Chinese)</h3>
                    <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {course.syllabus_zh}
                    </div>
                  </div>
                )}

                {/* No Syllabus Message */}
                {!course.syllabus && !course.syllabus_zh && (
                  <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-600">
                    {t('noSyllabus') || 'No course syllabus available'}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Additional Details */}
          {parsedDetails && (
            <div className="border-t pt-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Additional Information
              </h2>
              <div className="bg-gray-50 rounded-lg p-6">
                <dl className="space-y-3">
                  {Object.entries(parsedDetails)
                    .filter(([key]) => !['num_limit', 'reg_num', 'hours', 'time_classroom', 'cos_id', 'cos_code'].includes(key))
                    .map(([key, value]) => (
                    <div key={key} className="flex flex-col sm:flex-row">
                      <dt className="font-medium text-gray-700 sm:w-1/3 capitalize">
                        {key.replace(/_/g, ' ')}:
                      </dt>
                      <dd className="text-gray-900 sm:w-2/3 mt-1 sm:mt-0">
                        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                      </dd>
                    </div>
                  ))}
                </dl>
              </div>
            </div>
          )}

          {/* Action button */}
          {onAddToSchedule && (
            <div className="mt-8 flex justify-center">
              <button
                onClick={() => onAddToSchedule(course)}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Add to Schedule
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Detail item component for consistent formatting
 */
const DetailItem: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string;
}> = ({ icon, label, value }) => {
  return (
    <div className="flex items-start space-x-3">
      <div className="flex-shrink-0">
        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {icon}
          </svg>
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-500 mb-1">{label}</p>
        <p className="text-base font-semibold text-gray-900 break-words">{value}</p>
      </div>
    </div>
  );
};

export default CourseDetail;
