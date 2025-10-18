/**
 * Schedule Page - Course Schedule Builder with Backend Integration
 *
 * Features:
 * - Create and manage multiple schedules via backend API
 * - Drag-and-drop course search and addition
 * - Real-time conflict detection
 * - Automatic credit calculation
 * - Export schedule with clickable syllabus links
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { Header, Footer } from '@/components';
import { exportScheduleToPDF, exportScheduleWithGrid } from '@/lib/utils/pdfExporter';

interface Course {
  id: number;
  crs_no: string;
  name: string;
  teacher?: string;
  credits?: number;
  time?: string;
  classroom?: string;
  syllabus_url_zh?: string;
  syllabus_url_en?: string;
}

interface ScheduleCourse {
  id: number;
  schedule_id: number;
  course_id: number;
  color?: string;
  notes?: string;
  course: Course;
}

interface Schedule {
  id: number;
  name: string;
  acy: number;
  sem: number;
  user_id?: string;
  created_at: string;
  updated_at: string;
  total_credits: number;
  total_courses: number;
  schedule_courses?: ScheduleCourse[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export default function SchedulePage() {
  const router = useRouter();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [currentSchedule, setCurrentSchedule] = useState<Schedule | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Course[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // New schedule form
  const [newScheduleName, setNewScheduleName] = useState('');
  const [newScheduleAcy, setNewScheduleAcy] = useState(114); // Updated to current academic year
  const [newScheduleSem, setNewScheduleSem] = useState(1);
  const [availableSemesters, setAvailableSemesters] = useState<Array<{acy: number; sem: number}>>([]);

  // Load available semesters and set latest as default
  useEffect(() => {
    const loadSemesters = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/semesters`);
        if (response.ok) {
          const semesters = await response.json();
          setAvailableSemesters(semesters);

          // Set the latest semester as default for new schedules
          if (semesters.length > 0) {
            const latest = semesters[0]; // API returns semesters sorted by latest first
            setNewScheduleAcy(latest.acy);
            setNewScheduleSem(latest.sem);
          }
        }
      } catch (err) {
        console.error('Failed to load semesters:', err);
      }
    };

    loadSemesters();
  }, []);

  // Load user's schedules
  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      // For demo, we'll fetch all schedules for test_user
      // In production, this would use actual authentication
      const response = await fetch(`${API_BASE}/api/schedules/user/test_user`);
      if (!response.ok) throw new Error('Failed to load schedules');

      const data = await response.json();
      setSchedules(data);

      // Load first schedule by default
      if (data.length > 0 && !currentSchedule) {
        await loadScheduleDetail(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  const loadScheduleDetail = async (scheduleId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}`);
      if (!response.ok) throw new Error('Failed to load schedule details');

      const data = await response.json();
      setCurrentSchedule(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schedule');
    }
  };

  const createSchedule = async () => {
    if (!newScheduleName.trim()) {
      alert('請輸入課表名稱');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/schedules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newScheduleName,
          acy: newScheduleAcy,
          sem: newScheduleSem,
          user_id: 'test_user',
        }),
      });

      if (!response.ok) throw new Error('Failed to create schedule');

      const newSchedule = await response.json();
      setSchedules([...schedules, newSchedule]);
      setCurrentSchedule(newSchedule);
      setShowCreateModal(false);
      setNewScheduleName('');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create schedule');
    }
  };

  const searchCourses = async (query: string) => {
    if (!query.trim() || !currentSchedule) {
      setSearchResults([]);
      return;
    }

    try {
      setSearchLoading(true);
      // Filter by current schedule's semester
      const response = await fetch(
        `${API_BASE}/api/courses/?q=${encodeURIComponent(query)}&acy=${currentSchedule.acy}&sem=${currentSchedule.sem}&limit=20`
      );

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      setSearchResults(data || []);
    } catch (err) {
      console.error('Search error:', err);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const addCourseToSchedule = async (courseId: number) => {
    if (!currentSchedule) return;

    try {
      const response = await fetch(
        `${API_BASE}/api/schedules/${currentSchedule.id}/courses`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ course_id: courseId }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add course');
      }

      // Reload schedule to get updated data
      await loadScheduleDetail(currentSchedule.id);
      setShowSearchModal(false);
      setSearchQuery('');
      setSearchResults([]);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add course');
    }
  };

  const removeCourseFromSchedule = async (courseId: number) => {
    if (!currentSchedule) return;

    try {
      const response = await fetch(
        `${API_BASE}/api/schedules/${currentSchedule.id}/courses`,
        {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ course_id: courseId }),
        }
      );

      if (!response.ok) throw new Error('Failed to remove course');

      // Reload schedule
      await loadScheduleDetail(currentSchedule.id);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to remove course');
    }
  };

  const deleteSchedule = async (scheduleId: number) => {
    if (!confirm('確定要刪除這個課表嗎？')) return;

    try {
      const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete schedule');

      const updatedSchedules = schedules.filter((s) => s.id !== scheduleId);
      setSchedules(updatedSchedules);

      if (currentSchedule?.id === scheduleId) {
        setCurrentSchedule(updatedSchedules[0] || null);
        if (updatedSchedules[0]) {
          await loadScheduleDetail(updatedSchedules[0].id);
        }
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete schedule');
    }
  };

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        searchCourses(searchQuery);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  if (loading) {
    return (
      <>
        <Head>
          <title>我的課表 - NYCU Course Platform</title>
        </Head>
        <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
          <Header />
          <main className="flex-1 container mx-auto px-4 py-8">
            <div className="animate-pulse">
              <div className="h-10 bg-gray-300 rounded w-1/4 mb-8"></div>
              <div className="h-64 bg-gray-300 rounded"></div>
            </div>
          </main>
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>我的課表 - NYCU Course Platform</title>
        <meta name="description" content="管理您的 NYCU 課程表" />
      </Head>

      <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
        <Header />

        <main className="flex-1 container mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
                我的課表
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                建立和管理您的個人課程表
              </p>
            </div>

            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition flex items-center gap-2"
            >
              <span>➕</span>
              <span>新增課表</span>
            </button>
          </div>

          {/* Schedule Tabs */}
          {schedules.length > 0 && (
            <div className="mb-6 flex items-center gap-4 overflow-x-auto pb-2">
              {schedules.map((schedule) => (
                <button
                  key={schedule.id}
                  onClick={() => loadScheduleDetail(schedule.id)}
                  className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                    currentSchedule?.id === schedule.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {schedule.name}
                </button>
              ))}
            </div>
          )}

          {currentSchedule ? (
            <>
              {/* Stats Card */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6">
                <div className="flex flex-wrap items-center justify-between gap-6">
                  <div className="flex gap-8">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">課程數量</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white">
                        {currentSchedule.total_courses}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">總學分</p>
                      <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                        {currentSchedule.total_credits}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">學期</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white">
                        {currentSchedule.acy}-{currentSchedule.sem}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowSearchModal(true)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition"
                    >
                      ➕ 新增課程
                    </button>

                    {/* PDF Export Dropdown */}
                    <div className="relative group">
                      <button className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition flex items-center gap-2">
                        📄 匯出 PDF
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <div className="absolute right-0 mt-2 w-56 rounded-lg shadow-lg bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 hidden group-hover:block z-50">
                        <div className="py-1">
                          <button
                            onClick={() => exportScheduleToPDF(currentSchedule)}
                            className="block w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition"
                          >
                            <div className="font-medium">📋 標準格式</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">表格形式，含可點擊連結</div>
                          </button>
                          <button
                            onClick={() => exportScheduleWithGrid(currentSchedule)}
                            className="block w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition"
                          >
                            <div className="font-medium">📅 時間網格</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">週課表格式（橫向）</div>
                          </button>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => deleteSchedule(currentSchedule.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition"
                    >
                      🗑️ 刪除課表
                    </button>
                  </div>
                </div>
              </div>

              {/* Course List */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  課程列表
                </h2>

                {currentSchedule.schedule_courses && currentSchedule.schedule_courses.length > 0 ? (
                  <div className="space-y-3">
                    {currentSchedule.schedule_courses.map((sc) => (
                      <div
                        key={sc.id}
                        className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-indigo-300 dark:hover:border-indigo-500 transition"
                      >
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {sc.course.name}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {sc.course.crs_no}
                            {sc.course.teacher && ` · ${sc.course.teacher}`}
                            {sc.course.credits && ` · ${sc.course.credits} 學分`}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {sc.course.time || '時間未定'}
                            {sc.course.classroom && ` · ${sc.course.classroom}`}
                          </p>
                          {sc.course.syllabus_url_zh && (
                            <a
                              href={sc.course.syllabus_url_zh}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                            >
                              📄 查看課程大綱
                            </a>
                          )}
                        </div>

                        <button
                          onClick={() => removeCourseFromSchedule(sc.course_id)}
                          className="ml-4 px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition"
                        >
                          移除
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      課表是空的，開始添加課程吧！
                    </p>
                    <button
                      onClick={() => setShowSearchModal(true)}
                      className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition"
                    >
                      搜尋課程
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-12 text-center">
              <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">
                還沒有課表，建立第一個課表開始吧！
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-8 py-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition text-lg"
              >
                建立課表
              </button>
            </div>
          )}
        </main>

        <Footer />
      </div>

      {/* Create Schedule Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              建立新課表
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  課表名稱
                </label>
                <input
                  type="text"
                  value={newScheduleName}
                  onChange={(e) => setNewScheduleName(e.target.value)}
                  placeholder="例如：113-1 我的課表"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    學年度
                  </label>
                  <input
                    type="number"
                    value={newScheduleAcy}
                    onChange={(e) => setNewScheduleAcy(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    學期
                  </label>
                  <select
                    value={newScheduleSem}
                    onChange={(e) => setNewScheduleSem(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value={1}>第一學期</option>
                    <option value={2}>第二學期</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-8">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                取消
              </button>
              <button
                onClick={createSchedule}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition"
              >
                建立
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-3xl w-full max-h-[80vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              搜尋並添加課程
            </h2>

            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="輸入課程名稱、課號或教師姓名..."
              className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-6"
              autoFocus
            />

            {searchLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              </div>
            ) : searchResults.length > 0 ? (
              <div className="space-y-3">
                {searchResults.map((course) => (
                  <div
                    key={course.id}
                    className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-indigo-300 dark:hover:border-indigo-500 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {course.name}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {course.crs_no}
                          {course.teacher && ` · ${course.teacher}`}
                          {course.credits && ` · ${course.credits} 學分`}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {course.time || '時間未定'}
                        </p>
                      </div>
                      <button
                        onClick={() => addCourseToSchedule(course.id)}
                        className="ml-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                      >
                        添加
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : searchQuery ? (
              <p className="text-center text-gray-600 dark:text-gray-400 py-8">
                沒有找到相關課程
              </p>
            ) : (
              <p className="text-center text-gray-600 dark:text-gray-400 py-8">
                開始輸入以搜尋課程
              </p>
            )}

            <button
              onClick={() => {
                setShowSearchModal(false);
                setSearchQuery('');
                setSearchResults([]);
              }}
              className="w-full mt-6 px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >
              關閉
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export async function getStaticProps({ locale }: { locale: string }) {
  try {
    const translations = await serverSideTranslations(locale, [
      'common',
      'home',
      'course',
      'schedule',
      'error',
    ]);
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
