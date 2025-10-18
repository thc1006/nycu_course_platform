/**
 * Advanced Filters Component
 *
 * Provides comprehensive filtering options for courses including:
 * - Department filter
 * - Teacher filter
 * - Time slot filter (weekdays and periods)
 * - Course type (required/elective)
 * - Credits filter
 */

import React, { useState, useEffect } from 'react';
import { Filter, X, ChevronDown } from 'lucide-react';

interface AdvancedFiltersProps {
  courses: Course[];
  onFilterChange: (filters: FilterOptions) => void;
  initialFilters?: FilterOptions;
}

interface Course {
  id: number;
  crs_no: string;
  name: string;
  teacher?: string;
  credits?: number;
  dept?: string;
  college?: string;
  day_codes?: string;
  time_codes?: string;
  required?: string;
}

export interface FilterOptions {
  departments: string[];
  teachers: string[];
  days: string[];
  timeSlots: string[];
  courseTypes: string[];
  credits: number[];
}

const WEEKDAYS = [
  { code: 'M', label: '星期一' },
  { code: 'T', label: '星期二' },
  { code: 'W', label: '星期三' },
  { code: 'R', label: '星期四' },
  { code: 'F', label: '星期五' },
  { code: 'S', label: '星期六' },
  { code: 'U', label: '星期日' },
];

const TIME_PERIODS = [
  { value: '1-4', label: '上午 (1-4節)' },
  { value: '5-8', label: '下午 (5-8節)' },
  { value: '9-12', label: '晚上 (9-12節)' },
];

export default function AdvancedFilters({ courses, onFilterChange, initialFilters }: AdvancedFiltersProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    department: true,
    teacher: false,
    time: false,
    type: false,
  });

  const [filters, setFilters] = useState<FilterOptions>(
    initialFilters || {
      departments: [],
      teachers: [],
      days: [],
      timeSlots: [],
      courseTypes: [],
      credits: [],
    }
  );

  // Extract unique values from courses
  const uniqueDepartments = React.useMemo(() => {
    const depts = new Set(courses.map(c => c.dept).filter(Boolean));
    return Array.from(depts).sort();
  }, [courses]);

  const uniqueTeachers = React.useMemo(() => {
    const teachers = new Set(courses.map(c => c.teacher).filter(Boolean));
    return Array.from(teachers).sort();
  }, [courses]);

  const uniqueCredits = React.useMemo(() => {
    const credits = new Set(courses.map(c => c.credits).filter(Boolean));
    return Array.from(credits).sort((a, b) => a! - b!);
  }, [courses]);

  // Handle filter changes
  const handleArrayFilterToggle = (
    filterType: keyof FilterOptions,
    value: string | number
  ) => {
    const currentFilter = filters[filterType] as any[];
    const newFilter = currentFilter.includes(value)
      ? currentFilter.filter(item => item !== value)
      : [...currentFilter, value];

    const updatedFilters = { ...filters, [filterType]: newFilter };
    setFilters(updatedFilters);
    onFilterChange(updatedFilters);
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const clearAllFilters = () => {
    const emptyFilters: FilterOptions = {
      departments: [],
      teachers: [],
      days: [],
      timeSlots: [],
      courseTypes: [],
      credits: [],
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const activeFilterCount = React.useMemo(() => {
    return (
      filters.departments.length +
      filters.teachers.length +
      filters.days.length +
      filters.timeSlots.length +
      filters.courseTypes.length +
      filters.credits.length
    );
  }, [filters]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition"
      >
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <span className="font-semibold text-gray-900 dark:text-white">進階篩選</span>
          {activeFilterCount > 0 && (
            <span className="ml-2 px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 text-xs font-bold rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>
        <ChevronDown
          className={`w-5 h-5 text-gray-500 transition-transform ${
            showFilters ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Filter Content */}
      {showFilters && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 space-y-4 max-h-[600px] overflow-y-auto">
          {/* Clear All Button */}
          {activeFilterCount > 0 && (
            <button
              onClick={clearAllFilters}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
            >
              <X className="w-4 h-4" />
              清除所有篩選 ({activeFilterCount})
            </button>
          )}

          {/* Department Filter */}
          {uniqueDepartments.length > 0 && (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('department')}
                className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                <span className="font-medium text-sm text-gray-900 dark:text-white">
                  系所篩選 {filters.departments.length > 0 && `(${filters.departments.length})`}
                </span>
                <ChevronDown
                  className={`w-4 h-4 transition-transform ${
                    expandedSections.department ? 'rotate-180' : ''
                  }`}
                />
              </button>
              {expandedSections.department && (
                <div className="p-3 space-y-1 max-h-64 overflow-y-auto">
                  {uniqueDepartments.map(dept => (
                    <label
                      key={dept}
                      className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer transition"
                    >
                      <input
                        type="checkbox"
                        checked={filters.departments.includes(dept)}
                        onChange={() => handleArrayFilterToggle('departments', dept)}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300 flex-1 truncate">
                        {dept}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {courses.filter(c => c.dept === dept).length}
                      </span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Teacher Filter */}
          {uniqueTeachers.length > 0 && (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('teacher')}
                className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                <span className="font-medium text-sm text-gray-900 dark:text-white">
                  教師篩選 {filters.teachers.length > 0 && `(${filters.teachers.length})`}
                </span>
                <ChevronDown
                  className={`w-4 h-4 transition-transform ${
                    expandedSections.teacher ? 'rotate-180' : ''
                  }`}
                />
              </button>
              {expandedSections.teacher && (
                <div className="p-3 space-y-1 max-h-64 overflow-y-auto">
                  {uniqueTeachers.slice(0, 50).map(teacher => (
                    <label
                      key={teacher}
                      className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer transition"
                    >
                      <input
                        type="checkbox"
                        checked={filters.teachers.includes(teacher)}
                        onChange={() => handleArrayFilterToggle('teachers', teacher)}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300 flex-1 truncate">
                        {teacher}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {courses.filter(c => c.teacher === teacher).length}
                      </span>
                    </label>
                  ))}
                  {uniqueTeachers.length > 50 && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 text-center p-2">
                      顯示前50位教師，使用搜尋框尋找更多
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Time Slot Filter */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('time')}
              className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >
              <span className="font-medium text-sm text-gray-900 dark:text-white">
                時段篩選{' '}
                {(filters.days.length > 0 || filters.timeSlots.length > 0) &&
                  `(${filters.days.length + filters.timeSlots.length})`}
              </span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${
                  expandedSections.time ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.time && (
              <div className="p-3 space-y-3">
                {/* Weekdays */}
                <div>
                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">星期</p>
                  <div className="flex flex-wrap gap-2">
                    {WEEKDAYS.map(day => (
                      <button
                        key={day.code}
                        onClick={() => handleArrayFilterToggle('days', day.code)}
                        className={`px-3 py-1.5 text-sm font-medium rounded-lg transition ${
                          filters.days.includes(day.code)
                            ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {day.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Time Periods */}
                <div>
                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">時間</p>
                  <div className="space-y-1">
                    {TIME_PERIODS.map(period => (
                      <label
                        key={period.value}
                        className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer transition"
                      >
                        <input
                          type="checkbox"
                          checked={filters.timeSlots.includes(period.value)}
                          onChange={() => handleArrayFilterToggle('timeSlots', period.value)}
                          className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {period.label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Course Type Filter */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('type')}
              className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >
              <span className="font-medium text-sm text-gray-900 dark:text-white">
                課程類型 {filters.courseTypes.length > 0 && `(${filters.courseTypes.length})`}
              </span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${
                  expandedSections.type ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.type && (
              <div className="p-3 space-y-1">
                <label className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer transition">
                  <input
                    type="checkbox"
                    checked={filters.courseTypes.includes('必修')}
                    onChange={() => handleArrayFilterToggle('courseTypes', '必修')}
                    className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">必修</span>
                </label>
                <label className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer transition">
                  <input
                    type="checkbox"
                    checked={filters.courseTypes.includes('選修')}
                    onChange={() => handleArrayFilterToggle('courseTypes', '選修')}
                    className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">選修</span>
                </label>
              </div>
            )}
          </div>

          {/* Credits Filter */}
          {uniqueCredits.length > 0 && (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
              <p className="font-medium text-sm text-gray-900 dark:text-white mb-2">
                學分 {filters.credits.length > 0 && `(${filters.credits.length})`}
              </p>
              <div className="flex flex-wrap gap-2">
                {uniqueCredits.map(credit => (
                  <button
                    key={credit}
                    onClick={() => handleArrayFilterToggle('credits', credit!)}
                    className={`px-3 py-1.5 text-sm font-medium rounded-lg transition ${
                      filters.credits.includes(credit!)
                        ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {credit} 學分
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
