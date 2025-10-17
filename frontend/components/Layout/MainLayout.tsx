'use client'

import React, { ReactNode } from 'react'

interface MainLayoutProps {
  children: ReactNode
  darkMode?: boolean
}

export function MainLayout({ children, darkMode = false }: MainLayoutProps) {
  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="bg-white dark:bg-slate-950 text-gray-900 dark:text-gray-100">
        {children}
      </div>
    </div>
  )
}
