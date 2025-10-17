import { detectTimeConflicts, parseTimeSlot, hasConflict } from '@/utils/conflictDetection'

describe('Conflict Detection Utils', () => {
  const mockCourse1 = {
    id: 1,
    time: 'Mon 09:00-11:00',
    crs_no: 'CS0101',
  }

  const mockCourse2 = {
    id: 2,
    time: 'Mon 10:00-12:00', // Overlaps with course1
    crs_no: 'CS0102',
  }

  const mockCourse3 = {
    id: 3,
    time: 'Wed 14:00-16:00', // No conflict
    crs_no: 'CS0103',
  }

  describe('parseTimeSlot', () => {
    it('parses valid time slot', () => {
      const result = parseTimeSlot('Mon 09:00-11:00')
      expect(result).toEqual({
        day: 'Mon',
        startHour: 9,
        startMinute: 0,
        endHour: 11,
        endMinute: 0,
      })
    })

    it('handles different time formats', () => {
      const result = parseTimeSlot('Wed 14:30-16:45')
      expect(result.startHour).toBe(14)
      expect(result.startMinute).toBe(30)
      expect(result.endHour).toBe(16)
      expect(result.endMinute).toBe(45)
    })

    it('returns null for invalid format', () => {
      const result = parseTimeSlot('Invalid')
      expect(result).toBeNull()
    })
  })

  describe('hasConflict', () => {
    it('detects time conflict on same day', () => {
      const conflict = hasConflict(mockCourse1.time, mockCourse2.time)
      expect(conflict).toBe(true)
    })

    it('no conflict on different days', () => {
      const conflict = hasConflict(mockCourse1.time, mockCourse3.time)
      expect(conflict).toBe(false)
    })

    it('no conflict for adjacent time slots', () => {
      const conflict = hasConflict('Mon 09:00-11:00', 'Mon 11:00-13:00')
      expect(conflict).toBe(false)
    })

    it('detects partial overlap', () => {
      const conflict = hasConflict('Mon 10:30-12:30', 'Mon 11:00-13:00')
      expect(conflict).toBe(true)
    })
  })

  describe('detectTimeConflicts', () => {
    it('returns empty array for no conflicts', () => {
      const courses = [mockCourse1, mockCourse3]
      const conflicts = detectTimeConflicts(courses)
      expect(conflicts).toEqual([])
    })

    it('detects conflicts between multiple courses', () => {
      const courses = [mockCourse1, mockCourse2, mockCourse3]
      const conflicts = detectTimeConflicts(courses)
      expect(conflicts.length).toBeGreaterThan(0)
      expect(conflicts[0].courseIds).toContain(1)
      expect(conflicts[0].courseIds).toContain(2)
    })

    it('returns conflict details', () => {
      const courses = [mockCourse1, mockCourse2]
      const conflicts = detectTimeConflicts(courses)
      expect(conflicts[0]).toHaveProperty('courseIds')
      expect(conflicts[0]).toHaveProperty('message')
      expect(conflicts[0]).toHaveProperty('severity')
    })
  })
})
