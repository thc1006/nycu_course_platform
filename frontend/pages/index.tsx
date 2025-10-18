import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useTranslation } from 'next-i18next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { ChevronDown, Grid3x3, List, Filter, Search } from 'lucide-react';
import CourseCard from '@/components/course/CourseCard';
import AdvancedFilters, { FilterOptions } from '@/components/course/AdvancedFilters';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '';

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
  classroom_codes?: string;
  required?: string;
  syllabus?: string;
  syllabus_zh?: string;
  acy?: number;
  sem?: number;
}

interface Semester {
  label: string;
  value: string;
  acy: number;
  sem: number;
}

interface CollegeFilter {
  name: string;
  count: number;
}

export default function HomePage() {
  const { t } = useTranslation(['common', 'home']);
  const router = useRouter();
  const lang = (router.locale || 'zh') as 'en' | 'zh';

  // State
  const [selectedSemesters, setSelectedSemesters] = useState<string[]>([]);
  const [showSemesterDropdown, setShowSemesterDropdown] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCollege, setSelectedCollege] = useState<string>('全部');
  const [collegeFilters, setCollegeFilters] = useState<CollegeFilter[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [advancedFilters, setAdvancedFilters] = useState<FilterOptions>({
    departments: [],
    teachers: [],
    days: [],
    timeSlots: [],
    courseTypes: [],
    credits: [],
  });

  // Initialize semester selection from URL query params on mount and when URL changes
  useEffect(() => {
    if (!router.isReady) return;

    const { semesters: semestersParam } = router.query;
    if (semestersParam) {
      const semesterValues = Array.isArray(semestersParam) ? semestersParam : [semestersParam];
      // Only update if different from current selection
      if (JSON.stringify(semesterValues) !== JSON.stringify(selectedSemesters)) {
        setSelectedSemesters(semesterValues);
        loadCourses(semesterValues);
      }
    }
  }, [router.isReady, router.query.semesters]);

  // Available semesters
  const semesters: Semester[] = [
    { label: '114-1', value: '114-1', acy: 114, sem: 1 },
    { label: '113-2', value: '113-2', acy: 113, sem: 2 },
    { label: '113-1', value: '113-1', acy: 113, sem: 1 },
    { label: '112-2', value: '112-2', acy: 112, sem: 2 },
    { label: '112-1', value: '112-1', acy: 112, sem: 1 },
    { label: '111-2', value: '111-2', acy: 111, sem: 2 },
    { label: '111-1', value: '111-1', acy: 111, sem: 1 },
    { label: '110-2', value: '110-2', acy: 110, sem: 2 },
    { label: '110-1', value: '110-1', acy: 110, sem: 1 },
  ];

  // Toggle semester selection
  const toggleSemester = async (value: string) => {
    let newSelected: string[];
    if (selectedSemesters.includes(value)) {
      newSelected = selectedSemesters.filter(s => s !== value);
    } else {
      newSelected = [...selectedSemesters, value];
    }
    setSelectedSemesters(newSelected);

    // Update URL with semester selection (preserves state on navigation)
    if (newSelected.length > 0) {
      router.push(
        {
          pathname: '/',
          query: { semesters: newSelected },
        },
        undefined,
        { shallow: true } // Don't trigger page reload
      );
      await loadCourses(newSelected);
    } else {
      router.push('/', undefined, { shallow: true });
      setCourses([]);
      setFilteredCourses([]);
      setCollegeFilters([]);
    }
  };

  // Load courses for selected semesters
  const loadCourses = async (semesterValues: string[]) => {
    setLoading(true);
    try {
      const allCourses: Course[] = [];

      // Fetch courses for each selected semester
      for (const semValue of semesterValues) {
        const semester = semesters.find(s => s.value === semValue);
        if (!semester) continue;

        const response = await fetch(
          `${API_BASE}/api/courses/?acy=${semester.acy}&sem=${semester.sem}&limit=1000`
        );

        if (response.ok) {
          const data = await response.json();
          allCourses.push(...data);
        }
      }

      setCourses(allCourses);
      setFilteredCourses(allCourses);

      // Calculate college filters
      const collegeMap = new Map<string, number>();
      allCourses.forEach(course => {
        const college = course.college || course.dept || '其他';
        collegeMap.set(college, (collegeMap.get(college) || 0) + 1);
      });

      const filters: CollegeFilter[] = [
        { name: '全部', count: allCourses.length },
        ...Array.from(collegeMap.entries())
          .map(([name, count]) => ({ name, count }))
          .sort((a, b) => b.count - a.count)
      ];

      setCollegeFilters(filters);
      setSelectedCollege('全部');
    } catch (error) {
      console.error('Failed to load courses:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter courses by college, search, and advanced filters
  useEffect(() => {
    let filtered = courses;

    // Apply college filter
    if (selectedCollege !== '全部') {
      filtered = filtered.filter(course =>
        (course.college || course.dept || '其他') === selectedCollege
      );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(course =>
        course.name?.toLowerCase().includes(query) ||
        course.crs_no?.toLowerCase().includes(query) ||
        course.teacher?.toLowerCase().includes(query) ||
        course.dept?.toLowerCase().includes(query)
      );
    }

    // Apply advanced filters
    // Department filter
    if (advancedFilters.departments.length > 0) {
      filtered = filtered.filter(course =>
        course.dept && advancedFilters.departments.includes(course.dept)
      );
    }

    // Teacher filter
    if (advancedFilters.teachers.length > 0) {
      filtered = filtered.filter(course =>
        course.teacher && advancedFilters.teachers.includes(course.teacher)
      );
    }

    // Days filter (check if course has any of the selected days)
    if (advancedFilters.days.length > 0) {
      filtered = filtered.filter(course => {
        if (!course.day_codes) return false;
        return advancedFilters.days.some(day => course.day_codes?.includes(day));
      });
    }

    // Time slots filter (check if course time overlaps with selected periods)
    if (advancedFilters.timeSlots.length > 0) {
      filtered = filtered.filter(course => {
        if (!course.time_codes) return false;
        // Parse time codes and check if they fall within selected periods
        // Time slots: '1-4' (morning), '5-8' (afternoon), '9-12' (evening)
        return advancedFilters.timeSlots.some(slot => {
          const [start, end] = slot.split('-').map(Number);
          // Check if any digit in time_codes falls within the range
          const timeCodes = course.time_codes?.split('').map(Number).filter(n => !isNaN(n)) || [];
          return timeCodes.some(code => code >= start && code <= end);
        });
      });
    }

    // Course type filter (required/elective)
    if (advancedFilters.courseTypes.length > 0) {
      filtered = filtered.filter(course => {
        if (!course.required) return false;
        return advancedFilters.courseTypes.includes(course.required);
      });
    }

    // Credits filter
    if (advancedFilters.credits.length > 0) {
      filtered = filtered.filter(course =>
        course.credits && advancedFilters.credits.includes(course.credits)
      );
    }

    setFilteredCourses(filtered);
  }, [selectedCollege, searchQuery, courses, advancedFilters]);

  // Handle add to schedule
  const handleAddToSchedule = async (courseId: number) => {
    try {
      // Get or create user schedule for current semester
      const userId = 'guest_user'; // TODO: Replace with actual user ID from auth

      // Get user's schedules
      const schedulesRes = await fetch(`${API_BASE}/api/schedules/user/${userId}`);
      let schedules = [];

      if (schedulesRes.ok) {
        schedules = await schedulesRes.json();
      }

      // Find or create schedule for selected semester
      const firstSemester = selectedSemesters.length > 0 ? selectedSemesters[0] : '';
      const semester = semesters.find(s => s.value === firstSemester);

      if (!semester) {
        alert('請先選擇學期！');
        return;
      }

      let targetSchedule = schedules.find((s: any) => s.acy === semester.acy && s.sem === semester.sem);

      // Create schedule if not exists
      if (!targetSchedule) {
        const createRes = await fetch(`${API_BASE}/api/schedules`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: `我的 ${semester.label} 課表`,
            acy: semester.acy,
            sem: semester.sem,
            user_id: userId
          })
        });

        if (!createRes.ok) {
          throw new Error('無法創建課表');
        }

        targetSchedule = await createRes.json();
      }

      // Add course to schedule
      const addRes = await fetch(`${API_BASE}/api/schedules/${targetSchedule.id}/courses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_id: courseId })
      });

      if (addRes.ok) {
        alert('✅ 課程已成功加入課表！\n\n前往「我的課表」頁面查看。');
      } else if (addRes.status === 400) {
        alert('⚠️ 此課程已在課表中');
      } else {
        throw new Error('加入失敗');
      }
    } catch (error) {
      console.error('Failed to add course to schedule:', error);
      alert('❌ 加入課表失敗，請稍後再試');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50 bg-white dark:bg-gray-900 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
                  />
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold text-gray-900 dark:text-white">NYCU Course</span>
              <span className="text-xs text-gray-500 dark:text-gray-400 -mt-1">陽明交大選課</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/"
              className="text-indigo-600 dark:text-indigo-400 font-semibold transition flex items-center gap-2"
            >
              <span>📚</span>
              <span>瀏覽課程</span>
            </Link>
            <Link
              href="/schedule"
              className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium transition flex items-center gap-2"
            >
              <span>📋</span>
              <span>我的課表</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {/* Hero Section with Semester Selector */}
        <div className="bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                探索課程
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400">
                選擇學期，瀏覽課程，建立您的專屬課表
              </p>
            </div>

            {/* Semester Selector */}
            <div className="max-w-2xl mx-auto relative">
              <button
                onClick={() => setShowSemesterDropdown(!showSemesterDropdown)}
                className="w-full px-6 py-4 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-xl flex items-center justify-between text-gray-900 dark:text-white font-semibold hover:border-indigo-400 dark:hover:border-indigo-600 transition-all shadow-md"
              >
                <span className="flex items-center gap-2">
                  <span>📅</span>
                  {selectedSemesters.length === 0
                    ? '選擇學期'
                    : `已選擇 ${selectedSemesters.length} 個學期 ${selectedSemesters.join(', ')}`}
                </span>
                <ChevronDown
                  className={`h-5 w-5 transition-transform ${showSemesterDropdown ? 'rotate-180' : ''}`}
                />
              </button>

              {/* Semester Dropdown */}
              {showSemesterDropdown && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-xl shadow-2xl p-3 space-y-1 z-50 max-h-80 overflow-y-auto">
                  <div className="px-2 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400">
                    可選學期
                  </div>
                  {semesters.map(sem => (
                    <button
                      key={sem.value}
                      onClick={() => toggleSemester(sem.value)}
                      className={`w-full flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${
                        selectedSemesters.includes(sem.value)
                          ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-semibold'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white'
                      }`}
                    >
                      <span>{sem.label} 學期</span>
                      {selectedSemesters.includes(sem.value) && (
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Course Display Section */}
        {courses.length > 0 ? (
          <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Course Header */}
            <div className="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {selectedSemesters.join(', ')} 學期
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  {filteredCourses.length} 門課程
                </p>
              </div>

              {/* View Toggle and Search */}
              <div className="flex items-center gap-3">
                {/* Search Bar */}
                <div className="relative">
                  <input
                    type="text"
                    placeholder="搜尋課程..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                  />
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>

                {/* View Mode Toggle */}
                <div className="flex gap-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded transition ${
                      viewMode === 'grid'
                        ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Grid3x3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded transition ${
                      viewMode === 'list'
                        ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <List className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Advanced Filters */}
            <div className="mb-6">
              <AdvancedFilters
                courses={courses}
                onFilterChange={setAdvancedFilters}
                initialFilters={advancedFilters}
              />
            </div>

            {/* College Filters and Course Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* College Filter Sidebar */}
              {collegeFilters.length > 1 && (
                <div className="lg:col-span-1">
                  <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sticky top-20">
                    <div className="flex items-center gap-2 mb-3">
                      <Filter className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      <h3 className="font-semibold text-gray-900 dark:text-white">學院篩選</h3>
                    </div>
                    <div className="space-y-1">
                      {collegeFilters.map(filter => (
                        <button
                          key={filter.name}
                          onClick={() => setSelectedCollege(filter.name)}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition ${
                            selectedCollege === filter.name
                              ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-semibold'
                              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                          }`}
                        >
                          <span className="text-sm truncate">{filter.name}</span>
                          <span className="text-xs font-semibold">{filter.count}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Course Grid */}
              <div className={collegeFilters.length > 1 ? 'lg:col-span-3' : 'lg:col-span-4'}>
                {loading ? (
                  <div className="flex items-center justify-center py-20">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                      <p className="mt-4 text-gray-600 dark:text-gray-400">載入課程中...</p>
                    </div>
                  </div>
                ) : filteredCourses.length === 0 ? (
                  <div className="text-center py-20">
                    <p className="text-gray-600 dark:text-gray-400">找不到符合條件的課程</p>
                  </div>
                ) : (
                  <div className={`grid gap-4 ${
                    viewMode === 'grid'
                      ? 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
                      : 'grid-cols-1'
                  }`}>
                    {filteredCourses.map(course => (
                      <CourseCard
                        key={course.id}
                        course={course}
                        onAddSchedule={handleAddToSchedule}
                        showActions={true}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : selectedSemesters.length === 0 ? (
          <div className="max-w-2xl mx-auto px-4 py-20 text-center">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="text-6xl mb-4">📚</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                選擇學期開始探索
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                請選擇一個或多個學期以查看課程列表
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-2xl mx-auto px-4 py-20 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">載入課程中...</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-8 text-center">
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            <p className="text-lg font-medium text-slate-700 dark:text-slate-200 flex items-center justify-center gap-2">
              Built with
              <span className="text-rose-500 animate-pulse text-xl">❤️</span>
              for NYCU students
            </p>
            <p className="mt-2">讓選課變得更簡單 · 讓學習變得更有趣 🦐✨</p>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-500">
            <p>© 2025 NYCU 選課平台</p>
            <p>⚡ Made with Next.js & FastAPI</p>
          </div>
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
      revalidate: 3600,
    };
  } catch (error) {
    console.error('Error in getStaticProps:', error);
    return {
      notFound: true,
      revalidate: 60,
    };
  }
}
