/**
 * Home Page - Course Explorer
 *
 * Main landing page for browsing and searching courses.
 * Features:
 * - Semester selection dropdown
 * - Course search functionality
 * - Department filtering
 * - Paginated course list
 * - Responsive design
 * - Loading and error states
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import {
  Header,
  Footer,
  SemesterSelect,
  SearchInput,
  DepartmentFilter,
  CourseList,
  CourseSkeleton,
  Error,
} from '@/components';
import { useSemesters } from '@/lib/hooks/useSemesters';
import { useCourses } from '@/lib/hooks/useCourses';

const ITEMS_PER_PAGE = 50;

/**
 * Home page component
 */
export default function Home() {
  const router = useRouter();
  const { q: querySearch, dept: queryDept, acy: queryAcy, sem: querySem } = router.query;

  // State for filters
  const [selectedAcy, setSelectedAcy] = useState<number | undefined>(undefined);
  const [selectedSem, setSelectedSem] = useState<number | undefined>(undefined);
  const [selectedDept, setSelectedDept] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Fetch semesters
  const {
    semesters,
    loading: semestersLoading,
    error: semestersError,
  } = useSemesters();

  // Sync URL params to state
  useEffect(() => {
    if (querySearch && typeof querySearch === 'string') {
      setSearchQuery(querySearch);
    }
    if (queryDept && typeof queryDept === 'string') {
      setSelectedDept(queryDept);
    }
    if (queryAcy && typeof queryAcy === 'string') {
      setSelectedAcy(parseInt(queryAcy, 10));
    }
    if (querySem && typeof querySem === 'string') {
      setSelectedSem(parseInt(querySem, 10));
    }
  }, [querySearch, queryDept, queryAcy, querySem]);

  // Fetch courses with filters
  const {
    courses,
    loading: coursesLoading,
    error: coursesError,
    hasMore,
    loadMore,
    totalLoaded,
  } = useCourses(selectedAcy, selectedSem, selectedDept, undefined, searchQuery, {
    enablePagination: true,
    pageSize: ITEMS_PER_PAGE,
  });

  /**
   * Handle semester change
   */
  const handleSemesterChange = (acy: number | undefined, sem: number | undefined) => {
    setSelectedAcy(acy);
    setSelectedSem(sem);

    // Update URL
    const params = new URLSearchParams();
    if (acy) params.set('acy', acy.toString());
    if (sem) params.set('sem', sem.toString());
    if (selectedDept) params.set('dept', selectedDept);
    if (searchQuery) params.set('q', searchQuery);

    router.push(`/?${params.toString()}`, undefined, { shallow: true });
  };

  /**
   * Handle department filter change
   */
  const handleDepartmentChange = (dept: string | undefined) => {
    setSelectedDept(dept);

    // Update URL
    const params = new URLSearchParams();
    if (selectedAcy) params.set('acy', selectedAcy.toString());
    if (selectedSem) params.set('sem', selectedSem.toString());
    if (dept) params.set('dept', dept);
    if (searchQuery) params.set('q', searchQuery);

    router.push(`/?${params.toString()}`, undefined, { shallow: true });
  };

  /**
   * Handle search query change
   */
  const handleSearchChange = (query: string) => {
    setSearchQuery(query);

    // Update URL
    const params = new URLSearchParams();
    if (selectedAcy) params.set('acy', selectedAcy.toString());
    if (selectedSem) params.set('sem', selectedSem.toString());
    if (selectedDept) params.set('dept', selectedDept);
    if (query) params.set('q', query);

    router.push(`/?${params.toString()}`, undefined, { shallow: true });
  };

  /**
   * Handle load more button click
   */
  const handleLoadMore = () => {
    if (!coursesLoading && hasMore) {
      loadMore();
    }
  };

  /**
   * Add course to schedule
   */
  const handleAddToSchedule = (courseId: number) => {
    // Get existing schedule from localStorage
    const schedule = JSON.parse(localStorage.getItem('schedule') || '[]');

    // Check if course is already in schedule
    if (!schedule.includes(courseId)) {
      schedule.push(courseId);
      localStorage.setItem('schedule', JSON.stringify(schedule));

      // Show success message (you can replace this with a toast notification)
      alert('Course added to schedule!');
    } else {
      alert('Course is already in your schedule!');
    }
  };

  return (
    <>
      <Head>
        <title>NYCU Course Platform - Browse Courses</title>
        <meta
          name="description"
          content="Browse and search NYCU courses. Find the perfect courses for your schedule."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />

        <main className="flex-1 container mx-auto px-4 py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
              Course Explorer
            </h1>
            <p className="text-gray-600 text-lg">
              Browse and search courses for NYCU
            </p>
          </div>

          {/* Filters Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="space-y-4">
              {/* Semester Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Semester
                </label>
                {semestersError ? (
                  <Error message="Failed to load semesters" />
                ) : (
                  <SemesterSelect
                    semesters={semesters}
                    loading={semestersLoading}
                    selectedAcy={selectedAcy}
                    selectedSem={selectedSem}
                    onChange={handleSemesterChange}
                  />
                )}
              </div>

              {/* Search Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Courses
                </label>
                <SearchInput
                  value={searchQuery}
                  onChange={handleSearchChange}
                  placeholder="Search by course name or number..."
                />
              </div>

              {/* Department Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Department
                </label>
                <DepartmentFilter
                  value={selectedDept}
                  onChange={handleDepartmentChange}
                />
              </div>
            </div>

            {/* Active Filters Summary */}
            {(selectedAcy || selectedSem || selectedDept || searchQuery) && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex flex-wrap gap-2 items-center">
                  <span className="text-sm text-gray-600 font-medium">Active filters:</span>
                  {selectedAcy && selectedSem && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                      {selectedAcy} - {selectedSem === 1 ? 'Fall' : 'Spring'}
                      <button
                        onClick={() => handleSemesterChange(undefined, undefined)}
                        className="ml-2 hover:text-blue-900"
                        aria-label="Remove semester filter"
                      >
                        &times;
                      </button>
                    </span>
                  )}
                  {selectedDept && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                      {selectedDept}
                      <button
                        onClick={() => handleDepartmentChange(undefined)}
                        className="ml-2 hover:text-green-900"
                        aria-label="Remove department filter"
                      >
                        &times;
                      </button>
                    </span>
                  )}
                  {searchQuery && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800">
                      &quot;{searchQuery}&quot;
                      <button
                        onClick={() => handleSearchChange('')}
                        className="ml-2 hover:text-purple-900"
                        aria-label="Remove search filter"
                      >
                        &times;
                      </button>
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Course List Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            {/* Results Header */}
            {!coursesLoading && !coursesError && (
              <div className="mb-4 pb-4 border-b border-gray-200">
                <p className="text-gray-600">
                  {courses.length === 0 ? (
                    'No courses found'
                  ) : (
                    <>
                      Showing <span className="font-semibold">{totalLoaded}</span> course
                      {totalLoaded !== 1 ? 's' : ''}
                      {hasMore && ' (more available)'}
                    </>
                  )}
                </p>
              </div>
            )}

            {/* Error State */}
            {coursesError && (
              <div className="py-8">
                <Error
                  message="Failed to load courses. Please try again."
                  onRetry={() => window.location.reload()}
                />
              </div>
            )}

            {/* Loading State */}
            {coursesLoading && courses.length === 0 && (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <CourseSkeleton key={i} />
                ))}
              </div>
            )}

            {/* Course List */}
            {!coursesError && courses.length > 0 && (
              <>
                <CourseList
                  courses={courses}
                  onAddToSchedule={handleAddToSchedule}
                />

                {/* Load More Button */}
                {hasMore && (
                  <div className="mt-6 text-center">
                    <button
                      onClick={handleLoadMore}
                      disabled={coursesLoading}
                      className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      {coursesLoading ? (
                        <>
                          <svg
                            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                          </svg>
                          Loading...
                        </>
                      ) : (
                        <>
                          Load More
                          <svg
                            className="ml-2 -mr-1 w-5 h-5"
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
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Loading indicator while fetching more */}
                {coursesLoading && courses.length > 0 && (
                  <div className="mt-6">
                    <CourseSkeleton />
                  </div>
                )}
              </>
            )}

            {/* Empty State */}
            {!coursesLoading && !coursesError && courses.length === 0 && (
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
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  />
                </svg>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No courses found
                </h3>
                <p className="text-gray-500 mb-4">
                  Try adjusting your filters or search query
                </p>
                <button
                  onClick={() => {
                    setSelectedAcy(undefined);
                    setSelectedSem(undefined);
                    setSelectedDept(undefined);
                    setSearchQuery('');
                    router.push('/', undefined, { shallow: true });
                  }}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
