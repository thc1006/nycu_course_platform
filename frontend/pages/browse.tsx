import React, { useState, useEffect, useCallback, useRef, useTransition, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { useTranslation } from 'next-i18next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import Header from '../components/common/Header';
import { ChevronLeft, ChevronRight, Loader2, Filter, X } from 'lucide-react';
import axios from 'axios';
import useSWR from 'swr';
import { FixedSizeGrid as Grid } from 'react-window';

// Dynamic imports for code splitting
const FilterPanel = dynamic<any>(() => import('../components/FilterPanel').then(mod => mod.FilterPanel), {
  loading: () => <div className="h-64 skeleton rounded-xl" />,
  ssr: false,
});

const CourseCard = dynamic(() => import('../components/course/CourseCard'), {
  loading: () => <div className="h-72 skeleton rounded-xl" />,
  ssr: true,
});

// Import FilterState type separately for type safety
interface FilterState {
  semesters: number[];
  departments: string[];
  minCredits: number | null;
  maxCredits: number | null;
  keywords: string;
}

interface Course {
  id: number;
  crs_no: string;
  name: string;
  teacher: string;
  credits: number;
  dept: string;
  time: string;
  classroom: string;
  acy: number;
  sem: number;
}

// SWR fetcher function for POST requests
const fetcher = async (url: string, params: any) => {
  const response = await axios.post(url, {}, {
    params,
    timeout: 10000,
  });
  return response.data;
};

export default function BrowsePage() {
  const { t } = useTranslation('common');
  const [isPending, startTransition] = useTransition();
  const [filters, setFilters] = useState<FilterState>({
    semesters: [],
    departments: [],
    minCredits: null,
    maxCredits: null,
    keywords: '',
  });
  const [limit] = useState(12);
  const [offset, setOffset] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [debouncedFilters, setDebouncedFilters] = useState(filters);
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState(searchQuery);
  const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });

  // Track window size for responsive grid
  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    // Set initial size
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Debounce filters and search query (500ms delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
      setDebouncedSearchQuery(searchQuery);
    }, 500);

    return () => clearTimeout(timer);
  }, [filters, searchQuery]);

  // Build API parameters from filters
  const apiParams = useMemo(() => {
    const params: any = {
      limit,
      offset,
    };

    if (debouncedFilters.semesters.length > 0) {
      params.semesters = debouncedFilters.semesters;
    }
    if (debouncedFilters.departments.length > 0) {
      params.departments = debouncedFilters.departments;
    }
    if (debouncedFilters.minCredits !== null) {
      params.min_credits = debouncedFilters.minCredits;
    }
    if (debouncedFilters.maxCredits !== null) {
      params.max_credits = debouncedFilters.maxCredits;
    }
    if (debouncedFilters.keywords || debouncedSearchQuery) {
      params.keywords = [debouncedFilters.keywords || debouncedSearchQuery].filter(Boolean);
    }

    return params;
  }, [debouncedFilters, debouncedSearchQuery, limit, offset]);

  // Use SWR for data fetching with caching
  const { data, error, isLoading, isValidating } = useSWR(
    ['/api/advanced/filter', apiParams],
    ([url, params]) => fetcher(url, params),
    {
      revalidateOnFocus: false,      // Don't refetch on window focus
      revalidateOnReconnect: false,  // Don't refetch on reconnect
      dedupingInterval: 60000,       // Dedupe requests within 60 seconds
      keepPreviousData: true,        // Keep previous data while loading new data
    }
  );

  const courses = data?.courses || [];
  const total = data?.total || 0;

  // Calculate grid layout for virtual scrolling
  const gridConfig = useMemo(() => {
    // Tailwind breakpoints: sm: 640px, md: 768px, lg: 1024px, xl: 1280px
    let columnCount = 1;
    if (windowSize.width >= 1280) {
      columnCount = 3; // xl: 3 columns
    } else if (windowSize.width >= 768) {
      columnCount = 2; // md: 2 columns
    }

    const columnWidth = Math.floor((windowSize.width - 64) / columnCount); // 64px for padding
    const rowHeight = 350; // Course card height
    const rowCount = Math.ceil(courses.length / columnCount);

    return {
      columnCount,
      columnWidth,
      rowHeight,
      rowCount,
    };
  }, [windowSize.width, courses.length]);

  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    setOffset(0);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setOffset(0);
  };

  const handleAddToSchedule = useCallback((courseId: number) => {
    const savedSchedule = localStorage.getItem('schedule');
    const schedule = savedSchedule ? JSON.parse(savedSchedule) : [];
    if (!schedule.includes(courseId)) {
      schedule.push(courseId);
      localStorage.setItem('schedule', JSON.stringify(schedule));
    }
  }, []);

  // Virtual grid cell renderer
  const Cell = useCallback(({ columnIndex, rowIndex, style }: any) => {
    const courseIndex = rowIndex * gridConfig.columnCount + columnIndex;

    // Return empty cell if no course at this index
    if (courseIndex >= courses.length) {
      return null;
    }

    const course = courses[courseIndex];

    return (
      <div style={style} className="p-3">
        <CourseCard
          course={course}
          onAddSchedule={handleAddToSchedule}
        />
      </div>
    );
  }, [courses, gridConfig.columnCount, handleAddToSchedule]);

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  const goToPage = (page: number) => {
    setOffset((page - 1) * limit);
  };

  const renderPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => goToPage(i)}
          className={`
            px-3 py-1 rounded-xl text-sm font-medium transition-all
            ${
              i === currentPage
                ? 'bg-indigo-500 text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            }
          `}
        >
          {i}
        </button>
      );
    }

    return pages;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onSearch={handleSearch} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mobile Filter Toggle Button */}
        <button
          onClick={() => setShowMobileFilters(!showMobileFilters)}
          className="lg:hidden fixed bottom-6 right-6 z-40 flex items-center gap-2 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg transition-all transform hover:scale-105 active:scale-95"
        >
          {showMobileFilters ? (
            <>
              <X className="h-5 w-5" />
              <span className="font-medium">關閉篩選</span>
            </>
          ) : (
            <>
              <Filter className="h-5 w-5" />
              <span className="font-medium">篩選課程</span>
            </>
          )}
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Filters */}
          {/* Desktop: Always visible, Mobile: Overlay modal */}
          <div className={`
            lg:col-span-1
            ${showMobileFilters ? 'fixed' : 'hidden'}
            lg:block
            inset-0 lg:relative
            z-30 lg:z-auto
            ${showMobileFilters ? 'bg-black/50' : ''}
            lg:bg-transparent
          `}
          onClick={(e) => {
            // Close on backdrop click (mobile only)
            if (e.target === e.currentTarget && showMobileFilters) {
              setShowMobileFilters(false);
            }
          }}
          >
            <div className={`
              ${showMobileFilters ? 'absolute' : 'hidden'}
              lg:relative lg:block
              ${showMobileFilters ? 'left-0 top-0 bottom-0 w-80 max-w-[85vw]' : ''}
              bg-gray-50 dark:bg-gray-900 lg:bg-transparent
              overflow-y-auto
              lg:sticky lg:top-24
              p-4 lg:p-0
              shadow-xl lg:shadow-none
              transform transition-transform duration-300
              ${showMobileFilters ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            `}>
              <div className="lg:hidden flex items-center justify-between mb-4 pb-4 border-b border-gray-300 dark:border-gray-700">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">篩選課程</h2>
                <button
                  onClick={() => setShowMobileFilters(false)}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>
              <FilterPanel onFilterChange={(filters) => {
                handleFilterChange(filters);
                // Auto-close mobile filters after applying
                if (showMobileFilters) {
                  setShowMobileFilters(false);
                }
              }} />
            </div>
          </div>

          {/* Main - Courses */}
          <div className="lg:col-span-3">
            {/* Page Header */}
            <div className="mb-6 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                課程目錄
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {isLoading || isValidating ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    {isLoading ? '搜尋課程中...' : '更新中...'}
                  </span>
                ) : (
                  <>
                    顯示 {courses.length > 0 ? `${offset + 1}-${Math.min(offset + limit, total)}` : '0'} / 共 {total.toLocaleString()} 門課程
                  </>
                )}
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                <p className="text-red-700 dark:text-red-400">載入課程失敗</p>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div
                    key={i}
                    className="h-72 skeleton rounded-xl animate-fade-in"
                    style={{ animationDelay: `${i * 0.1}s` }}
                  />
                ))}
              </div>
            )}

            {/* Course Grid - Virtual Scrolling */}
            {!isLoading && courses.length > 0 && gridConfig.rowCount > 0 && (
              <div className={`mb-8 transition-opacity duration-300 ${isValidating ? 'opacity-60' : 'opacity-100'}`}>
                <Grid
                  columnCount={gridConfig.columnCount}
                  columnWidth={gridConfig.columnWidth}
                  height={Math.min(gridConfig.rowHeight * gridConfig.rowCount, 1200)} // Max height 1200px
                  rowCount={gridConfig.rowCount}
                  rowHeight={gridConfig.rowHeight}
                  width={windowSize.width >= 1024 ? windowSize.width * 0.75 - 64 : windowSize.width - 64} // Adjust for layout
                  style={{
                    overflowX: 'hidden',
                  }}
                >
                  {Cell}
                </Grid>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && courses.length === 0 && !error && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-200 dark:border-gray-700">
                <div className="mb-4">
                  <svg
                    className="w-16 h-16 mx-auto text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  找不到課程
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  請嘗試調整篩選條件或搜尋關鍵字
                </p>
              </div>
            )}

            {/* Pagination */}
            {total > limit && (
              <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => goToPage(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    上一頁
                  </button>

                  <div className="hidden sm:flex items-center gap-2">
                    {currentPage > 3 && (
                      <>
                        <button
                          onClick={() => goToPage(1)}
                          className="px-3 py-1 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
                        >
                          1
                        </button>
                        {currentPage > 4 && (
                          <span className="text-gray-500 dark:text-gray-400">...</span>
                        )}
                      </>
                    )}

                    {renderPageNumbers()}

                    {currentPage < totalPages - 2 && (
                      <>
                        {currentPage < totalPages - 3 && (
                          <span className="text-gray-500 dark:text-gray-400">...</span>
                        )}
                        <button
                          onClick={() => goToPage(totalPages)}
                          className="px-3 py-1 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
                        >
                          {totalPages}
                        </button>
                      </>
                    )}
                  </div>

                  <span className="sm:hidden text-sm text-gray-600 dark:text-gray-400">
                    第 {currentPage} 頁 / 共 {totalPages} 頁
                  </span>

                  <button
                    onClick={() => goToPage(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    下一頁
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            東華選課系統 • 共 {total.toLocaleString()} 門課程
          </p>
        </div>
      </footer>
    </div>
  );
}

export async function getStaticProps({ locale }: { locale: string }) {
  try {
    const translations = await serverSideTranslations(locale, ['common', 'home', 'course', 'schedule', 'error']);
    return {
      props: {
        ...translations,
      },
      revalidate: 3600, // ISR: Revalidate every hour
    };
  } catch (error) {
    console.error('Error in getStaticProps:', error);
    return {
      notFound: true,
      revalidate: 60, // Try again after 1 minute on error
    };
  }
}