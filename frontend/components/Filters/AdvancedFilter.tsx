'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'

interface FilterState {
  semesters: number[]
  departments: string[]
  minCredits: number | null
  maxCredits: number | null
  keywords: string
}

interface AdvancedFilterProps {
  onFilterChange: (filters: FilterState) => void
  semesters?: Array<{ year: number; sem: number }>
  departments?: string[]
}

const DEPARTMENTS = [
  'CS', 'EE', 'MATH', 'PHYS', 'CHEM', 'BIO',
  'ENG', 'ECON', 'PSYCH', 'HIST', 'ART', 'MUS'
]

const CREDIT_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

export function AdvancedFilter({ onFilterChange, semesters = [], departments = DEPARTMENTS }: AdvancedFilterProps) {
  const [filters, setFilters] = useState<FilterState>({
    semesters: [],
    departments: [],
    minCredits: null,
    maxCredits: null,
    keywords: '',
  })

  const [isExpanded, setIsExpanded] = useState(true)

  const handleSemesterToggle = (semId: number) => {
    setFilters(prev => {
      const newSems = prev.semesters.includes(semId)
        ? prev.semesters.filter(s => s !== semId)
        : [...prev.semesters, semId]
      return { ...prev, semesters: newSems }
    })
  }

  const handleDepartmentToggle = (dept: string) => {
    setFilters(prev => {
      const newDepts = prev.departments.includes(dept)
        ? prev.departments.filter(d => d !== dept)
        : [...prev.departments, dept]
      return { ...prev, departments: newDepts }
    })
  }

  const handleCreditsChange = (type: 'min' | 'max', value: number | null) => {
    setFilters(prev => ({
      ...prev,
      [type === 'min' ? 'minCredits' : 'maxCredits']: value,
    }))
  }

  const handleKeywordsChange = (keywords: string) => {
    setFilters(prev => ({ ...prev, keywords }))
  }

  const handleApply = () => {
    onFilterChange(filters)
  }

  const handleClear = () => {
    setFilters({
      semesters: [],
      departments: [],
      minCredits: null,
      maxCredits: null,
      keywords: '',
    })
  }

  const activeFilterCount =
    filters.semesters.length +
    filters.departments.length +
    (filters.minCredits ? 1 : 0) +
    (filters.maxCredits ? 1 : 0) +
    (filters.keywords ? 1 : 0)

  return (
    <div className="bg-white dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-gray-900 dark:text-white">🔍 Filters</span>
          {activeFilterCount > 0 && (
            <span className="bg-blue-600 text-white px-2 py-1 rounded-full text-xs font-bold">
              {activeFilterCount}
            </span>
          )}
        </div>
        <span className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}>▼</span>
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="p-4 space-y-5 border-t border-gray-200 dark:border-slate-700">

          {/* Semesters */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Semesters
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[110, 111, 112, 113, 114].map(year => (
                <div key={`${year}-1`} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={`sem-${year}-1`}
                    checked={filters.semesters.includes(year * 10 + 1)}
                    onChange={() => handleSemesterToggle(year * 10 + 1)}
                    className="w-4 h-4 rounded cursor-pointer"
                  />
                  <label htmlFor={`sem-${year}-1`} className="text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                    {year}-1
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Departments */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Departments
            </label>
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
              {departments.map(dept => (
                <div key={dept} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={`dept-${dept}`}
                    checked={filters.departments.includes(dept)}
                    onChange={() => handleDepartmentToggle(dept)}
                    className="w-4 h-4 rounded cursor-pointer"
                  />
                  <label htmlFor={`dept-${dept}`} className="text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                    {dept}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Credits */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Credits
            </label>
            <div className="flex gap-3">
              <div className="flex-1">
                <select
                  value={filters.minCredits ?? ''}
                  onChange={(e) => handleCreditsChange('min', e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-3 py-2 rounded border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white"
                >
                  <option value="">Min</option>
                  {CREDIT_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="flex-1">
                <select
                  value={filters.maxCredits ?? ''}
                  onChange={(e) => handleCreditsChange('max', e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-3 py-2 rounded border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white"
                >
                  <option value="">Max</option>
                  {CREDIT_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Keywords */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Keywords
            </label>
            <input
              type="text"
              placeholder="Search by course name..."
              value={filters.keywords}
              onChange={(e) => handleKeywordsChange(e.target.value)}
              className="w-full px-3 py-2 rounded border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-3 border-t border-gray-200 dark:border-slate-700">
            <Button onClick={handleApply} variant="default" className="flex-1">
              Apply Filters
            </Button>
            <Button onClick={handleClear} variant="outline" className="flex-1">
              Clear
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
