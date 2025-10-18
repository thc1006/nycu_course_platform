/**
 * Header Component
 *
 * Main navigation header for the NYCU Course Platform.
 * Features:
 * - Logo/brand name
 * - Navigation menu (Home, Schedule, About)
 * - Search box
 * - Responsive mobile menu with hamburger icon
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * <Header />
 * ```
 */

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';
import LanguageSwitcher from '../LanguageSwitcher';
import { ExternalLink, ChevronDown } from 'lucide-react';

/**
 * Header component with responsive navigation
 *
 * @returns {JSX.Element} The rendered header component
 */
// NYCU Official Services Integration
const NYCU_SERVICES = {
  core: [
    { name: 'NYCU 單一入口', nameEn: 'NYCU Portal', url: 'https://portal.nycu.edu.tw/', icon: '🏛️', description: '校園服務入口' },
    { name: '課程時間表', nameEn: 'Course Timetable', url: 'https://timetable.nycu.edu.tw/', icon: '📅', description: '官方課表系統' },
    { name: 'E3 教學平台', nameEn: 'E3 Learning', url: 'https://portal.nycu.edu.tw/', icon: '🎓', description: '數位學習平台' },
  ],
  academic: [
    { name: '學籍成績', nameEn: 'Academic Records', url: 'https://portal.nycu.edu.tw/', icon: '📊', description: '成績查詢系統' },
    { name: '圖書館', nameEn: 'Library', url: 'https://www.lib.nycu.edu.tw/', icon: '📚', description: '圖書資源' },
  ],
  services: [
    { name: 'Microsoft 365', nameEn: 'M365', url: 'https://portal.nycu.edu.tw/#/m365/index', icon: '💼', description: '電子郵件與雲端' },
    { name: '距離畢業距離(需VPN)', nameEn: 'Graduation Distance', url: 'https://eportfolio.nycu.edu.tw/grade/distance', icon: '🎓', description: '畢業學分查詢' },
    { name: '校務系統', nameEn: 'Campus Systems', url: 'https://portal.nycu.edu.tw/#/links/nycu', icon: '⚙️', description: '70+ 服務' },
  ]
};

const Header: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isServicesDropdownOpen, setIsServicesDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsServicesDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /**
   * Toggle mobile menu visibility
   */
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  /**
   * Check if a route is currently active
   *
   * @param {string} path - The route path to check
   * @returns {boolean} True if the route is active
   */
  const isActive = (path: string): boolean => {
    return router.pathname === path;
  };

  return (
    <header className="bg-white/10 dark:bg-gray-700/10 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center">
        <div className="flex items-center justify-between w-full">
          {/* Logo/Brand - NDHU Style with Sparkles + Pulse Animation */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="relative">
              {/* Main Icon: 9x9 indigo-600 圓角方框 + Sparkles SVG */}
              <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg
                  className="w-5 h-5 text-white"
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
              {/* 右上角活躍指示點 with pulse animation */}
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold text-gray-900 dark:text-white">NYCU Course</span>
              <span className="text-xs text-gray-500 dark:text-gray-400 -mt-1">陽明交大選課</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-2">
            <Link
              href="/"
              className={`relative flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive('/')
                  ? 'text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-900/20 shadow-sm'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
              <span>瀏覽課程</span>
              {isActive('/') && (
                <div className="absolute inset-0 bg-indigo-100/50 dark:bg-indigo-800/30 rounded-xl -z-10"></div>
              )}
            </Link>
            <Link
              href="/schedule"
              className={`relative flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive('/schedule')
                  ? 'text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-900/20 shadow-sm'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
              </svg>
              <span>我的課表</span>
              {isActive('/schedule') && (
                <div className="absolute inset-0 bg-indigo-100/50 dark:bg-indigo-800/30 rounded-xl -z-10"></div>
              )}
            </Link>

            {/* NYCU Services Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsServicesDropdownOpen(!isServicesDropdownOpen)}
                className="relative flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-white bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 border border-emerald-200 dark:border-emerald-700"
              >
                <span className="text-base">🏛️</span>
                <span>NYCU 服務</span>
                <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isServicesDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown Menu */}
              {isServicesDropdownOpen && (
                <div className="absolute top-full right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50 animate-fade-in">
                  <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-4 text-white">
                    <h3 className="font-bold text-lg flex items-center gap-2">
                      <span>🏛️</span>
                      NYCU 單一入口服務
                    </h3>
                    <p className="text-xs text-emerald-100 mt-1">快速存取交大校園系統</p>
                  </div>

                  <div className="p-3 max-h-96 overflow-y-auto">
                    {/* Core Services */}
                    <div className="mb-4">
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-2">核心服務</h4>
                      <div className="space-y-1">
                        {NYCU_SERVICES.core.map((service) => (
                          <a
                            key={service.url}
                            href={service.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-all duration-200 group"
                          >
                            <span className="text-2xl">{service.icon}</span>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-gray-900 dark:text-white text-sm">{service.name}</span>
                                <ExternalLink className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </div>
                              <p className="text-xs text-gray-500 dark:text-gray-400">{service.description}</p>
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>

                    {/* Academic Services */}
                    <div className="mb-4">
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-2">學術資源</h4>
                      <div className="space-y-1">
                        {NYCU_SERVICES.academic.map((service) => (
                          <a
                            key={service.url}
                            href={service.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all duration-200 group"
                          >
                            <span className="text-2xl">{service.icon}</span>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-gray-900 dark:text-white text-sm">{service.name}</span>
                                <ExternalLink className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </div>
                              <p className="text-xs text-gray-500 dark:text-gray-400">{service.description}</p>
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>

                    {/* Other Services */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-2">其他服務</h4>
                      <div className="space-y-1">
                        {NYCU_SERVICES.services.map((service) => (
                          <a
                            key={service.url}
                            href={service.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all duration-200 group"
                          >
                            <span className="text-2xl">{service.icon}</span>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-gray-900 dark:text-white text-sm">{service.name}</span>
                                <ExternalLink className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </div>
                              <p className="text-xs text-gray-500 dark:text-gray-400">{service.description}</p>
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-700/50 px-4 py-3 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
                      ⚠️ 部分服務需要登入 NYCU 單一入口
                    </p>
                  </div>
                </div>
              )}
            </div>

            <LanguageSwitcher />
          </nav>

          {/* Search Box - Desktop */}
          <div className="hidden lg:flex items-center">
            <div className="relative">
              <input
                type="search"
                placeholder="搜尋課程..."
                className="w-64 pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 hover:bg-white/90 dark:hover:bg-gray-800/90 hover:shadow-sm"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const query = (e.target as HTMLInputElement).value;
                    if (query.trim()) {
                      router.push(`/?q=${encodeURIComponent(query)}`);
                    }
                  }
                }}
              />
              <svg
                className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden p-2 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 transition-colors duration-200"
            aria-label="切換選單"
          >
            {isMobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden fixed inset-0 top-16 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm z-40 overflow-y-auto">
            <div className="p-4 space-y-4">
              {/* Mobile Navigation Links */}
              <nav className="flex flex-col space-y-2">
                <Link
                  href="/"
                  className={`px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                    isActive('/')
                      ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                      : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  瀏覽課程
                </Link>
                <Link
                  href="/schedule"
                  className={`px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                    isActive('/schedule')
                      ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                      : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-100/50 dark:hover:bg-gray-700/50'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  我的課表
                </Link>
              </nav>

              {/* Mobile Search */}
              <div className="relative mt-4">
                <input
                  type="search"
                  placeholder="搜尋課程..."
                  className="w-full pl-10 pr-4 py-3 bg-white/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const query = (e.target as HTMLInputElement).value;
                      if (query.trim()) {
                        router.push(`/?q=${encodeURIComponent(query)}`);
                        setIsMobileMenuOpen(false);
                      }
                    }
                  }}
                />
                <svg
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>

              {/* Mobile Language Switcher */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <LanguageSwitcher className="justify-between" />
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
