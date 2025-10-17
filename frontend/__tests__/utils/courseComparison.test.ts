import { compareCourses, getComparisonDifferences, formatComparisonData } from '@/utils/courseComparison'

describe('Course Comparison Utils', () => {
  const mockCourseA = {
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

  const mockCourseB = {
    id: 2,
    crs_no: 'CS0102',
    name: 'Data Structures',
    teacher: 'Prof. Johnson',
    credits: 4,
    dept: 'CS',
    time: 'Wed 13:00-15:00',
    classroom: 'A102',
    acy: 113,
    sem: 1,
  }

  describe('compareCourses', () => {
    it('compares two courses', () => {
      const comparison = compareCourses([mockCourseA, mockCourseB])
      expect(comparison).toHaveProperty('courseA')
      expect(comparison).toHaveProperty('courseB')
      expect(comparison.courseA.id).toBe(mockCourseA.id)
      expect(comparison.courseB.id).toBe(mockCourseB.id)
    })

    it('returns null for single course', () => {
      const comparison = compareCourses([mockCourseA])
      expect(comparison).toBeNull()
    })

    it('handles more than 2 courses', () => {
      const comparison = compareCourses([mockCourseA, mockCourseB])
      expect(comparison).not.toBeNull()
    })
  })

  describe('getComparisonDifferences', () => {
    it('identifies different fields', () => {
      const differences = getComparisonDifferences(mockCourseA, mockCourseB)
      expect(differences).toContain('credits')
      expect(differences).toContain('name')
      expect(differences).toContain('teacher')
    })

    it('returns empty array for identical courses', () => {
      const differences = getComparisonDifferences(mockCourseA, mockCourseA)
      expect(differences).toEqual([])
    })

    it('marks matching fields', () => {
      const differences = getComparisonDifferences(mockCourseA, mockCourseB)
      expect(differences).not.toContain('dept')
      expect(differences).not.toContain('acy')
    })
  })

  describe('formatComparisonData', () => {
    it('formats comparison for display', () => {
      const formatted = formatComparisonData(mockCourseA, mockCourseB)
      expect(formatted).toHaveProperty('rows')
      expect(formatted.rows.length).toBeGreaterThan(0)
    })

    it('each row has both values', () => {
      const formatted = formatComparisonData(mockCourseA, mockCourseB)
      formatted.rows.forEach(row => {
        expect(row).toHaveProperty('field')
        expect(row).toHaveProperty('valueA')
        expect(row).toHaveProperty('valueB')
        expect(row).toHaveProperty('isDifferent')
      })
    })

    it('highlights differences', () => {
      const formatted = formatComparisonData(mockCourseA, mockCourseB)
      const creditRow = formatted.rows.find(r => r.field === 'credits')
      expect(creditRow?.isDifferent).toBe(true)
    })
  })
})
