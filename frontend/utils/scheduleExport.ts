/**
 * Schedule Export Utility
 * Handles exporting schedules to various formats (iCal, Google Calendar, JSON)
 */

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

/**
 * Generate iCal format string for schedule export
 * Creates a valid VCALENDAR with VEVENT entries for each course
 */
export function generateICalFormat(courses: Course[]): string {
  const now = new Date()
  const formattedDate = formatICalDate(now)

  let ical = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NYCU Course Platform//Schedule Export//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:NYCU Schedule
X-WR-TIMEZONE:Asia/Taipei
X-WR-CALDESC:Exported course schedule
`

  // Add events for each course
  for (const course of courses) {
    const eventDate = generateEventDate(course)
    ical += `BEGIN:VEVENT
UID:${course.id}-${course.acy}-${course.sem}@nycu-courses
DTSTART:${eventDate.start}
DTEND:${eventDate.end}
RRULE:FREQ=WEEKLY;COUNT=18
SUMMARY:${escapeICalText(course.name)}
DESCRIPTION:${escapeICalText(`Course: ${course.crs_no}\nInstructor: ${course.teacher}\nLocation: ${course.classroom}\nCredits: ${course.credits}`)}
LOCATION:${escapeICalText(course.classroom)}
ORGANIZER;CN=${escapeICalText(course.teacher)}:mailto:instructor@nycu.edu.tw
CREATED:${formattedDate}
LAST-MODIFIED:${formattedDate}
DTSTAMP:${formattedDate}
END:VEVENT
`
  }

  ical += `END:VCALENDAR`

  return ical
}

/**
 * Generate Google Calendar URL for adding a course
 * Creates a shareable Google Calendar link
 */
export function generateGoogleCalendarUrl(course: Course): string {
  const eventDate = generateEventDate(course)
  const title = encodeURIComponent(course.name)
  const details = encodeURIComponent(
    `${course.crs_no}\nInstructor: ${course.teacher}\nLocation: ${course.classroom}\nCredits: ${course.credits}`
  )
  const location = encodeURIComponent(course.classroom)

  // Format dates for Google Calendar (YYYYMMDD'T'HHMMSS'Z')
  const startDate = eventDate.start.replace(/[\D]/g, '').substring(0, 15)
  const endDate = eventDate.end.replace(/[\D]/g, '').substring(0, 15)

  const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&title=${title}&dates=${startDate}/${endDate}&location=${location}&details=${details}`

  return url
}

/**
 * Export schedule as JSON string
 * Includes all course details
 */
export function exportScheduleToJSON(courses: Course[]): string {
  const exportData = courses.map((course) => ({
    id: course.id,
    crs_no: course.crs_no,
    name: course.name,
    teacher: course.teacher,
    credits: course.credits,
    dept: course.dept,
    time: course.time,
    classroom: course.classroom,
    acy: course.acy,
    sem: course.sem,
  }))

  return JSON.stringify(exportData, null, 2)
}

/**
 * Validate export data
 * Checks if provided data has all required fields for a valid course
 */
export function validateExportData(data: any): boolean {
  if (!Array.isArray(data)) {
    return false
  }

  if (data.length === 0) {
    return false
  }

  // Required fields for a valid course
  const requiredFields = [
    'id',
    'crs_no',
    'name',
    'teacher',
    'credits',
    'dept',
    'time',
    'classroom',
    'acy',
    'sem',
  ]

  // Check if all items have required fields
  return data.every((item) => {
    if (typeof item !== 'object' || item === null) {
      return false
    }
    return requiredFields.every((field) => field in item)
  })
}

/**
 * Helper: Format date for iCal format (YYYYMMDD'T'HHMMSS'Z')
 */
function formatICalDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  return `${year}${month}${day}T${hours}${minutes}${seconds}Z`
}

/**
 * Helper: Generate event start and end dates based on course time
 * Parses "Day HH:MM-HH:MM" format
 */
function generateEventDate(course: Course): { start: string; end: string } {
  // Parse course time: "Mon 09:00-11:00"
  const timeRegex = /(\w+)\s+(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})/
  const match = course.time.match(timeRegex)

  if (!match) {
    // Fallback to current date if parsing fails
    const today = new Date()
    const start = formatICalDate(today)
    const end = formatICalDate(new Date(today.getTime() + 2 * 60 * 60 * 1000))
    return { start, end }
  }

  const [, dayName, startHour, startMin, endHour, endMin] = match

  // Map day name to date (use next occurrence of that day)
  const dayMap: Record<string, number> = {
    Mon: 1,
    Tue: 2,
    Wed: 3,
    Thu: 4,
    Fri: 5,
    Sat: 6,
    Sun: 0,
  }

  const targetDayOfWeek = dayMap[dayName] || 1
  const today = new Date()
  const currentDay = today.getDay()
  const daysUntilTarget = (targetDayOfWeek - currentDay + 7) % 7 || 7

  const courseDate = new Date(today)
  courseDate.setDate(courseDate.getDate() + daysUntilTarget)

  // Set start time
  const startDate = new Date(courseDate)
  startDate.setHours(parseInt(startHour, 10), parseInt(startMin, 10), 0, 0)

  // Set end time
  const endDate = new Date(courseDate)
  endDate.setHours(parseInt(endHour, 10), parseInt(endMin, 10), 0, 0)

  return {
    start: formatICalDate(startDate),
    end: formatICalDate(endDate),
  }
}

/**
 * Helper: Escape special characters for iCal format
 * Handles commas, newlines, and quotes
 */
function escapeICalText(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/,/g, '\\,')
    .replace(/;/g, '\\;')
    .replace(/\n/g, '\\n')
}
