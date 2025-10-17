/**
 * Conflict Detection Utility
 * Handles time slot parsing and conflict detection for course schedules
 */

interface TimeSlot {
  day: string
  startHour: number
  startMinute: number
  endHour: number
  endMinute: number
}

interface Conflict {
  courseIds: number[]
  message: string
  severity: 'warning' | 'error'
}

interface Course {
  id: number
  time: string
  crs_no?: string
  [key: string]: any
}

/**
 * Parse time slot string in format "Day HH:MM-HH:MM"
 * Example: "Mon 09:00-11:00"
 */
export function parseTimeSlot(timeString: string): TimeSlot | null {
  try {
    // Pattern: "Mon 09:00-11:00"
    const regex = /^(\w+)\s+(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$/
    const match = timeString.trim().match(regex)

    if (!match) {
      return null
    }

    const [, day, startHour, startMinute, endHour, endMinute] = match

    return {
      day,
      startHour: parseInt(startHour, 10),
      startMinute: parseInt(startMinute, 10),
      endHour: parseInt(endHour, 10),
      endMinute: parseInt(endMinute, 10),
    }
  } catch (error) {
    return null
  }
}

/**
 * Convert time to minutes from midnight for easier comparison
 */
function timeToMinutes(hour: number, minute: number): number {
  return hour * 60 + minute
}

/**
 * Check if two time slots conflict (same day and overlapping times)
 * Adjacent slots (end time = start time) do NOT conflict
 */
export function hasConflict(time1: string, time2: string): boolean {
  const slot1 = parseTimeSlot(time1)
  const slot2 = parseTimeSlot(time2)

  // If parsing fails, no conflict can be detected
  if (!slot1 || !slot2) {
    return false
  }

  // Different days = no conflict
  if (slot1.day !== slot2.day) {
    return false
  }

  // Convert to minutes for easier comparison
  const slot1Start = timeToMinutes(slot1.startHour, slot1.startMinute)
  const slot1End = timeToMinutes(slot1.endHour, slot1.endMinute)
  const slot2Start = timeToMinutes(slot2.startHour, slot2.startMinute)
  const slot2End = timeToMinutes(slot2.endHour, slot2.endMinute)

  // Check for overlap
  // No overlap if: slot1 ends before slot2 starts OR slot2 ends before slot1 starts
  // We use < (not <=) because adjacent slots don't conflict
  if (slot1End <= slot2Start || slot2End <= slot1Start) {
    return false
  }

  return true
}

/**
 * Detect all time conflicts in a course schedule
 * Returns array of conflicts with course IDs and details
 */
export function detectTimeConflicts(courses: Course[]): Conflict[] {
  const conflicts: Conflict[] = []
  const conflictPairs = new Set<string>() // To avoid duplicate conflict reports

  // Check each pair of courses
  for (let i = 0; i < courses.length; i++) {
    for (let j = i + 1; j < courses.length; j++) {
      const course1 = courses[i]
      const course2 = courses[j]

      if (hasConflict(course1.time, course2.time)) {
        // Create a unique key for this conflict pair (sorted to avoid duplicates)
        const key = [course1.id, course2.id].sort().join('-')

        if (!conflictPairs.has(key)) {
          conflictPairs.add(key)

          conflicts.push({
            courseIds: [course1.id, course2.id],
            message: `Time conflict detected between ${course1.crs_no || `Course ${course1.id}`} and ${course2.crs_no || `Course ${course2.id}`}`,
            severity: 'error',
          })
        }
      }
    }
  }

  return conflicts
}
