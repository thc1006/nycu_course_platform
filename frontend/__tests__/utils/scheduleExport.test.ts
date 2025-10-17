import {
  generateICalFormat,
  generateGoogleCalendarUrl,
  exportScheduleToJSON,
  validateExportData
} from '@/utils/scheduleExport'

describe('Schedule Export Utils', () => {
  const mockCourse = {
    id: 1,
    crs_no: 'CS0101',
    name: 'Intro to Programming',
    teacher: 'Dr. Smith',
    credits: 3,
    dept: 'CS',
    time: 'Mon 09:00-11:00',
    classroom: 'A101',
    acy: 113,
    sem: 1,
  }

  describe('generateICalFormat', () => {
    it('generates valid iCal format', () => {
      const ical = generateICalFormat([mockCourse])
      expect(ical).toContain('BEGIN:VCALENDAR')
      expect(ical).toContain('END:VCALENDAR')
      expect(ical).toContain('BEGIN:VEVENT')
      expect(ical).toContain('END:VEVENT')
    })

    it('includes course details', () => {
      const ical = generateICalFormat([mockCourse])
      expect(ical).toContain('Intro to Programming')
      expect(ical).toContain('Dr. Smith')
      expect(ical).toContain('A101')
    })

    it('returns downloadable file content', () => {
      const ical = generateICalFormat([mockCourse])
      expect(typeof ical).toBe('string')
      expect(ical.length).toBeGreaterThan(0)
    })

    it('handles multiple courses', () => {
      const courses = [
        mockCourse,
        { ...mockCourse, id: 2, crs_no: 'CS0102', name: 'Data Structures' }
      ]
      const ical = generateICalFormat(courses)
      expect((ical.match(/BEGIN:VEVENT/g) || []).length).toBe(2)
    })
  })

  describe('generateGoogleCalendarUrl', () => {
    it('generates valid Google Calendar URL', () => {
      const url = generateGoogleCalendarUrl(mockCourse)
      expect(url).toContain('https://calendar.google.com')
      expect(url).toContain('title=')
      expect(url).toContain('dates=')
    })

    it('includes course title', () => {
      const url = generateGoogleCalendarUrl(mockCourse)
      expect(url).toContain(encodeURIComponent('Intro to Programming'))
    })

    it('includes course details in description', () => {
      const url = generateGoogleCalendarUrl(mockCourse)
      expect(url).toContain('details=')
    })
  })

  describe('exportScheduleToJSON', () => {
    it('exports schedule as JSON', () => {
      const json = exportScheduleToJSON([mockCourse])
      const parsed = JSON.parse(json)
      expect(Array.isArray(parsed)).toBe(true)
      expect(parsed[0].id).toBe(mockCourse.id)
    })

    it('includes all course fields', () => {
      const json = exportScheduleToJSON([mockCourse])
      const parsed = JSON.parse(json)
      expect(parsed[0]).toHaveProperty('crs_no')
      expect(parsed[0]).toHaveProperty('name')
      expect(parsed[0]).toHaveProperty('teacher')
    })

    it('handles multiple courses', () => {
      const courses = [
        mockCourse,
        { ...mockCourse, id: 2, crs_no: 'CS0102' }
      ]
      const json = exportScheduleToJSON(courses)
      const parsed = JSON.parse(json)
      expect(parsed.length).toBe(2)
    })
  })

  describe('validateExportData', () => {
    it('validates correct export data', () => {
      const isValid = validateExportData([mockCourse])
      expect(isValid).toBe(true)
    })

    it('rejects invalid data', () => {
      const isValid = validateExportData([{ invalid: 'data' }])
      expect(isValid).toBe(false)
    })

    it('requires essential fields', () => {
      const incompleteCourse = { id: 1, name: 'Test' } // Missing required fields
      const isValid = validateExportData([incompleteCourse])
      expect(isValid).toBe(false)
    })
  })
})
