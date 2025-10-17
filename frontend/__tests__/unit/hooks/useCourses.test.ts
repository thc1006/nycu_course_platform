/**
 * Unit Tests for useCourses Hook
 *
 * Tests the useCourses hook functionality including:
 * - Filtering by academic year, semester, and department
 * - Search functionality
 * - Pagination and load more
 * - Error handling
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useCourses } from '@/lib/hooks/useCourses';
import { getCourses } from '@/lib/api/course';
import type { Course } from '@/lib/types';

// Mock the course API module
jest.mock('@/lib/api/course');

const mockGetCourses = getCourses as jest.MockedFunction<typeof getCourses>;

describe('useCourses Hook', () => {
  // Sample test data
  const mockCourses: Course[] = [
    {
      id: 1,
      acy: 113,
      sem: 1,
      crs_no: 'CS3101',
      name: 'Introduction to Computer Science',
      teacher: 'Dr. Smith',
      credits: 3,
      dept: 'CS',
      time: 'Mon 10:00-12:00',
      classroom: 'EC015',
      details: null,
    },
    {
      id: 2,
      acy: 113,
      sem: 1,
      crs_no: 'MATH2101',
      name: 'Calculus I',
      teacher: 'Dr. Johnson',
      credits: 4,
      dept: 'MATH',
      time: 'Tue 14:00-16:00',
      classroom: 'EC101',
      details: null,
    },
    {
      id: 3,
      acy: 113,
      sem: 1,
      crs_no: 'CS3102',
      name: 'Data Structures',
      teacher: 'Dr. Smith',
      credits: 3,
      dept: 'CS',
      time: 'Wed 10:00-12:00',
      classroom: 'EC016',
      details: null,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('test_useCourses_with_filters', () => {
    it('should fetch courses with academic year filter', async () => {
      // Arrange
      mockGetCourses.mockResolvedValueOnce(mockCourses);

      // Act
      const { result } = renderHook(() => useCourses(113));

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.courses).toEqual(mockCourses);
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({ acy: 113 })
      );
    });

    it('should fetch courses with semester filter', async () => {
      // Arrange
      mockGetCourses.mockResolvedValueOnce(mockCourses);

      // Act
      const { result } = renderHook(() => useCourses(113, 1));

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.courses).toEqual(mockCourses);
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({ acy: 113, sem: 1 })
      );
    });

    it('should fetch courses with department filter', async () => {
      // Arrange
      const csCourses = mockCourses.filter(c => c.dept === 'CS');
      mockGetCourses.mockResolvedValueOnce(csCourses);

      // Act
      const { result } = renderHook(() => useCourses(113, 1, 'CS'));

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.courses).toEqual(csCourses);
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({ acy: 113, sem: 1, dept: 'CS' })
      );
    });

    it('should fetch courses with teacher filter', async () => {
      // Arrange
      const smithCourses = mockCourses.filter(c => c.teacher === 'Dr. Smith');
      mockGetCourses.mockResolvedValueOnce(smithCourses);

      // Act
      const { result } = renderHook(() =>
        useCourses(113, 1, undefined, 'Dr. Smith')
      );

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.courses).toEqual(smithCourses);
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({ acy: 113, sem: 1, teacher: 'Dr. Smith' })
      );
    });

    it('should fetch courses with multiple filters combined', async () => {
      // Arrange
      mockGetCourses.mockResolvedValueOnce([mockCourses[0]]);

      // Act
      const { result } = renderHook(() =>
        useCourses(113, 1, 'CS', 'Dr. Smith')
      );

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({
          acy: 113,
          sem: 1,
          dept: 'CS',
          teacher: 'Dr. Smith',
        })
      );
    });
  });

  describe('test_useCourses_search', () => {
    it('should search courses by query string', async () => {
      // Arrange
      const searchResults = [mockCourses[0]];
      mockGetCourses.mockResolvedValueOnce(searchResults);

      // Act
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, 'computer')
      );

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.courses).toEqual(searchResults);
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({ q: 'computer' })
      );
    });

    it('should reset results when search query changes', async () => {
      // Arrange: Initial search
      mockGetCourses.mockResolvedValueOnce([mockCourses[0]]);

      // Act: Render with initial query
      const { result, rerender } = renderHook(
        ({ query }) =>
          useCourses(undefined, undefined, undefined, undefined, query),
        { initialProps: { query: 'computer' } }
      );

      // Wait for initial results
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.courses).toEqual([mockCourses[0]]);

      // Arrange: New search
      mockGetCourses.mockResolvedValueOnce([mockCourses[1]]);

      // Act: Update query
      rerender({ query: 'calculus' });

      // Wait for new results
      await waitFor(() => {
        expect(result.current.courses).toEqual([mockCourses[1]]);
      });

      // Assert: Should have made two API calls
      expect(mockGetCourses).toHaveBeenCalledTimes(2);
    });

    it('should handle empty search results', async () => {
      // Arrange
      mockGetCourses.mockResolvedValueOnce([]);

      // Act
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, 'nonexistent')
      );

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.courses).toEqual([]);
      expect(result.current.error).toBe(null);
    });
  });

  describe('test_useCourses_pagination', () => {
    it('should support pagination with loadMore', async () => {
      // Arrange: Initial page
      const page1 = mockCourses.slice(0, 2);
      mockGetCourses.mockResolvedValueOnce(page1);

      // Act: Render with pagination enabled
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, undefined, {
          enablePagination: true,
          pageSize: 2,
        })
      );

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Initial page loaded
      expect(result.current.courses).toEqual(page1);
      expect(result.current.hasMore).toBe(true);
      expect(result.current.totalLoaded).toBe(2);

      // Arrange: Second page
      const page2 = mockCourses.slice(2, 3);
      mockGetCourses.mockResolvedValueOnce(page2);

      // Act: Load more
      result.current.loadMore();

      // Wait for second page
      await waitFor(() => {
        expect(result.current.courses.length).toBe(3);
      });

      // Assert: Both pages loaded
      expect(result.current.courses).toEqual([...page1, ...page2]);
      expect(result.current.totalLoaded).toBe(3);
      expect(mockGetCourses).toHaveBeenCalledTimes(2);
    });

    it('should set hasMore to false when fewer results than pageSize', async () => {
      // Arrange: Only 1 course returned with pageSize of 2
      mockGetCourses.mockResolvedValueOnce([mockCourses[0]]);

      // Act
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, undefined, {
          enablePagination: true,
          pageSize: 2,
        })
      );

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: hasMore should be false
      expect(result.current.hasMore).toBe(false);
    });

    it('should not load more when already loading', async () => {
      // Arrange: Setup delayed response
      let resolvePromise: (value: Course[]) => void;
      const promise = new Promise<Course[]>((resolve) => {
        resolvePromise = resolve;
      });
      mockGetCourses.mockReturnValueOnce(promise);

      // Act: Render with pagination
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, undefined, {
          enablePagination: true,
          pageSize: 2,
        })
      );

      // Try to load more while still loading initial data
      result.current.loadMore();

      // Resolve initial load
      resolvePromise!(mockCourses.slice(0, 2));

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Should only have called API once
      expect(mockGetCourses).toHaveBeenCalledTimes(1);
    });

    it('should reset offset when filters change', async () => {
      // Arrange: Initial fetch
      mockGetCourses.mockResolvedValueOnce(mockCourses);

      // Act: Render with initial filters
      const { result, rerender } = renderHook(
        ({ dept }) =>
          useCourses(113, 1, dept, undefined, undefined, {
            enablePagination: true,
            pageSize: 2,
          }),
        { initialProps: { dept: 'CS' } }
      );

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Arrange: Change filter
      mockGetCourses.mockResolvedValueOnce([mockCourses[1]]);

      // Act: Change department filter
      rerender({ dept: 'MATH' });

      // Wait for new results
      await waitFor(() => {
        expect(result.current.courses).toEqual([mockCourses[1]]);
      });

      // Assert: Should have reset to first page
      expect(mockGetCourses).toHaveBeenLastCalledWith(
        expect.objectContaining({ dept: 'MATH', offset: 0 })
      );
    });
  });

  describe('test_useCourses_error_handling', () => {
    it('should handle API errors gracefully', async () => {
      // Arrange
      const errorMessage = 'Failed to fetch courses';
      mockGetCourses.mockRejectedValueOnce(new Error(errorMessage));

      // Act
      const { result } = renderHook(() => useCourses());

      // Wait for error
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe(errorMessage);
      expect(result.current.courses).toEqual([]);
    });

    it('should preserve previous data on error when paginating', async () => {
      // Arrange: Initial successful load
      mockGetCourses.mockResolvedValueOnce(mockCourses.slice(0, 2));

      // Act: Render with pagination
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, undefined, {
          enablePagination: true,
          pageSize: 2,
        })
      );

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const initialCourses = result.current.courses;

      // Arrange: Second page fails
      mockGetCourses.mockRejectedValueOnce(new Error('Network error'));

      // Act: Try to load more
      result.current.loadMore();

      // Wait for error
      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      // Assert: Previous data should be preserved
      expect(result.current.courses).toEqual(initialCourses);
    });

    it('should handle non-Error exceptions', async () => {
      // Arrange
      mockGetCourses.mockRejectedValueOnce('String error');

      // Act
      const { result } = renderHook(() => useCourses());

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Failed to fetch courses');
    });

    it('should refetch successfully after an error', async () => {
      // Arrange: Initial error
      mockGetCourses.mockRejectedValueOnce(new Error('Initial error'));

      // Act: Render hook
      const { result } = renderHook(() => useCourses());

      // Wait for error
      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      // Arrange: Successful refetch
      mockGetCourses.mockResolvedValueOnce(mockCourses);

      // Act: Refetch
      result.current.refetch();

      // Wait for success
      await waitFor(() => {
        expect(result.current.courses.length).toBeGreaterThan(0);
      });

      // Assert
      expect(result.current.error).toBe(null);
      expect(result.current.courses).toEqual(mockCourses);
    });
  });

  describe('Hook options', () => {
    it('should not fetch when enabled is false', async () => {
      // Arrange
      mockGetCourses.mockResolvedValueOnce(mockCourses);

      // Act
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, undefined, {
          enabled: false,
        })
      );

      // Wait a bit
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Assert: Should not have fetched
      expect(mockGetCourses).not.toHaveBeenCalled();
      expect(result.current.loading).toBe(true); // Still in initial state
    });

    it('should use custom page size', async () => {
      // Arrange
      mockGetCourses.mockResolvedValueOnce(mockCourses);

      // Act
      const { result } = renderHook(() =>
        useCourses(undefined, undefined, undefined, undefined, undefined, {
          enablePagination: true,
          pageSize: 10,
        })
      );

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert
      expect(mockGetCourses).toHaveBeenCalledWith(
        expect.objectContaining({ limit: 10, offset: 0 })
      );
    });
  });
});
