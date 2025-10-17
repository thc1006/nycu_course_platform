'use client'

import React from 'react'
import { Button } from '@/components/ui/button'

interface CourseCardProps {
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
  rating?: number
  reviews?: number
  onAddToSchedule?: (id: number) => void
}

export function CourseCard({
  id,
  crs_no,
  name,
  teacher,
  credits,
  dept,
  time,
  classroom,
  rating = 4.2,
  reviews = 23,
  onAddToSchedule,
}: CourseCardProps) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700 overflow-hidden hover:shadow-lg dark:hover:shadow-slate-800/50 transition-shadow duration-300">
      {/* Card Header */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex justify-between items-start gap-2 mb-2">
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">{crs_no}</p>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white line-clamp-2">{name}</h3>
          </div>
          <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-2 py-1 rounded text-xs font-semibold">
            {dept}
          </span>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-2 text-sm">
          <span className="text-yellow-500">⭐</span>
          <span className="font-semibold text-gray-900 dark:text-white">{rating.toFixed(1)}</span>
          <span className="text-gray-600 dark:text-gray-400">({reviews} reviews)</span>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-4 space-y-3">
        {/* Instructor */}
        <div className="flex items-start gap-2">
          <span className="text-gray-500 dark:text-gray-400">👤</span>
          <div className="flex-1">
            <p className="text-sm text-gray-600 dark:text-gray-400">Instructor</p>
            <p className="font-semibold text-gray-900 dark:text-white">{teacher}</p>
          </div>
        </div>

        {/* Course Details */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Credits</p>
            <p className="font-semibold text-gray-900 dark:text-white">{credits}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Time</p>
            <p className="text-sm font-medium text-gray-900 dark:text-white">{time.split(' ')[0]}</p>
          </div>
        </div>

        {/* Classroom */}
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Classroom</p>
          <p className="font-semibold text-gray-900 dark:text-white">{classroom}</p>
        </div>
      </div>

      {/* Card Footer */}
      <div className="p-4 bg-gray-50 dark:bg-slate-800/50 border-t border-gray-200 dark:border-slate-700 flex gap-2">
        <Button
          onClick={() => onAddToSchedule?.(id)}
          size="sm"
          variant="default"
          className="flex-1"
        >
          Add to Schedule
        </Button>
        <Button size="sm" variant="outline" className="flex-1">
          Details
        </Button>
      </div>
    </div>
  )
}
