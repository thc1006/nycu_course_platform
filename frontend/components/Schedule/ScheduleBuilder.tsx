'use client'

import React, { useState, useCallback } from 'react'
import { generateICalFormat, exportScheduleToJSON } from '@/utils/scheduleExport'
import { detectTimeConflicts } from '@/utils/conflictDetection'

interface Course {
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
  [key: string]: any
}

interface ScheduleBuilderProps {
  courses: Course[]
  selectedCourses: Course[]
  onCoursesChange: (courses: Course[]) => void
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const DAY_ABBREVIATIONS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
const HOURS = Array.from({ length: 10 }, (_, i) => i + 8) // 8:00 - 17:00

export function ScheduleBuilder({
  courses,
  selectedCourses,
  onCoursesChange,
}: ScheduleBuilderProps) {
  const [draggedCourse, setDraggedCourse] = useState<Course | null>(null)
  const [conflicts, setConflicts] = useState<any[]>([])

  // Update conflicts when selected courses change
  React.useEffect(() => {
    const detectedConflicts = detectTimeConflicts(selectedCourses)
    setConflicts(detectedConflicts)
  }, [selectedCourses])

  // Handle adding a course to schedule
  const handleAddCourse = useCallback(
    (course: Course) => {
      if (!selectedCourses.find((c) => c.id === course.id)) {
        onCoursesChange([...selectedCourses, course])
      }
    },
    [selectedCourses, onCoursesChange]
  )

  // Handle removing a course from schedule
  const handleRemoveCourse = useCallback(
    (courseId: number) => {
      onCoursesChange(selectedCourses.filter((c) => c.id !== courseId))
    },
    [selectedCourses, onCoursesChange]
  )

  // Handle drag start
  const handleDragStart = (course: Course) => {
    setDraggedCourse(course)
  }

  // Handle drag over
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  // Handle drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (draggedCourse) {
      // In a real implementation, this would reschedule the course
      // For now, just clear the dragged state
      setDraggedCourse(null)
    }
  }

  // Calculate total credits
  const totalCredits = selectedCourses.reduce((sum, course) => sum + course.credits, 0)

  // Export to iCal format
  const handleExportICal = () => {
    const icalContent = generateICalFormat(selectedCourses)
    downloadFile(icalContent, 'schedule.ics', 'text/calendar')
  }

  // Export to JSON format
  const handleExportJSON = () => {
    const jsonContent = exportScheduleToJSON(selectedCourses)
    downloadFile(jsonContent, 'schedule.json', 'application/json')
  }

  // Helper function to download file
  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  // Check if course has conflict
  const hasConflict = (courseId: number) => {
    return conflicts.some((conflict) => conflict.courseIds.includes(courseId))
  }

  return (
    <div className="w-full bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center border-b pb-4">
          <h2 className="text-2xl font-bold dark:text-white">My Schedule</h2>
          <div className="flex gap-2">
            <button
              onClick={handleExportICal}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition"
              title="Export"
            >
              Export iCal
            </button>
            <button
              onClick={handleExportJSON}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition"
              title="Download"
            >
              Download JSON
            </button>
          </div>
        </div>

        {/* Warnings */}
        {conflicts.length > 0 && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <strong>Time Conflicts Detected:</strong>
            <ul className="mt-2 space-y-1">
              {conflicts.map((conflict, idx) => (
                <li key={idx}>• {conflict.message}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Schedule Grid */}
        <div className="overflow-x-auto">
          <div className="min-w-full border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100 dark:bg-gray-800">
                  <th className="border-r p-2 text-center font-semibold dark:text-white">Time</th>
                  {DAYS.map((day) => (
                    <th key={day} className="border-r p-2 text-center font-semibold dark:text-white">
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {HOURS.map((hour) => (
                  <tr key={hour} className="border-t">
                    <td className="border-r p-2 text-center font-semibold text-sm bg-gray-50 dark:bg-gray-800 dark:text-white">
                      {String(hour).padStart(2, '0')}:00
                    </td>
                    {DAY_ABBREVIATIONS.map((day) => {
                      const coursesAtSlot = selectedCourses.filter((course) => {
                        const timeRegex = new RegExp(`^${day}\\s+${String(hour).padStart(2, '0')}:`)
                        return timeRegex.test(course.time)
                      })

                      return (
                        <td
                          key={`${day}-${hour}`}
                          className="border-r p-1 h-20 align-top hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                          onDragOver={handleDragOver}
                          onDrop={handleDrop}
                        >
                          <div className="space-y-1">
                            {coursesAtSlot.map((course) => (
                              <div
                                key={course.id}
                                draggable
                                onDragStart={() => handleDragStart(course)}
                                className={`p-1 rounded text-xs cursor-move select-none transition ${
                                  hasConflict(course.id)
                                    ? 'bg-red-200 border border-red-400 dark:bg-red-900 dark:border-red-600'
                                    : 'bg-blue-100 border border-blue-400 dark:bg-blue-900 dark:border-blue-600'
                                }`}
                              >
                                <div className="font-semibold dark:text-white">{course.crs_no}</div>
                                <div className="text-xs dark:text-gray-200">{course.name}</div>
                              </div>
                            ))}
                          </div>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Course List */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold dark:text-white">Selected Courses</h3>
          <div className="space-y-2">
            {selectedCourses.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400">No courses selected</p>
            ) : (
              selectedCourses.map((course) => (
                <div
                  key={course.id}
                  className={`p-3 rounded-lg flex justify-between items-center border-l-4 ${
                    hasConflict(course.id)
                      ? 'bg-red-50 border-red-400 dark:bg-red-900/20 dark:border-red-500'
                      : 'bg-blue-50 border-blue-400 dark:bg-blue-900/20 dark:border-blue-500'
                  }`}
                >
                  <div className="flex-1">
                    <div className="font-semibold dark:text-white">
                      {course.crs_no} - {course.name}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      {course.teacher} • {course.time} • {course.credits} credits
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemoveCourse(course.id)}
                    className="ml-4 px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded transition"
                    title="Remove/Delete"
                  >
                    Remove
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border">
          <div className="text-lg font-semibold dark:text-white">
            Total Credits: <span className="text-blue-600 dark:text-blue-400">{totalCredits}</span>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300">
            {selectedCourses.length} course{selectedCourses.length !== 1 ? 's' : ''} selected
          </div>
        </div>

        {/* Add Course Section */}
        {courses.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-xl font-semibold dark:text-white">Available Courses</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {courses
                .filter((course) => !selectedCourses.find((sc) => sc.id === course.id))
                .slice(0, 10)
                .map((course) => (
                  <div
                    key={course.id}
                    className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border flex justify-between items-center"
                  >
                    <div className="flex-1">
                      <div className="font-semibold dark:text-white">
                        {course.crs_no} - {course.name}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-300">
                        {course.teacher} • {course.time}
                      </div>
                    </div>
                    <button
                      onClick={() => handleAddCourse(course)}
                      className="ml-4 px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded transition"
                      title="Add"
                    >
                      Add
                    </button>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
