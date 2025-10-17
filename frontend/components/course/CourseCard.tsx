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

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';
import { formatSchedule } from '@/utils/scheduleParser';
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

  // Format schedule
  const schedule = formatSchedule(
    course.day_codes,
    course.time_codes,
    course.classroom_codes,
    lang === 'zh' ? 'zh' : 'en'
  );

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
      className={`group relative overflow-hidden rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all hover:shadow-md hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600 ${className}`}
    >
      {/* Header with Code and Status */}
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <code className="inline-block text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded mb-1">
            {course.crs_no}
          </code>
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 leading-snug break-words">
            {course.name}
          </h3>
        </div>

        {course.required !== undefined && (
          <span
            className={`flex-shrink-0 text-xs font-semibold px-2 py-1 rounded whitespace-nowrap ${
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
      </div>

      {/* Syllabus Indicator */}
      {hasSyllabus && (
        <div className="mb-4 flex items-center gap-2 p-2 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded border border-blue-100 dark:border-blue-800">
          <BookOpen className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
          <span className="text-xs text-blue-700 dark:text-blue-300 font-medium">
            {lang === 'zh' ? '有課程綱要' : 'Has outline'}
          </span>
        </div>
      )}

      {/* Action Buttons */}
      {showActions && (
        <div className="flex gap-2">
          <button
            onClick={handleAddSchedule}
            disabled={isAdding}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 text-white text-sm font-medium rounded transition-all duration-200 transform hover:scale-105 active:scale-95"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">
              {lang === 'zh' ? '加入課表' : 'Add'}
            </span>
          </button>

          <Link
            href={`/course/${course.id}`}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 text-sm font-medium rounded transition-all duration-200"
          >
            <span className="hidden sm:inline">
              {lang === 'zh' ? '詳情' : 'Details'}
            </span>
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
      )}

      {/* Decorative Corner */}
      <div className="absolute -right-6 -top-6 h-20 w-20 bg-gradient-to-br from-blue-100 to-transparent dark:from-blue-900/10 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  );
};

export default CourseCard;
