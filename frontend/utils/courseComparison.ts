/**
 * Course Comparison Utility
 * Handles comparing courses and identifying differences
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

interface ComparisonRow {
  field: string
  valueA: any
  valueB: any
  isDifferent: boolean
}

interface ComparisonData {
  rows: ComparisonRow[]
  courseA: Course
  courseB: Course
}

interface CourseComparison {
  courseA: Course
  courseB: Course
}

/**
 * Compare two courses and return comparison object
 * Returns null if only one course or zero courses provided
 */
export function compareCourses(courses: Course[]): CourseComparison | null {
  if (courses.length < 2) {
    return null
  }

  // Return comparison of first two courses
  return {
    courseA: courses[0],
    courseB: courses[1],
  }
}

/**
 * Get list of fields that differ between two courses
 * Returns array of field names that are different
 */
export function getComparisonDifferences(
  courseA: Course,
  courseB: Course
): string[] {
  const differences: string[] = []

  // Define fields to compare
  const fieldsToCompare: (keyof Course)[] = [
    'name',
    'teacher',
    'credits',
    'time',
    'classroom',
    'dept',
    'crs_no',
    'acy',
    'sem',
  ]

  for (const field of fieldsToCompare) {
    if (courseA[field] !== courseB[field]) {
      differences.push(field)
    }
  }

  return differences
}

/**
 * Format comparison data for display
 * Returns object with rows containing both values and difference indicator
 */
export function formatComparisonData(
  courseA: Course,
  courseB: Course
): ComparisonData {
  const differences = getComparisonDifferences(courseA, courseB)
  const differenceSet = new Set(differences)

  // Fields to display in comparison
  const displayFields: (keyof Course)[] = [
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

  const rows: ComparisonRow[] = displayFields.map((field) => ({
    field: field, // Keep original field name for testing
    valueA: courseA[field],
    valueB: courseB[field],
    isDifferent: differenceSet.has(field),
  }))

  return {
    rows,
    courseA,
    courseB,
  }
}

/**
 * Format field name for display
 * Converts camelCase to Title Case
 */
function formatFieldName(field: string): string {
  const fieldNames: Record<string, string> = {
    crs_no: 'Course Number',
    name: 'Course Name',
    teacher: 'Instructor',
    credits: 'Credits',
    dept: 'Department',
    time: 'Time',
    classroom: 'Classroom',
    acy: 'Academic Year',
    sem: 'Semester',
  }

  return fieldNames[field] || field
}
