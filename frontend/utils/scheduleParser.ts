/**
 * NYCU Course Schedule Parser Utility
 *
 * Converts NYCU time codes and day codes into human-readable schedule format.
 *
 * NYCU stores schedule information as codes:
 * - day_codes: "135" means Monday(1), Wednesday(3), Friday(5)
 * - time_codes: "89A" means 14:00-15:00(8), 15:00-16:00(9), 16:00-17:00(A)
 * - classroom_codes: "A101,B202" (already readable)
 *
 * This utility converts codes to human-readable format like:
 * "Mon/Wed/Fri 14:00-17:00 (A101, B202)"
 */

/**
 * Mapping of time codes to standard Taiwan university time slots
 * Taiwan university typically uses 10-minute lessons with standard time slots
 */
const TIME_CODE_MAP: Record<string, { start: string; end: string }> = {
  '1': { start: '07:00', end: '08:00' },
  '2': { start: '08:00', end: '09:00' },
  '3': { start: '09:00', end: '10:00' },
  '4': { start: '10:00', end: '11:00' },
  '5': { start: '11:00', end: '12:00' },
  '6': { start: '12:00', end: '13:00' },
  '7': { start: '13:00', end: '14:00' },
  '8': { start: '14:00', end: '15:00' },
  '9': { start: '15:00', end: '16:00' },
  'A': { start: '16:00', end: '17:00' },
  'B': { start: '17:00', end: '18:00' },
  'C': { start: '18:00', end: '19:00' },
  'D': { start: '19:00', end: '20:00' },
  'E': { start: '20:00', end: '21:00' },
  'F': { start: '21:00', end: '22:00' },
};

/**
 * Day code to English day name mapping
 */
const DAY_CODE_MAP_EN: Record<string, string> = {
  '1': 'Mon',
  '2': 'Tue',
  '3': 'Wed',
  '4': 'Thu',
  '5': 'Fri',
  '6': 'Sat',
  '7': 'Sun',
};

/**
 * Day code to Traditional Chinese day name mapping
 */
const DAY_CODE_MAP_ZH: Record<string, string> = {
  '1': '一',
  '2': '二',
  '3': '三',
  '4': '四',
  '5': '五',
  '6': '六',
  '7': '日',
};

/**
 * Parse time codes to get start and end times
 *
 * @param timeCodes - String of time codes (e.g., "89A")
 * @returns Object with start and end times, or null if invalid
 */
export function parseTimeRange(
  timeCodes: string | undefined | null
): { start: string; end: string } | null {
  if (!timeCodes || timeCodes.length === 0) return null;

  const codes = timeCodes.split('');
  const firstCode = codes[0];
  const lastCode = codes[codes.length - 1];

  const firstSlot = TIME_CODE_MAP[firstCode];
  const lastSlot = TIME_CODE_MAP[lastCode];

  if (!firstSlot || !lastSlot) return null;

  return {
    start: firstSlot.start,
    end: lastSlot.end,
  };
}

/**
 * Parse day codes to get readable day format
 *
 * @param dayCodes - String of day codes (e.g., "135")
 * @param lang - Language ('en' for English, 'zh' for Traditional Chinese)
 * @returns String of day names (e.g., "Mon/Wed/Fri" or "一/三/五")
 */
export function parseDays(
  dayCodes: string | undefined | null,
  lang: 'en' | 'zh' = 'en'
): string {
  if (!dayCodes || dayCodes.length === 0) return 'N/A';

  const dayMap = lang === 'en' ? DAY_CODE_MAP_EN : DAY_CODE_MAP_ZH;
  const separator = lang === 'en' ? '/' : '/';

  const days = dayCodes
    .split('')
    .map((d) => dayMap[d])
    .filter(Boolean);

  return days.length > 0 ? days.join(separator) : 'N/A';
}

/**
 * Format time range as readable string
 *
 * @param timeCodes - String of time codes (e.g., "89A")
 * @returns Formatted time range (e.g., "14:00-17:00") or "N/A"
 */
export function formatTimeRange(
  timeCodes: string | undefined | null
): string {
  const timeRange = parseTimeRange(timeCodes);
  if (!timeRange) return 'N/A';
  return `${timeRange.start}-${timeRange.end}`;
}

/**
 * Format classrooms as readable string
 *
 * @param classroomCodes - Comma-separated classroom codes (e.g., "A101,B202")
 * @returns Formatted classroom string
 */
export function formatClassrooms(
  classroomCodes: string | undefined | null
): string {
  if (!classroomCodes) return 'TBA';
  return classroomCodes.split(',').map((c) => c.trim()).join(', ');
}

/**
 * Complete schedule formatter - main entry point
 *
 * Combines day codes, time codes, and classrooms into a complete schedule string
 *
 * @param dayCodes - Day codes (e.g., "135")
 * @param timeCodes - Time codes (e.g., "89A")
 * @param classrooms - Classroom codes (e.g., "A101,B202")
 * @param lang - Language ('en' or 'zh')
 * @returns Complete schedule string (e.g., "Mon/Wed/Fri 14:00-17:00 (A101, B202)")
 */
export function formatSchedule(
  dayCodes: string | undefined | null,
  timeCodes: string | undefined | null,
  classrooms: string | undefined | null,
  lang: 'en' | 'zh' = 'en'
): string {
  const days = parseDays(dayCodes, lang);
  const time = formatTimeRange(timeCodes);
  const rooms = formatClassrooms(classrooms);

  // Handle cases where schedule information is incomplete
  if (days === 'N/A' && time === 'N/A') {
    return 'TBA';
  }

  const parts = [];
  if (days !== 'N/A') parts.push(days);
  if (time !== 'N/A') parts.push(time);

  const schedule = parts.join(' ');
  return rooms && rooms !== 'TBA' ? `${schedule} (${rooms})` : schedule;
}

/**
 * Get day name from day code
 *
 * @param dayCode - Single day code (e.g., "1")
 * @param lang - Language ('en' or 'zh')
 * @returns Day name (e.g., "Mon" or "一")
 */
export function getDayName(
  dayCode: string,
  lang: 'en' | 'zh' = 'en'
): string {
  const dayMap = lang === 'en' ? DAY_CODE_MAP_EN : DAY_CODE_MAP_ZH;
  return dayMap[dayCode] || 'Unknown';
}

/**
 * Get time slot from time code
 *
 * @param timeCode - Single time code (e.g., "8")
 * @returns Time range (e.g., "14:00-15:00")
 */
export function getTimeSlot(timeCode: string): string {
  const slot = TIME_CODE_MAP[timeCode];
  if (!slot) return 'N/A';
  return `${slot.start}-${slot.end}`;
}

/**
 * Check if schedule has complete information
 *
 * @param dayCodes - Day codes
 * @param timeCodes - Time codes
 * @returns Boolean indicating if schedule has any information
 */
export function hasSchedule(
  dayCodes: string | undefined | null,
  timeCodes: string | undefined | null
): boolean {
  return (
    (dayCodes && dayCodes.length > 0) ||
    (timeCodes && timeCodes.length > 0)
  );
}

/**
 * Format schedule for display in Chinese
 * Convenience function that calls formatSchedule with lang='zh'
 *
 * @param dayCodes - Day codes
 * @param timeCodes - Time codes
 * @param classrooms - Classroom codes
 * @returns Schedule string in Chinese
 */
export function formatScheduleZH(
  dayCodes: string | undefined | null,
  timeCodes: string | undefined | null,
  classrooms: string | undefined | null
): string {
  return formatSchedule(dayCodes, timeCodes, classrooms, 'zh');
}

/**
 * Format schedule for display in English
 * Convenience function that calls formatSchedule with lang='en'
 *
 * @param dayCodes - Day codes
 * @param timeCodes - Time codes
 * @param classrooms - Classroom codes
 * @returns Schedule string in English
 */
export function formatScheduleEN(
  dayCodes: string | undefined | null,
  timeCodes: string | undefined | null,
  classrooms: string | undefined | null
): string {
  return formatSchedule(dayCodes, timeCodes, classrooms, 'en');
}

// Export all functions as namespace for convenience imports
export const ScheduleParser = {
  parseTimeRange,
  parseDays,
  formatTimeRange,
  formatClassrooms,
  formatSchedule,
  getDayName,
  getTimeSlot,
  hasSchedule,
  formatScheduleZH,
  formatScheduleEN,
};

// Example usage:
/*
const course = {
  day_codes: "135",
  time_codes: "89A",
  classroom_codes: "A101,B202"
};

// English format
formatSchedule(course.day_codes, course.time_codes, course.classroom_codes, 'en')
// Output: "Mon/Wed/Fri 14:00-17:00 (A101, B202)"

// Chinese format
formatSchedule(course.day_codes, course.time_codes, course.classroom_codes, 'zh')
// Output: "一/三/五 14:00-17:00 (A101, B202)"

// Alternative usage
formatScheduleZH("135", "89A", "A101,B202")
// Output: "一/三/五 14:00-17:00 (A101, B202)"
*/
