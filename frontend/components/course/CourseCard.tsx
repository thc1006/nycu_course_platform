/**
 * Course Card Component - NDHU-Inspired Design
 *
 * Displays a single course in minimalist card format with NDHU aesthetic.
 * Adapted for NYCU's richer course data structure.
 *
 * Features:
 * - Minimalist, clean design (following NDHU style)
 * - NYCU schedule code parsing (day_codes, time_codes)
 * - Bilingual support (English & Traditional Chinese)
 * - Required/Elective status badge
 * - Syllabus availability indicator
 * - Light/Dark mode support
 * - Responsive design with smooth animations
 * - Action buttons (Add to Schedule, View Details)
 */

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';
import { formatSchedule } from '@/utils/scheduleParser';
import {
  parseCourseDetails,
  formatScheduleDisplay,
  formatClassroomDisplay,
} from '@/utils/nycuParser';
import { BookOpen, Plus, ChevronRight } from 'lucide-react';

interface CourseCardProps {
  course: {
    id: number;
    crs_no: string;
    name: string;
    teacher?: string;
    credits?: number;
    dept?: string;
    day_codes?: string;
    time_codes?: string;
    classroom_codes?: string;
    required?: string;
    syllabus?: string;
    syllabus_zh?: string;
    details?: string | null;
  };
  onAddSchedule?: (courseId: number) => void;
  className?: string;
  showActions?: boolean;
}

const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onAddSchedule,
  className = '',
  showActions = true,
}) => {
  const router = useRouter();
  const lang = (router.locale || 'en') as 'en' | 'zh';
  const { t } = useTranslation('common');

  const [isAdding, setIsAdding] = useState(false);

  // Parse time and classroom from course details (NYCU format)
  const timeClassroomInfo = useMemo(() => {
    return parseCourseDetails(course.details);
  }, [course.details]);

  // Format schedule - use parsed data if available, otherwise fall back to old format
  const schedule = useMemo(() => {
    if (timeClassroomInfo && timeClassroomInfo.schedule.length > 0) {
      return formatScheduleDisplay(timeClassroomInfo.schedule, lang === 'zh' ? 'zh' : 'en');
    }
    // Fallback to old format for backwards compatibility
    return formatSchedule(
      course.day_codes,
      course.time_codes,
      course.classroom_codes,
      lang === 'zh' ? 'zh' : 'en'
    );
  }, [timeClassroomInfo, course.day_codes, course.time_codes, course.classroom_codes, lang]);

  // Format classroom
  const classroom = useMemo(() => {
    if (timeClassroomInfo && timeClassroomInfo.classroom) {
      return formatClassroomDisplay(timeClassroomInfo.classroom, lang === 'zh' ? 'zh' : 'en');
    }
    return null;
  }, [timeClassroomInfo, lang]);

  // Check for syllabus
  const hasSyllabus = course.syllabus || course.syllabus_zh;

  // Required status
  const isRequired = course.required === 'Y' || course.required === '1';
  const statusLabel = isRequired
    ? lang === 'zh' ? '必修' : 'Required'
    : lang === 'zh' ? '選修' : 'Elective';

  // Handle add schedule
  const handleAddSchedule = async () => {
    if (onAddSchedule) {
      setIsAdding(true);
      try {
        onAddSchedule(course.id);
      } finally {
        setIsAdding(false);
      }
    }
  };

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-all duration-300 ease-out hover:shadow-lg hover:border-indigo-300 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-indigo-600 hover:scale-[1.02] dark:hover:bg-gray-750 ${className}`}
    >
      {/* Header with Code and Status */}
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <code className="inline-block text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-2 py-1 rounded-xl mb-1 transition-colors duration-200">
            {course.crs_no}
          </code>
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 leading-snug break-words">
            {course.name}
          </h3>
        </div>

        {course.required !== undefined && (
          <span
            className={`flex-shrink-0 text-xs font-semibold px-2 py-1 rounded-xl whitespace-nowrap transition-colors duration-200 ${
              isRequired
                ? 'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300'
                : 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
            }`}
          >
            {statusLabel}
          </span>
        )}
      </div>

      {/* Course Details */}
      <div className="space-y-2 mb-4 text-sm">
        {course.teacher && (
          <div className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
            <span className="flex-shrink-0 text-base leading-relaxed">👨‍🏫</span>
            <span className="break-words">{course.teacher}</span>
          </div>
        )}

        {(course.credits || course.dept) && (
          <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
            {course.credits && (
              <div className="flex items-center gap-1">
                <span>📚</span>
                <span>{course.credits} {lang === 'zh' ? '學分' : 'Cr'}</span>
              </div>
            )}
            {course.dept && (
              <div className="flex items-center gap-1">
                <span>🏢</span>
                <span>{course.dept}</span>
              </div>
            )}
          </div>
        )}

        {schedule !== 'TBA' && (
          <div className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
            <span className="flex-shrink-0 text-base leading-relaxed">⏰</span>
            <span className="break-words">{schedule}</span>
          </div>
        )}

        {classroom && (
          <div className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
            <span className="flex-shrink-0 text-base leading-relaxed">📍</span>
            <span className="break-words">{classroom}</span>
          </div>
        )}
      </div>

      {/* Syllabus Indicator */}
      {hasSyllabus && (
        <div className="mb-4 flex items-center gap-2 p-2 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800 transition-colors duration-200">
          <BookOpen className="h-4 w-4 text-indigo-600 dark:text-indigo-400 flex-shrink-0" />
          <span className="text-xs text-indigo-700 dark:text-indigo-300 font-medium">
            {lang === 'zh' ? '有課程綱要' : 'Syllabus Available'}
          </span>
        </div>
      )}

      {/* Action Buttons */}
      {showActions && (
        <div className="flex gap-2">
          <button
            onClick={handleAddSchedule}
            disabled={isAdding}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:from-gray-400 disabled:to-gray-400 text-white text-sm font-medium rounded-xl transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-md hover:shadow-lg"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">
              {lang === 'zh' ? '加入課表' : 'Add to Schedule'}
            </span>
          </button>

          <Link
            href={`/course/${course.id}`}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border-2 border-gray-300 dark:border-gray-600 hover:border-indigo-500 dark:hover:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 text-sm font-medium rounded-xl transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <span className="hidden sm:inline">
              {lang === 'zh' ? '查看詳情' : 'View Details'}
            </span>
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
      )}

      {/* Decorative Corner */}
      <div className="absolute -right-6 -top-6 h-20 w-20 bg-gradient-to-br from-indigo-100 to-transparent dark:from-indigo-900/10 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  );
};

export default CourseCard;
