/**
 * CourseCard Component Tests
 *
 * Test suite for CourseCard component with NYCU time/classroom parsing.
 * Following TDD principles - tests written before implementation changes.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { useRouter } from 'next/router';
import CourseCard from '@/components/course/CourseCard';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock next-i18next
jest.mock('next-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en' },
  }),
}));

// Mock Link component
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  };
});

describe('CourseCard - NYCU Time/Classroom Display', () => {
  const mockRouter = {
    locale: 'en',
    push: jest.fn(),
    query: {},
    pathname: '/',
  };

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Time and Classroom Parsing from details field', () => {
    test('should display parsed schedule when details.time_classroom exists', () => {
      const courseWithDetails = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: JSON.stringify({ time_classroom: 'M56R2-ED201[GF]' }),
      };

      render(<CourseCard course={courseWithDetails} />);

      // Should display "Mon 5-6, Thu 2" for schedule
      expect(screen.getByText(/Mon 5-6, Thu 2/i)).toBeInTheDocument();
    });

    test('should display parsed classroom when details.time_classroom exists', () => {
      const courseWithDetails = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: JSON.stringify({ time_classroom: 'M56R2-ED201[GF]' }),
      };

      render(<CourseCard course={courseWithDetails} />);

      // Should display classroom "ED201"
      expect(screen.getByText(/ED201/i)).toBeInTheDocument();
    });

    test('should display time and classroom together when available', () => {
      const courseWithDetails = {
        id: 2,
        crs_no: 'PHYS2101',
        name: 'Physics Lab',
        teacher: 'Prof. Chen',
        credits: 2,
        dept: 'PHYS',
        details: JSON.stringify({ time_classroom: 'W34-SC101[3F]' }),
      };

      render(<CourseCard course={courseWithDetails} />);

      // Should show "Wed 3-4" for schedule
      expect(screen.getByText(/Wed 3-4/i)).toBeInTheDocument();
      // Should show "SC101" for classroom
      expect(screen.getByText(/SC101/i)).toBeInTheDocument();
    });

    test('should handle multiple time-classroom pairs', () => {
      const courseWithMultipleTimes = {
        id: 3,
        crs_no: 'MATH2101',
        name: 'Calculus',
        teacher: 'Dr. Lee',
        credits: 4,
        dept: 'MATH',
        details: JSON.stringify({ time_classroom: 'W12-EC114,R34-SC101' }),
      };

      render(<CourseCard course={courseWithMultipleTimes} />);

      // Should display combined schedule
      expect(screen.getByText(/Wed 1-2, Thu 3-4/i)).toBeInTheDocument();
      // Should display first classroom
      expect(screen.getByText(/EC114/i)).toBeInTheDocument();
    });

    test('should display schedule with Chinese language when locale is zh', () => {
      (useRouter as jest.Mock).mockReturnValue({ ...mockRouter, locale: 'zh' });

      const courseWithDetails = {
        id: 1,
        crs_no: 'CS3101',
        name: '資料結構',
        teacher: '王老師',
        credits: 3,
        dept: 'CS',
        details: JSON.stringify({ time_classroom: 'M56-ED201' }),
      };

      render(<CourseCard course={courseWithDetails} />);

      // Should display Chinese day name "星期一"
      expect(screen.getByText(/星期一/i)).toBeInTheDocument();
      // Should display classroom with building name
      expect(screen.getByText(/ED201.*工程二館/i)).toBeInTheDocument();
    });
  });

  describe('Edge Cases and Fallbacks', () => {
    test('should show TBA when details field is null', () => {
      const courseWithoutDetails = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={courseWithoutDetails} />);

      // Should not display any schedule info (or show TBA)
      const scheduleElement = screen.queryByText(/Mon|Tue|Wed|Thu|Fri/i);
      expect(scheduleElement).not.toBeInTheDocument();
    });

    test('should show TBA when details.time_classroom is empty', () => {
      const courseWithEmptyTime = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: JSON.stringify({ time_classroom: '' }),
      };

      render(<CourseCard course={courseWithEmptyTime} />);

      // Should not crash and should not show schedule
      const scheduleElement = screen.queryByText(/Mon|Tue|Wed|Thu|Fri/i);
      expect(scheduleElement).not.toBeInTheDocument();
    });

    test('should handle invalid JSON in details field gracefully', () => {
      const courseWithInvalidJSON = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: 'invalid-json{',
      };

      render(<CourseCard course={courseWithInvalidJSON} />);

      // Should not crash
      expect(screen.getByText('Data Structures')).toBeInTheDocument();
    });

    test('should handle details with time_classroom only (no classroom part)', () => {
      const courseTimeOnly = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Online Course',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: JSON.stringify({ time_classroom: 'M56R2' }),
      };

      render(<CourseCard course={courseTimeOnly} />);

      // Should display schedule
      expect(screen.getByText(/Mon 5-6, Thu 2/i)).toBeInTheDocument();
      // Should not crash from missing classroom
    });
  });

  describe('Component Rendering', () => {
    test('should display course code', () => {
      const course = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} />);
      expect(screen.getByText('CS3101')).toBeInTheDocument();
    });

    test('should display course name', () => {
      const course = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} />);
      expect(screen.getByText('Data Structures')).toBeInTheDocument();
    });

    test('should display teacher name with emoji', () => {
      const course = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} />);
      expect(screen.getByText(/Dr. Smith/i)).toBeInTheDocument();
    });

    test('should display credits and department', () => {
      const course = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} />);
      expect(screen.getByText(/3.*Cr/i)).toBeInTheDocument();
      expect(screen.getByText('CS')).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    test('should call onAddSchedule when Add to Schedule clicked', () => {
      const mockOnAddSchedule = jest.fn();
      const course = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} onAddSchedule={mockOnAddSchedule} />);

      const addButton = screen.getByRole('button', { name: /Add to Schedule/i });
      fireEvent.click(addButton);

      expect(mockOnAddSchedule).toHaveBeenCalledWith(1);
    });

    test('should link to course detail page', () => {
      const course = {
        id: 123,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} />);

      const detailsLink = screen.getByRole('link', { name: /View Details/i });
      expect(detailsLink).toHaveAttribute('href', '/course/123');
    });

    test('should hide action buttons when showActions is false', () => {
      const course = {
        id: 1,
        crs_no: 'CS3101',
        name: 'Data Structures',
        teacher: 'Dr. Smith',
        credits: 3,
        dept: 'CS',
        details: null,
      };

      render(<CourseCard course={course} showActions={false} />);

      const addButton = screen.queryByRole('button', { name: /Add to Schedule/i });
      expect(addButton).not.toBeInTheDocument();
    });
  });
});
