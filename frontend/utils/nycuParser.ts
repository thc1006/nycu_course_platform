/**
 * NYCU Course Time and Classroom Parser
 *
 * Parses NYCU timetable format strings into structured data.
 * Format: "M56R2-ED201[GF]"
 * - M56 = Monday periods 5-6
 * - R2 = Thursday period 2
 * - ED201[GF] = Engineering Building 2, Room 201, General Floor
 */

// Type Definitions
export interface ScheduleInfo {
  dayCode: string;
  dayName: string;
  dayNameZh: string;
  periods: number[];
  periodRange: string;
}

export interface ClassroomInfo {
  buildingCode: string;
  buildingName: string;
  buildingNameZh: string;
  roomNumber: string;
  floor: string | null;
  fullCode: string;
  displayName: string;
}

export interface TimeClassroomInfo {
  schedule: ScheduleInfo[];
  classroom: ClassroomInfo | null;
  additionalClassrooms?: ClassroomInfo[];
  originalString: string;
}

// Day code mappings
const DAY_CODES: Record<string, { name: string; nameZh: string; short: string }> = {
  M: { name: 'Monday', nameZh: '星期一', short: 'Mon' },
  T: { name: 'Tuesday', nameZh: '星期二', short: 'Tue' },
  W: { name: 'Wednesday', nameZh: '星期三', short: 'Wed' },
  R: { name: 'Thursday', nameZh: '星期四', short: 'Thu' },
  F: { name: 'Friday', nameZh: '星期五', short: 'Fri' },
  S: { name: 'Saturday', nameZh: '星期六', short: 'Sat' },
  U: { name: 'Sunday', nameZh: '星期日', short: 'Sun' },
};

// Building code mappings (common NYCU buildings)
const BUILDING_CODES: Record<string, { name: string; nameZh: string }> = {
  EC: { name: 'Engineering Building 1', nameZh: '工程一館' },
  ED: { name: 'Engineering Building 2', nameZh: '工程二館' },
  EE: { name: 'Engineering Building 3', nameZh: '工程三館' },
  EF: { name: 'Engineering Building 4', nameZh: '工程四館' },
  EG: { name: 'Engineering Building 5', nameZh: '工程五館' },
  EH: { name: 'Engineering Building 6', nameZh: '工程六館' },
  SC: { name: 'Science Building 3', nameZh: '科學三館' },
  CS: { name: 'Computer Science Building', nameZh: '資訊科學館' },
  LA: { name: 'Liberal Arts Building', nameZh: '人社一館' },
  LB: { name: 'Liberal Arts Building 2', nameZh: '人社二館' },
  HA: { name: 'Hsinchu Campus General Building', nameZh: '綜合一館' },
  HB: { name: 'Hsinchu Campus General Building 2', nameZh: '綜合二館' },
  HC: { name: 'Hsinchu Campus General Building 3', nameZh: '綜合三館' },
  HK: { name: 'Hsinchu Campus General Building K', nameZh: '綜合K館' },
  // Default for unknown codes
  DEFAULT: { name: 'Building', nameZh: '館' },
};

/**
 * Format day code to short form (e.g., 'M' -> 'Mon')
 */
export function formatDayCode(dayCode: string): string {
  return DAY_CODES[dayCode]?.short || dayCode;
}

/**
 * Format period array to range string (e.g., [5, 6] -> '5-6', [1, 3, 5] -> '1, 3, 5')
 */
export function formatPeriodRange(periods: number[]): string {
  if (periods.length === 0) return '';
  if (periods.length === 1) return periods[0].toString();

  // Sort periods
  const sorted = [...periods].sort((a, b) => a - b);

  // Group continuous periods
  const groups: number[][] = [];
  let currentGroup: number[] = [sorted[0]];

  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] === sorted[i - 1] + 1) {
      currentGroup.push(sorted[i]);
    } else {
      groups.push(currentGroup);
      currentGroup = [sorted[i]];
    }
  }
  groups.push(currentGroup);

  // Format groups
  return groups
    .map(group => {
      if (group.length === 1) return group[0].toString();
      if (group.length === 2) return `${group[0]}-${group[1]}`;
      return `${group[0]}-${group[group.length - 1]}`;
    })
    .join(', ');
}

/**
 * Parse NYCU schedule string (e.g., "M56R2" -> [{ dayCode: 'M', periods: [5, 6] }, ...])
 */
export function parseNYCUSchedule(scheduleString: string | null | undefined): ScheduleInfo[] {
  if (!scheduleString || scheduleString.trim() === '') {
    return [];
  }

  const result: ScheduleInfo[] = [];
  let i = 0;

  while (i < scheduleString.length) {
    const char = scheduleString[i];

    // Check if it's a day code
    if (DAY_CODES[char]) {
      const dayCode = char;
      const dayInfo = DAY_CODES[dayCode];
      i++;

      // Extract period numbers
      const periods: number[] = [];
      while (i < scheduleString.length) {
        const nextChar = scheduleString[i];

        // If we hit another day code, break
        if (DAY_CODES[nextChar]) {
          break;
        }

        // If it's a digit, extract the number
        if (/\d/.test(nextChar)) {
          // Check for two-digit period (only 10 and 11 are treated as two-digit periods)
          // 12, 13, 14 are parsed as single digits (1,2 / 1,3 / 1,4) as this is more common in practice
          if (nextChar === '1' && i + 1 < scheduleString.length && /\d/.test(scheduleString[i + 1])) {
            const secondDigit = scheduleString[i + 1];
            if (secondDigit === '0' || secondDigit === '1') {
              // Only treat 10 and 11 as two-digit periods
              periods.push(parseInt(scheduleString.slice(i, i + 2), 10));
              i += 2;
              continue;
            }
          }
          // Single digit period
          periods.push(parseInt(nextChar, 10));
          i++;
        } else {
          // Non-digit, non-day-code character, skip it
          i++;
        }
      }

      if (periods.length > 0) {
        result.push({
          dayCode,
          dayName: dayInfo.name,
          dayNameZh: dayInfo.nameZh,
          periods,
          periodRange: formatPeriodRange(periods),
        });
      }
    } else {
      // Skip unknown characters
      i++;
    }
  }

  return result;
}

/**
 * Parse NYCU classroom string (e.g., "ED201[GF]" -> { buildingCode: 'ED', roomNumber: '201', ... })
 */
export function parseNYCUClassroom(classroomString: string | null | undefined): ClassroomInfo | null {
  if (!classroomString || classroomString.trim() === '') {
    return null;
  }

  // Extract building code (2-3 letter prefix)
  const buildingMatch = classroomString.match(/^([A-Z]{2,3})/);
  if (!buildingMatch) {
    return null;
  }

  const buildingCode = buildingMatch[1];
  const buildingInfo = BUILDING_CODES[buildingCode] || BUILDING_CODES.DEFAULT;

  // Extract room number
  const roomMatch = classroomString.match(/([A-Z]{2,3})(\d+)/);
  const roomNumber = roomMatch ? roomMatch[2] : '';

  // Extract floor info (optional, in brackets)
  const floorMatch = classroomString.match(/\[([^\]]+)\]/);
  const floor = floorMatch ? floorMatch[1] : null;

  // Create display name (without floor brackets)
  const displayName = classroomString.replace(/\[.*?\]/, '').trim();

  return {
    buildingCode,
    buildingName: buildingInfo.name,
    buildingNameZh: buildingInfo.nameZh,
    roomNumber,
    floor,
    fullCode: classroomString,
    displayName,
  };
}

/**
 * Parse complete time-classroom string (e.g., "M56R2-ED201[GF]")
 * Supports multiple formats:
 * - "M56R2-ED201[GF]" - single classroom
 * - "W12-EC114,R34-SC101" - multiple time-classroom pairs
 * - "M56R2" - time only (no classroom)
 */
export function parseTimeClassroom(timeClassroomString: string | null | undefined): TimeClassroomInfo | null {
  if (!timeClassroomString || timeClassroomString.trim() === '') {
    return null;
  }

  const originalString = timeClassroomString;

  // Check if there are multiple time-classroom pairs (comma-separated)
  if (timeClassroomString.includes(',')) {
    // Parse multiple pairs like "W12-EC114,R34-SC101"
    const pairs = timeClassroomString.split(',').map(p => p.trim());
    const allSchedules: ScheduleInfo[] = [];
    const classrooms: ClassroomInfo[] = [];

    pairs.forEach(pair => {
      const [timePart, classroomPart] = pair.split('-').map(s => s.trim());
      if (timePart) {
        const schedule = parseNYCUSchedule(timePart);
        allSchedules.push(...schedule);
      }
      if (classroomPart) {
        const classroom = parseNYCUClassroom(classroomPart);
        if (classroom) {
          classrooms.push(classroom);
        }
      }
    });

    return {
      schedule: allSchedules,
      classroom: classrooms.length > 0 ? classrooms[0] : null,
      additionalClassrooms: classrooms.length > 1 ? classrooms.slice(1) : undefined,
      originalString,
    };
  }

  // Single format: "M56R2-ED201[GF]" or "M56R2"
  const [timePart, classroomPart] = timeClassroomString.split('-').map(s => s?.trim());

  const schedule = parseNYCUSchedule(timePart || '');
  const classroom = classroomPart ? parseNYCUClassroom(classroomPart) : null;

  return {
    schedule,
    classroom,
    originalString,
  };
}

/**
 * Format schedule info to display string
 * @param schedule - Parsed schedule info
 * @param lang - Language ('zh' or 'en')
 * @returns Formatted string (e.g., "Mon 5-6, Thu 2" or "週一 5-6, 週四 2")
 */
export function formatScheduleDisplay(schedule: ScheduleInfo[], lang: 'zh' | 'en' = 'en'): string {
  if (!schedule || schedule.length === 0) {
    return lang === 'zh' ? '未排定' : 'TBA';
  }

  return schedule
    .map(s => {
      const day = lang === 'zh' ? s.dayNameZh : formatDayCode(s.dayCode);
      return `${day} ${s.periodRange}`;
    })
    .join(', ');
}

/**
 * Format classroom info to display string
 * @param classroom - Parsed classroom info
 * @param lang - Language ('zh' or 'en')
 * @returns Formatted string (e.g., "ED201 (工程二館)" or "ED201")
 */
export function formatClassroomDisplay(classroom: ClassroomInfo | null, lang: 'zh' | 'en' = 'en'): string {
  if (!classroom) {
    return lang === 'zh' ? '未排定' : 'TBA';
  }

  if (lang === 'zh') {
    return `${classroom.displayName} (${classroom.buildingNameZh})`;
  }

  return classroom.displayName;
}

/**
 * Parse course details JSON string and extract time/classroom info
 * @param detailsString - JSON string from course.details field
 * @returns Parsed time-classroom info or null
 */
export function parseCourseDetails(detailsString: string | null | undefined): TimeClassroomInfo | null {
  if (!detailsString) {
    return null;
  }

  try {
    const details = JSON.parse(detailsString);
    if (details.time_classroom) {
      return parseTimeClassroom(details.time_classroom);
    }
  } catch (e) {
    console.error('Failed to parse course details:', e);
  }

  return null;
}
