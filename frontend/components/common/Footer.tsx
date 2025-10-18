/**
 * Footer Component
 *
 * NDHU Design System Compliant Site Footer
 * Features:
 * - Blur background effect (backdrop-blur-xl)
 * - Slate color system with transparency
 * - Multi-column layout (3 columns on desktop, 1 on mobile)
 * - Navigation links
 * - Full dark mode support
 * - py-12 vertical padding
 * - Responsive design with proper spacing
 * - Traditional Chinese localization
 *
 * @example
 * ```tsx
 * <Footer />
 * ```
 */

import React from 'react';
import Link from 'next/link';

/**
 * Footer component with NDHU design system styling
 * Includes blur background, proper spacing, and accessibility features
 *
 * @returns {JSX.Element} The rendered footer component
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-t border-slate-200/50 dark:border-slate-700/50 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
          {/* About Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-indigo-600 dark:text-indigo-400 transition-colors duration-200">
              NYCU Course
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              國立陽明交通大學課程查詢與選課平台 — 讓選課變得更簡單，讓學習變得更有趣
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white transition-colors duration-200">
              快速連結
            </h3>
            <nav className="flex flex-col space-y-2">
              <Link
                href="/"
                className="text-sm text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 font-medium"
              >
                瀏覽課程
              </Link>
              <Link
                href="/schedule"
                className="text-sm text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 font-medium"
              >
                我的課表
              </Link>
              <a
                href="https://www.nycu.edu.tw"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 font-medium"
              >
                陽明交大官網
              </a>
            </nav>
          </div>

          {/* Resources */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white transition-colors duration-200">
              開發資源
            </h3>
            <nav className="flex flex-col space-y-2">
              <a
                href="https://github.com/thc1006/nycu_course_platform"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 font-medium inline-flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
                GitHub 原始碼
              </a>
              <a
                href="https://dstw.dev"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 font-medium"
              >
                DSTW.dev
              </a>
            </nav>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-slate-200/50 dark:border-slate-700/50 mt-8 pt-8">
          {/* Main Slogan - NDHU Style */}
          <div className="text-center space-y-4 mb-6">
            <p className="text-lg font-medium text-slate-700 dark:text-slate-200 flex items-center justify-center gap-2">
              Built with
              <span className="text-rose-500 animate-pulse text-xl">❤️</span>
              for NYCU students
            </p>
            <p className="text-slate-600 dark:text-slate-300 text-base font-light">
              讓選課變得更簡單 · 讓學習變得更有趣
              <span className="inline-block ml-1 text-lg">✨</span>
            </p>
          </div>

          {/* Divider Line */}
          <div className="flex items-center justify-center mb-6">
            <div className="h-px bg-slate-300/60 dark:bg-slate-600/60 w-32"></div>
          </div>

          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            {/* Copyright */}
            <div className="flex flex-col sm:flex-row items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
              <div className="flex items-center gap-2">
                <span className="text-xs">©</span>
                <span>{currentYear} NYCU 選課平台</span>
              </div>
              <div className="hidden sm:block w-1 h-1 bg-slate-400/60 rounded-full"></div>
              <div className="flex items-center gap-2">
                <span className="text-xs">⚡</span>
                <span>Made with Next.js & FastAPI</span>
              </div>
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/thc1006/nycu_course_platform"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200"
                aria-label="GitHub"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
