import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useTranslation } from 'next-i18next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { ChevronDown } from 'lucide-react';

interface Semester {
  label: string;
  value: string;
}

export default function HomePage() {
  const { t } = useTranslation(['common', 'home']);
  const router = useRouter();
  const lang = (router.locale || 'en') as 'en' | 'zh';

  const [selectedSemesters, setSelectedSemesters] = useState<string[]>([]);
  const [showSemesterDropdown, setShowSemesterDropdown] = useState(false);

  const semesters: Semester[] = [
    { label: '114-1', value: '114-1' },
    { label: '114-2', value: '114-2' },
    { label: '113-1', value: '113-1' },
    { label: '113-2', value: '113-2' },
    { label: '112-1', value: '112-1' },
    { label: '112-2', value: '112-2' },
    { label: '111-1', value: '111-1' },
    { label: '111-2', value: '111-2' },
    { label: '110-1', value: '110-1' },
  ];

  const toggleSemester = (value: string) => {
    setSelectedSemesters(prev =>
      prev.includes(value)
        ? prev.filter(s => s !== value)
        : [...prev, value]
    );
  };

  const handleViewCourses = () => {
    if (selectedSemesters.length === 0) {
      alert(lang === 'zh' ? '請選擇至少一個學期' : 'Please select at least one semester');
      return;
    }
    // Navigate to browse with selected semesters
    const params = new URLSearchParams();
    selectedSemesters.forEach(sem => params.append('semester', sem));
    router.push(`/browse?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              <span className="text-blue-600 dark:text-blue-400">NYCU</span> Course
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white transition">
              {lang === 'zh' ? '查課拉' : 'Platform'}
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/browse"
              className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium transition flex items-center gap-2"
            >
              <span>📚</span>
              <span>{lang === 'zh' ? '瀏覽課表' : 'Browse Courses'}</span>
            </Link>
            <Link
              href="/schedule"
              className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium transition flex items-center gap-2"
            >
              <span>📋</span>
              <span>{lang === 'zh' ? '我的課表' : 'My Schedule'}</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section - Similar to NDHU */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-24">
        <div className="max-w-2xl w-full text-center">
          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            {lang === 'zh' ? '探索課程' : 'Explore Courses'}
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 mb-12">
            {lang === 'zh'
              ? '選擇學期，瀏覽課程，建立您的專屬課表'
              : 'Select a semester, browse courses, and build your personal schedule'}
          </p>

          {/* Semester Selector Button */}
          <div className="relative mb-8">
            <button
              onClick={() => setShowSemesterDropdown(!showSemesterDropdown)}
              className="w-full px-6 py-4 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg flex items-center justify-between text-gray-900 dark:text-white font-semibold hover:border-gray-400 dark:hover:border-gray-600 transition-all"
            >
              <span className="flex items-center gap-2">
                <span>📚</span>
                {selectedSemesters.length === 0
                  ? lang === 'zh'
                    ? '選擇學期'
                    : 'Select Semester'
                  : `${selectedSemesters.length} ${lang === 'zh' ? '個學期已選' : 'semesters selected'}`}
              </span>
              <ChevronDown
                className={`h-5 w-5 transition-transform ${showSemesterDropdown ? 'rotate-180' : ''}`}
              />
            </button>

            {/* Semester Dropdown */}
            {showSemesterDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg shadow-lg p-3 space-y-2">
                {semesters.map(sem => (
                  <label
                    key={sem.value}
                    className="flex items-center gap-3 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-pointer transition"
                  >
                    <input
                      type="checkbox"
                      checked={selectedSemesters.includes(sem.value)}
                      onChange={() => toggleSemester(sem.value)}
                      className="w-5 h-5 rounded border-gray-300 cursor-pointer"
                    />
                    <span className="text-gray-900 dark:text-white font-medium">{sem.label}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Call to Action */}
          {selectedSemesters.length > 0 && (
            <div className="mb-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {lang === 'zh'
                  ? `✓ 已選擇 ${selectedSemesters.length} 個學期`
                  : `✓ ${selectedSemesters.length} semester(s) selected`}
              </p>
            </div>
          )}

          {/* Browse Button */}
          <button
            onClick={handleViewCourses}
            className={`w-full px-8 py-4 rounded-lg font-semibold text-white transition-all transform hover:scale-105 ${
              selectedSemesters.length > 0
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-400 cursor-not-allowed'
            }`}
            disabled={selectedSemesters.length === 0}
          >
            {lang === 'zh' ? '瀏覽課程' : 'Browse Courses'} →
          </button>

          {/* Empty State Message */}
          {selectedSemesters.length === 0 && (
            <div className="mt-8 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <p className="text-gray-600 dark:text-gray-400">
                {lang === 'zh'
                  ? '請選擇一個或多個學期以查看課程列表'
                  : 'Please select one or more semesters to view the course list'}
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer - Minimal like NDHU */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center">
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            {lang === 'zh' ? (
              <>
                <p>Built with ❤️ for NYCU students</p>
                <p className="mt-2">讓選課變得更簡單 · 讓學習變得更有趣 🦐✨</p>
              </>
            ) : (
              <p>Built with ❤️ for NYCU students</p>
            )}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-500">
            <p>© 2025 NYCU Course Platform</p>
            <p>⚡ Made with Next.js & TypeScript</p>
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
      revalidate: 3600, // ISR: Revalidate every hour
    };
  } catch (error) {
    console.error('Error in getStaticProps:', error);
    // Return a fallback page that will trigger a rebuild
    return {
      notFound: true,
      revalidate: 60, // Try again after 1 minute on error
    };
  }
}