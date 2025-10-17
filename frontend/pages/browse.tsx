'use client'

import React, { useState, useEffect } from 'react'
import { useTranslation } from 'next-i18next'
import { serverSideTranslations } from 'next-i18next/serverSideTranslations'
import { Header } from '@/components/Layout/Header'
import { AdvancedFilter } from '@/components/Filters/AdvancedFilter'
import { CourseCard } from '@/components/Course/CourseCard'
import axios from 'axios'

interface Course {
  id: number
  crs_no: string
  name: string
  teacher: string
  credits: number
  dept: string
  time: string
  classroom: string
  acy: number
  sem: number
}

interface FilterState {
  semesters: number[]
  departments: string[]
  minCredits: number | null
  maxCredits: number | null
  keywords: string
}

export default function BrowsePage() {
  const { t } = useTranslation('common')
  const [darkMode, setDarkMode] = useState(false)
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<FilterState>({
    semesters: [],
    departments: [],
    minCredits: null,
    maxCredits: null,
    keywords: '',
  })
  const [total, setTotal] = useState(0)
  const [limit] = useState(12)
  const [offset, setOffset] = useState(0)

  // Load dark mode preference
  useEffect(() => {
    const saved = localStorage.getItem('darkMode')
    if (saved) setDarkMode(JSON.parse(saved))
  }, [])

  // Fetch courses
  useEffect(() => {
    const fetchCourses = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await axios.post(
          'http://localhost:8000/api/advanced/filter',
          {},
          {
            params: {
              semesters: filters.semesters.length > 0 ? filters.semesters : undefined,
              departments: filters.departments.length > 0 ? filters.departments : undefined,
              min_credits: filters.minCredits,
              max_credits: filters.maxCredits,
              keywords: filters.keywords ? [filters.keywords] : undefined,
              limit,
              offset,
            },
          }
        )
        setCourses(response.data.courses)
        setTotal(response.data.total)
      } catch (err) {
        setError('Failed to fetch courses')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchCourses()
  }, [filters, offset, limit])

  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters)
    setOffset(0)
  }

  const handleDarkModeToggle = (enabled: boolean) => {
    setDarkMode(enabled)
    localStorage.setItem('darkMode', JSON.stringify(enabled))
  }

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-white dark:bg-slate-950">
        {/* Header */}
        <Header
          darkMode={darkMode}
          onDarkModeToggle={handleDarkModeToggle}
          onLanguageChange={(lang) => console.log('Language changed to:', lang)}
        />

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar - Filters */}
            <div className="lg:col-span-1">
              <AdvancedFilter onFilterChange={handleFilterChange} />
            </div>

            {/* Main - Courses */}
            <div className="lg:col-span-3">
              {/* Page Title */}
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Available Courses
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Showing {courses.length} of {total} courses
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400">
                  {error}
                </div>
              )}

              {/* Loading State */}
              {loading && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="h-64 bg-gray-200 dark:bg-slate-800 rounded-lg animate-pulse"
                    />
                  ))}
                </div>
              )}

              {/* Course Grid */}
              {!loading && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                  {courses.map(course => (
                    <CourseCard
                      key={course.id}
                      {...course}
                      onAddToSchedule={(id) => console.log('Add to schedule:', id)}
                    />
                  ))}
                </div>
              )}

              {/* Empty State */}
              {!loading && courses.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-600 dark:text-gray-400">
                    No courses found matching your filters
                  </p>
                </div>
              )}

              {/* Pagination */}
              {total > limit && (
                <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-slate-700">
                  <button
                    onClick={() => setOffset(Math.max(0, offset - limit))}
                    disabled={offset === 0}
                    className="px-4 py-2 rounded-lg border border-gray-300 dark:border-slate-600 text-gray-700 dark:text-gray-300 disabled:opacity-50"
                  >
                    ← Previous
                  </button>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit)}
                  </span>
                  <button
                    onClick={() => setOffset(offset + limit)}
                    disabled={offset + limit >= total}
                    className="px-4 py-2 rounded-lg border border-gray-300 dark:border-slate-600 text-gray-700 dark:text-gray-300 disabled:opacity-50"
                  >
                    Next →
                  </button>
                </div>
              )}
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-gray-50 dark:bg-slate-900 border-t border-gray-200 dark:border-slate-700 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 dark:text-gray-400 text-sm">
            <p>NYCU Course Platform • All courses information is up-to-date</p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export async function getStaticProps({ locale }: { locale: string }) {
  return {
    props: {
      ...(await serverSideTranslations(locale, ['common'])),
    },
  }
}
