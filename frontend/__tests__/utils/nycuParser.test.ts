/**
 * TDD Tests for NYCU Time/Classroom Parser
 *
 * Format: "M56R2-ED201[GF]"
 * - M56 = Monday periods 5-6
 * - R2 = Thursday period 2
 * - ED201[GF] = Engineering Building 2, Room 201, General Floor
 *
 * Day codes: M (Mon), T (Tue), W (Wed), R (Thu), F (Fri), S (Sat), U (Sun)
 * Period codes: 1-14 (each number represents one period)
 */

import {
  parseNYCUSchedule,
  parseNYCUClassroom,
  parseTimeClassroom,
  formatDayCode,
  formatPeriodRange,
  type ScheduleInfo,
  type ClassroomInfo,
  type TimeClassroomInfo,
} from '@/utils/nycuParser';

describe('NYCU Parser - parseNYCUSchedule', () => {
  test('should parse single day with continuous periods', () => {
    const result = parseNYCUSchedule('M56');
    expect(result).toHaveLength(1);
    expect(result[0]).toEqual({
      dayCode: 'M',
      dayName: 'Monday',
      dayNameZh: '星期一',
      periods: [5, 6],
      periodRange: '5-6',
    });
  });

  test('should parse multiple days with different periods', () => {
    const result = parseNYCUSchedule('M56R2');
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({
      dayCode: 'M',
      dayName: 'Monday',
      dayNameZh: '星期一',
      periods: [5, 6],
      periodRange: '5-6',
    });
    expect(result[1]).toEqual({
      dayCode: 'R',
      dayName: 'Thursday',
      dayNameZh: '星期四',
      periods: [2],
      periodRange: '2',
    });
  });

  test('should parse Tuesday and Wednesday', () => {
    const result = parseNYCUSchedule('T34W12');
    expect(result).toHaveLength(2);
    expect(result[0].dayCode).toBe('T');
    expect(result[0].dayName).toBe('Tuesday');
    expect(result[0].periods).toEqual([3, 4]);
    expect(result[1].dayCode).toBe('W');
    expect(result[1].dayName).toBe('Wednesday');
    expect(result[1].periods).toEqual([1, 2]);
  });

  test('should parse Friday and Saturday', () => {
    const result = parseNYCUSchedule('F789S5');
    expect(result[0].dayCode).toBe('F');
    expect(result[0].dayName).toBe('Friday');
    expect(result[0].periods).toEqual([7, 8, 9]);
    expect(result[1].dayCode).toBe('S');
    expect(result[1].dayName).toBe('Saturday');
  });

  test('should handle single period', () => {
    const result = parseNYCUSchedule('M1');
    expect(result[0].periods).toEqual([1]);
    expect(result[0].periodRange).toBe('1');
  });

  test('should handle multiple continuous periods', () => {
    const result = parseNYCUSchedule('M1234');
    expect(result[0].periods).toEqual([1, 2, 3, 4]);
    expect(result[0].periodRange).toBe('1-4');
  });

  test('should return empty array for empty string', () => {
    const result = parseNYCUSchedule('');
    expect(result).toEqual([]);
  });

  test('should return empty array for null/undefined', () => {
    expect(parseNYCUSchedule(null as any)).toEqual([]);
    expect(parseNYCUSchedule(undefined as any)).toEqual([]);
  });

  test('should handle two-digit periods (10-14)', () => {
    const result = parseNYCUSchedule('M1011');
    expect(result[0].periods).toEqual([10, 11]);
  });
});

describe('NYCU Parser - parseNYCUClassroom', () => {
  test('should parse standard classroom format', () => {
    const result = parseNYCUClassroom('ED201[GF]');
    expect(result).toEqual({
      buildingCode: 'ED',
      buildingName: 'Engineering Building 2',
      buildingNameZh: '工程二館',
      roomNumber: '201',
      floor: 'GF',
      fullCode: 'ED201[GF]',
      displayName: 'ED201',
    });
  });

  test('should parse science building', () => {
    const result = parseNYCUClassroom('SC101[1F]');
    expect(result).toEqual({
      buildingCode: 'SC',
      buildingName: 'Science Building 3',
      buildingNameZh: '科學三館',
      roomNumber: '101',
      floor: '1F',
      fullCode: 'SC101[1F]',
      displayName: 'SC101',
    });
  });

  test('should parse general building without floor info', () => {
    const result = parseNYCUClassroom('EC114');
    expect(result).toEqual({
      buildingCode: 'EC',
      buildingName: 'Engineering Building 1',
      buildingNameZh: '工程一館',
      roomNumber: '114',
      floor: null,
      fullCode: 'EC114',
      displayName: 'EC114',
    });
  });

  test('should handle null/undefined/empty', () => {
    expect(parseNYCUClassroom(null as any)).toBeNull();
    expect(parseNYCUClassroom(undefined as any)).toBeNull();
    expect(parseNYCUClassroom('')).toBeNull();
  });

  test('should parse computer science building', () => {
    const result = parseNYCUClassroom('CS123');
    expect(result?.buildingCode).toBe('CS');
    expect(result?.buildingNameZh).toBe('資訊科學館');
  });
});

describe('NYCU Parser - parseTimeClassroom', () => {
  test('should parse complete time-classroom string', () => {
    const result = parseTimeClassroom('M56R2-ED201[GF]');
    expect(result).toEqual({
      schedule: [
        {
          dayCode: 'M',
          dayName: 'Monday',
          dayNameZh: '星期一',
          periods: [5, 6],
          periodRange: '5-6',
        },
        {
          dayCode: 'R',
          dayName: 'Thursday',
          dayNameZh: '星期四',
          periods: [2],
          periodRange: '2',
        },
      ],
      classroom: {
        buildingCode: 'ED',
        buildingName: 'Engineering Building 2',
        buildingNameZh: '工程二館',
        roomNumber: '201',
        floor: 'GF',
        fullCode: 'ED201[GF]',
        displayName: 'ED201',
      },
      originalString: 'M56R2-ED201[GF]',
    });
  });

  test('should parse time-classroom with multiple classrooms', () => {
    const result = parseTimeClassroom('W12-EC114,R34-SC101');
    expect(result).toEqual({
      schedule: [
        {
          dayCode: 'W',
          dayName: 'Wednesday',
          dayNameZh: '星期三',
          periods: [1, 2],
          periodRange: '1-2',
        },
        {
          dayCode: 'R',
          dayName: 'Thursday',
          dayNameZh: '星期四',
          periods: [3, 4],
          periodRange: '3-4',
        },
      ],
      classroom: {
        buildingCode: 'EC',
        buildingName: 'Engineering Building 1',
        buildingNameZh: '工程一館',
        roomNumber: '114',
        floor: null,
        fullCode: 'EC114',
        displayName: 'EC114',
      },
      additionalClassrooms: [
        {
          buildingCode: 'SC',
          buildingName: 'Science Building 3',
          buildingNameZh: '科學三館',
          roomNumber: '101',
          floor: null,
          fullCode: 'SC101',
          displayName: 'SC101',
        },
      ],
      originalString: 'W12-EC114,R34-SC101',
    });
  });

  test('should handle null/undefined/empty string', () => {
    expect(parseTimeClassroom(null as any)).toBeNull();
    expect(parseTimeClassroom(undefined as any)).toBeNull();
    expect(parseTimeClassroom('')).toBeNull();
  });

  test('should parse time-only format (no classroom)', () => {
    const result = parseTimeClassroom('M56R2');
    expect(result).toEqual({
      schedule: [
        {
          dayCode: 'M',
          dayName: 'Monday',
          dayNameZh: '星期一',
          periods: [5, 6],
          periodRange: '5-6',
        },
        {
          dayCode: 'R',
          dayName: 'Thursday',
          dayNameZh: '星期四',
          periods: [2],
          periodRange: '2',
        },
      ],
      classroom: null,
      originalString: 'M56R2',
    });
  });
});

describe('NYCU Parser - Utility Functions', () => {
  test('formatDayCode should format day codes correctly', () => {
    expect(formatDayCode('M')).toBe('Mon');
    expect(formatDayCode('T')).toBe('Tue');
    expect(formatDayCode('W')).toBe('Wed');
    expect(formatDayCode('R')).toBe('Thu');
    expect(formatDayCode('F')).toBe('Fri');
    expect(formatDayCode('S')).toBe('Sat');
    expect(formatDayCode('U')).toBe('Sun');
  });

  test('formatPeriodRange should format period ranges', () => {
    expect(formatPeriodRange([1])).toBe('1');
    expect(formatPeriodRange([1, 2])).toBe('1-2');
    expect(formatPeriodRange([5, 6, 7])).toBe('5-7');
    expect(formatPeriodRange([10, 11, 12, 13])).toBe('10-13');
  });

  test('formatPeriodRange should handle non-continuous periods', () => {
    expect(formatPeriodRange([1, 3, 5])).toBe('1, 3, 5');
    expect(formatPeriodRange([1, 2, 5, 6])).toBe('1-2, 5-6');
  });
});

describe('NYCU Parser - Edge Cases', () => {
  test('should handle malformed input gracefully', () => {
    expect(parseNYCUSchedule('XYZ')).toEqual([]);
    expect(parseNYCUSchedule('123')).toEqual([]);
  });

  test('should handle partial data', () => {
    const result = parseTimeClassroom('M56-');
    expect(result?.schedule).toHaveLength(1);
    expect(result?.classroom).toBeNull();
  });

  test('should parse complex real-world examples', () => {
    // Real course: 資料結構
    const result1 = parseTimeClassroom('T56R56-EC114');
    expect(result1?.schedule).toHaveLength(2);
    expect(result1?.schedule[0].dayCode).toBe('T');
    expect(result1?.schedule[0].periods).toEqual([5, 6]);
    expect(result1?.schedule[1].dayCode).toBe('R');
    expect(result1?.schedule[1].periods).toEqual([5, 6]);
    expect(result1?.classroom?.displayName).toBe('EC114');

    // Real course: 微積分
    const result2 = parseTimeClassroom('M34W34-SC101[1F]');
    expect(result2?.schedule).toHaveLength(2);
    expect(result2?.classroom?.buildingCode).toBe('SC');
    expect(result2?.classroom?.floor).toBe('1F');
  });
});
