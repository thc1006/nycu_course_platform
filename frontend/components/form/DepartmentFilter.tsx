/**
 * DepartmentFilter Component
 *
 * Dropdown filter for selecting departments.
 * Features:
 * - List of departments
 * - "All Departments" option
 * - Currently selected department highlight
 * - onChange handler
 * - Badge display for selected department
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <DepartmentFilter
 *   departments={['CS', 'EE', 'MATH']}
 *   value={selectedDept}
 *   onChange={(dept) => setSelectedDept(dept)}
 * />
 * ```
 */

import React, { useCallback } from 'react';

/**
 * Props for the DepartmentFilter component
 */
interface DepartmentFilterProps {
  /** Array of available department codes */
  departments: string[];
  /** Currently selected department (empty string or undefined for "All") */
  value?: string;
  /** Callback when selection changes */
  onChange: (department: string) => void;
  /** Whether the filter is disabled */
  disabled?: boolean;
  /** Optional label text */
  label?: string;
  /** Whether to show the badge */
  showBadge?: boolean;
  /** Optional placeholder for "All Departments" */
  allDepartmentsText?: string;
}

/**
 * Department filter dropdown component
 *
 * @param {DepartmentFilterProps} props - Component props
 * @returns {JSX.Element} The rendered department filter
 */
const DepartmentFilter: React.FC<DepartmentFilterProps> = ({
  departments = [],
  value = '',
  onChange,
  disabled = false,
  label,
  showBadge = true,
  allDepartmentsText = 'All Departments',
}) => {
  /**
   * Handle selection change
   */
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  /**
   * Clear the selected department
   */
  const handleClear = useCallback(() => {
    onChange('');
  }, [onChange]);

  /**
   * Sort departments alphabetically
   */
  const sortedDepartments = [...departments].sort((a, b) => a.localeCompare(b));

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          value={value}
          onChange={handleChange}
          disabled={disabled}
          className={`
            block w-full pl-10 pr-10 py-2.5 text-base border border-gray-300
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            rounded-lg shadow-sm appearance-none bg-white
            transition-colors
            ${disabled ? 'bg-gray-100 cursor-not-allowed text-gray-500' : 'hover:border-gray-400'}
          `}
        >
          <option value="">{allDepartmentsText}</option>
          {sortedDepartments.map((dept) => (
            <option key={dept} value={dept}>
              {dept}
            </option>
          ))}
        </select>

        {/* Department icon */}
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            />
          </svg>
        </div>

        {/* Custom dropdown arrow */}
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Selected department badge */}
      {value && showBadge && (
        <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          </svg>
          {value}
          <button
            onClick={handleClear}
            className="ml-2 hover:text-green-900 focus:outline-none"
            aria-label="Clear filter"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Helper text */}
      {value && (
        <p className="mt-1 text-xs text-gray-500">
          Filtering by {value} department
        </p>
      )}
    </div>
  );
};

/**
 * Compact variant of DepartmentFilter for inline use
 */
export const CompactDepartmentFilter: React.FC<DepartmentFilterProps> = ({
  departments = [],
  value = '',
  onChange,
  disabled = false,
  allDepartmentsText = 'All Depts',
}) => {
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  const sortedDepartments = [...(departments || [])].sort((a, b) => a.localeCompare(b));

  return (
    <div className="relative inline-block">
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-2.5 text-gray-400">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
          />
        </svg>
      </div>
      <select
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className="pl-9 pr-8 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
      >
        <option value="">{allDepartmentsText}</option>
        {sortedDepartments.map((dept) => (
          <option key={dept} value={dept}>
            {dept}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2 text-gray-400">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
};

/**
 * Multi-select variant for selecting multiple departments
 */
export const MultiDepartmentFilter: React.FC<{
  departments?: string[];
  value?: string[];
  onChange: (departments: string[]) => void;
  label?: string;
}> = ({ departments = [], value = [], onChange, label }) => {
  const toggleDepartment = useCallback(
    (dept: string) => {
      if (value.includes(dept)) {
        onChange(value.filter((d) => d !== dept));
      } else {
        onChange([...value, dept]);
      }
    },
    [value, onChange]
  );

  const handleClearAll = useCallback(() => {
    onChange([]);
  }, [onChange]);

  const sortedDepartments = [...(departments || [])].sort((a, b) => a.localeCompare(b));

  return (
    <div className="w-full">
      {label && (
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">{label}</label>
          {value.length > 0 && (
            <button
              onClick={handleClearAll}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Clear all
            </button>
          )}
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        {sortedDepartments.map((dept) => {
          const isSelected = value.includes(dept);
          return (
            <button
              key={dept}
              onClick={() => toggleDepartment(dept)}
              className={`
                px-3 py-1.5 text-sm font-medium rounded-full transition-colors
                ${
                  isSelected
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              {dept}
              {isSelected && (
                <span className="ml-1.5">✓</span>
              )}
            </button>
          );
        })}
      </div>
      {value.length > 0 && (
        <p className="mt-2 text-xs text-gray-500">
          {value.length} {value.length === 1 ? 'department' : 'departments'} selected
        </p>
      )}
    </div>
  );
};

export default DepartmentFilter;
