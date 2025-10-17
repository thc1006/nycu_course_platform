/**
 * SemesterSelect Component
 *
 * Dropdown selector for academic semesters.
 * Features:
 * - List of available semesters
 * - Highlight currently selected semester
 * - onChange handler for selection
 * - Displays academic year and semester type (Fall/Spring)
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <SemesterSelect
 *   semesters={semesters}
 *   value={selectedSemester}
 *   onChange={(semester) => setSelectedSemester(semester)}
 * />
 * ```
 */

import React, { useCallback } from 'react';
import { Semester } from '../../lib/types';

/**
 * Props for the SemesterSelect component
 */
interface SemesterSelectProps {
  /** Array of available semesters */
  semesters: Semester[];
  /** Currently selected semester (optional) */
  value?: Semester | null;
  /** Callback when selection changes */
  onChange: (semester: Semester | null) => void;
  /** Whether the select is disabled */
  disabled?: boolean;
  /** Optional placeholder text */
  placeholder?: string;
  /** Optional label text */
  label?: string;
  /** Whether to show a "clear" option */
  allowClear?: boolean;
}

/**
 * Semester selector dropdown component
 *
 * @param {SemesterSelectProps} props - Component props
 * @returns {JSX.Element} The rendered semester select
 */
const SemesterSelect: React.FC<SemesterSelectProps> = ({
  semesters,
  value,
  onChange,
  disabled = false,
  placeholder = 'Choose a semester...',
  label,
  allowClear = true,
}) => {
  /**
   * Format semester for display
   */
  const formatSemester = useCallback((semester: Semester): string => {
    return `${semester.acy} ${semester.sem === 1 ? 'Fall' : 'Spring'}`;
  }, []);

  /**
   * Get unique key for semester
   */
  const getSemesterKey = useCallback((semester: Semester): string => {
    return `${semester.acy}-${semester.sem}`;
  }, []);

  /**
   * Handle selection change
   */
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const selectedValue = e.target.value;

      if (!selectedValue || selectedValue === '') {
        onChange(null);
        return;
      }

      const [acyStr, semStr] = selectedValue.split('-');
      const selectedSemester = semesters.find(
        (s) => s.acy === parseInt(acyStr, 10) && s.sem === parseInt(semStr, 10)
      );

      onChange(selectedSemester || null);
    },
    [semesters, onChange]
  );

  /**
   * Get current selected value
   */
  const selectedValue = value ? getSemesterKey(value) : '';

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          value={selectedValue}
          onChange={handleChange}
          disabled={disabled}
          className={`
            block w-full pl-4 pr-10 py-2.5 text-base border border-gray-300
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            rounded-lg shadow-sm appearance-none bg-white
            transition-colors
            ${disabled ? 'bg-gray-100 cursor-not-allowed text-gray-500' : 'hover:border-gray-400'}
          `}
        >
          <option value="">{placeholder}</option>
          {semesters.map((semester) => (
            <option key={getSemesterKey(semester)} value={getSemesterKey(semester)}>
              {formatSemester(semester)}
            </option>
          ))}
        </select>

        {/* Custom dropdown arrow */}
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Selected semester badge */}
      {value && allowClear && (
        <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          {formatSemester(value)}
          <button
            onClick={() => onChange(null)}
            className="ml-2 hover:text-blue-900 focus:outline-none"
            aria-label="Clear selection"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

/**
 * Compact variant of SemesterSelect for inline use
 */
export const CompactSemesterSelect: React.FC<SemesterSelectProps> = ({
  semesters,
  value,
  onChange,
  disabled = false,
  placeholder = 'Semester',
}) => {
  const formatSemester = useCallback((semester: Semester): string => {
    return `${semester.acy} ${semester.sem === 1 ? 'Fall' : 'Spring'}`;
  }, []);

  const getSemesterKey = useCallback((semester: Semester): string => {
    return `${semester.acy}-${semester.sem}`;
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const selectedValue = e.target.value;
      if (!selectedValue) {
        onChange(null);
        return;
      }
      const [acyStr, semStr] = selectedValue.split('-');
      const selectedSemester = semesters.find(
        (s) => s.acy === parseInt(acyStr, 10) && s.sem === parseInt(semStr, 10)
      );
      onChange(selectedSemester || null);
    },
    [semesters, onChange]
  );

  const selectedValue = value ? getSemesterKey(value) : '';

  return (
    <div className="relative inline-block">
      <select
        value={selectedValue}
        onChange={handleChange}
        disabled={disabled}
        className="pl-3 pr-8 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
      >
        <option value="">{placeholder}</option>
        {semesters.map((semester) => (
          <option key={getSemesterKey(semester)} value={getSemesterKey(semester)}>
            {formatSemester(semester)}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
};

export default SemesterSelect;
