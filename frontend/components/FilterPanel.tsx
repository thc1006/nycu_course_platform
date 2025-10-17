import React from 'react';
import { Search, Filter, ChevronDown, X } from 'lucide-react';
import * as Slider from '@radix-ui/react-slider';
import * as Checkbox from '@radix-ui/react-checkbox';
import * as Select from '@radix-ui/react-select';
import { Check } from 'lucide-react';

interface FilterPanelProps {
  onFilterChange: (filters: FilterState) => void;
  departments?: string[];
  semesters?: { id: number; label: string }[];
}

export interface FilterState {
  semesters: number[];
  departments: string[];
  minCredits: number | null;
  maxCredits: number | null;
  keywords: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  onFilterChange,
  departments = [],
  semesters = [
    { id: 1, label: '112-1' },
    { id: 2, label: '112-2' },
    { id: 3, label: '111-1' },
    { id: 4, label: '111-2' },
    { id: 5, label: '110-1' },
    { id: 6, label: '110-2' },
    { id: 7, label: '109-1' },
    { id: 8, label: '109-2' },
    { id: 9, label: '108-1' },
  ],
}) => {
  const [filters, setFilters] = React.useState<FilterState>({
    semesters: [],
    departments: [],
    minCredits: 0,
    maxCredits: 6,
    keywords: '',
  });

  const [isExpanded, setIsExpanded] = React.useState(true);
  const [searchInput, setSearchInput] = React.useState('');

  const handleSemesterToggle = (semesterId: number) => {
    const newSemesters = filters.semesters.includes(semesterId)
      ? filters.semesters.filter(id => id !== semesterId)
      : [...filters.semesters, semesterId];

    const newFilters = { ...filters, semesters: newSemesters };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleDepartmentChange = (dept: string) => {
    const newDepartments = filters.departments.includes(dept)
      ? filters.departments.filter(d => d !== dept)
      : [...filters.departments, dept];

    const newFilters = { ...filters, departments: newDepartments };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleCreditChange = (values: number[]) => {
    const newFilters = {
      ...filters,
      minCredits: values[0],
      maxCredits: values[1],
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newFilters = { ...filters, keywords: searchInput };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearAllFilters = () => {
    const newFilters: FilterState = {
      semesters: [],
      departments: [],
      minCredits: 0,
      maxCredits: 6,
      keywords: '',
    };
    setFilters(newFilters);
    setSearchInput('');
    onFilterChange(newFilters);
  };

  const hasActiveFilters =
    filters.semesters.length > 0 ||
    filters.departments.length > 0 ||
    filters.keywords !== '' ||
    filters.minCredits !== 0 ||
    filters.maxCredits !== 6;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Filters</h3>
            {hasActiveFilters && (
              <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full">
                Active
              </span>
            )}
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ChevronDown
              className={`h-5 w-5 text-gray-600 dark:text-gray-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Filters Content */}
      <div className={`${isExpanded ? 'block' : 'hidden'}`}>
        <div className="p-4 space-y-6">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Courses
            </label>
            <form onSubmit={handleSearchSubmit} className="relative">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Course name, code, or teacher..."
                className="w-full px-4 py-2 pl-10 pr-4 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </form>
          </div>

          {/* Semesters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Semesters
            </label>
            <div className="grid grid-cols-2 gap-2">
              {semesters.map(semester => (
                <label
                  key={semester.id}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  <Checkbox.Root
                    checked={filters.semesters.includes(semester.id)}
                    onCheckedChange={() => handleSemesterToggle(semester.id)}
                    className="h-4 w-4 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                  >
                    <Checkbox.Indicator className="flex items-center justify-center text-white">
                      <Check className="h-3 w-3" />
                    </Checkbox.Indicator>
                  </Checkbox.Root>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {semester.label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Credits Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Credits Range
            </label>
            <div className="px-1">
              <Slider.Root
                value={[filters.minCredits || 0, filters.maxCredits || 6]}
                onValueChange={handleCreditChange}
                max={6}
                min={0}
                step={1}
                className="relative flex items-center select-none touch-none w-full h-5"
              >
                <Slider.Track className="bg-gray-200 dark:bg-gray-600 relative grow rounded-full h-[3px]">
                  <Slider.Range className="absolute bg-blue-500 rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb
                  className="block w-5 h-5 bg-white dark:bg-gray-200 border-2 border-blue-500 rounded-full hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                  aria-label="Min credits"
                />
                <Slider.Thumb
                  className="block w-5 h-5 bg-white dark:bg-gray-200 border-2 border-blue-500 rounded-full hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                  aria-label="Max credits"
                />
              </Slider.Root>
              <div className="flex justify-between mt-2">
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {filters.minCredits || 0} credits
                </span>
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {filters.maxCredits || 6} credits
                </span>
              </div>
            </div>
          </div>

          {/* Department Select */}
          {departments.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Department
              </label>
              <Select.Root
                value={filters.departments[0] || ''}
                onValueChange={(value) => handleDepartmentChange(value)}
              >
                <Select.Trigger className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors flex items-center justify-between">
                  <Select.Value placeholder="Select department" />
                  <Select.Icon>
                    <ChevronDown className="h-4 w-4" />
                  </Select.Icon>
                </Select.Trigger>

                <Select.Portal>
                  <Select.Content className="overflow-hidden bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
                    <Select.Viewport className="p-1">
                      {departments.map(dept => (
                        <Select.Item
                          key={dept}
                          value={dept}
                          className="relative flex items-center px-8 py-2 text-sm text-gray-900 dark:text-white rounded hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none cursor-pointer"
                        >
                          <Select.ItemText>{dept}</Select.ItemText>
                          <Select.ItemIndicator className="absolute left-2 inline-flex items-center">
                            <Check className="h-4 w-4" />
                          </Select.ItemIndicator>
                        </Select.Item>
                      ))}
                    </Select.Viewport>
                  </Select.Content>
                </Select.Portal>
              </Select.Root>
            </div>
          )}

          {/* Clear Filters Button */}
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-all"
            >
              <X className="h-4 w-4" />
              Clear All Filters
            </button>
          )}
        </div>
      </div>
    </div>
  );
};