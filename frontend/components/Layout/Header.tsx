'use client'

import React, { useState } from 'react'
import { useTranslation } from 'next-i18next'
import { Button } from '@/components/ui/button'

interface HeaderProps {
  darkMode?: boolean
  onDarkModeToggle?: (enabled: boolean) => void
  onLanguageChange?: (lang: string) => void
}

export function Header({ darkMode = false, onDarkModeToggle, onLanguageChange }: HeaderProps) {
  const { t, i18n } = useTranslation('common')
  const [showLangMenu, setShowLangMenu] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo / Brand */}
          <div className="flex items-center gap-3">
            <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 dark:from-blue-400 dark:to-blue-600 text-transparent bg-clip-text">
              🎓
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">NYCU Courses</h1>
              <p className="text-xs text-gray-600 dark:text-gray-400">Finding courses made simple</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden sm:flex items-center gap-1">
            <Button variant="ghost" className="text-gray-700 dark:text-gray-300">
              {t('browse')}
            </Button>
            <Button variant="ghost" className="text-gray-700 dark:text-gray-300">
              {t('mySchedule')}
            </Button>
          </nav>

          {/* Controls */}
          <div className="flex items-center gap-3">
            {/* Dark Mode Toggle */}
            <button
              onClick={() => onDarkModeToggle?.(!darkMode)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
              title="Toggle dark mode"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>

            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setShowLangMenu(!showLangMenu)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors text-sm font-semibold"
              >
                {i18n?.language === 'zh' ? '中文' : 'EN'}
              </button>
              {showLangMenu && (
                <div className="absolute right-0 mt-2 bg-white dark:bg-slate-800 rounded-lg border border-gray-200 dark:border-slate-700 overflow-hidden shadow-lg">
                  <button
                    onClick={() => {
                      onLanguageChange?.('en')
                      setShowLangMenu(false)
                    }}
                    className="block w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-slate-700 text-sm"
                  >
                    English
                  </button>
                  <button
                    onClick={() => {
                      onLanguageChange?.('zh')
                      setShowLangMenu(false)
                    }}
                    className="block w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-slate-700 text-sm border-t border-gray-200 dark:border-slate-700"
                  >
                    中文
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
