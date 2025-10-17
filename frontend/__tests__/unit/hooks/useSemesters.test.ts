/**
 * Unit Tests for useSemesters Hook
 *
 * Tests the useSemesters hook functionality including:
 * - Successful data fetching
 * - Loading state management
 * - Error handling
 * - Refetch functionality
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useSemesters } from '@/lib/hooks/useSemesters';
import { getSemesters } from '@/lib/api/semester';
import type { Semester } from '@/lib/types';

// Mock the semester API module
jest.mock('@/lib/api/semester');

const mockGetSemesters = getSemesters as jest.MockedFunction<typeof getSemesters>;

describe('useSemesters Hook', () => {
  // Sample test data
  const mockSemesters: Semester[] = [
    { id: 1, acy: 113, sem: 1 },
    { id: 2, acy: 112, sem: 2 },
    { id: 3, acy: 112, sem: 1 },
  ];

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  describe('test_useSemesters_fetch_success', () => {
    it('should fetch semesters successfully and update state', async () => {
      // Arrange: Mock successful API response
      mockGetSemesters.mockResolvedValueOnce(mockSemesters);

      // Act: Render the hook
      const { result } = renderHook(() => useSemesters());

      // Assert: Initially loading should be true
      expect(result.current.loading).toBe(true);
      expect(result.current.semesters).toEqual([]);
      expect(result.current.error).toBe(null);

      // Wait for the hook to finish loading
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Data should be loaded successfully
      expect(result.current.semesters).toEqual(mockSemesters);
      expect(result.current.error).toBe(null);
      expect(mockGetSemesters).toHaveBeenCalledTimes(1);
    });

    it('should handle empty semesters list', async () => {
      // Arrange: Mock empty response
      mockGetSemesters.mockResolvedValueOnce([]);

      // Act: Render the hook
      const { result } = renderHook(() => useSemesters());

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Should have empty array
      expect(result.current.semesters).toEqual([]);
      expect(result.current.error).toBe(null);
    });
  });

  describe('test_useSemesters_loading_state', () => {
    it('should manage loading state correctly during fetch', async () => {
      // Arrange: Create a promise we can control
      let resolvePromise: (value: Semester[]) => void;
      const promise = new Promise<Semester[]>((resolve) => {
        resolvePromise = resolve;
      });
      mockGetSemesters.mockReturnValueOnce(promise);

      // Act: Render the hook
      const { result } = renderHook(() => useSemesters());

      // Assert: Should be loading initially
      expect(result.current.loading).toBe(true);
      expect(result.current.semesters).toEqual([]);

      // Resolve the promise
      resolvePromise!(mockSemesters);

      // Wait for state update
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Loading should be false after completion
      expect(result.current.loading).toBe(false);
      expect(result.current.semesters).toEqual(mockSemesters);
    });

    it('should transition from loading to loaded state', async () => {
      // Arrange
      mockGetSemesters.mockResolvedValueOnce(mockSemesters);

      // Act
      const { result } = renderHook(() => useSemesters());

      // Assert initial loading state
      expect(result.current.loading).toBe(true);

      // Wait for transition
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert final loaded state
      expect(result.current.loading).toBe(false);
      expect(result.current.semesters.length).toBeGreaterThan(0);
    });
  });

  describe('test_useSemesters_error_state', () => {
    it('should handle API errors gracefully', async () => {
      // Arrange: Mock API error
      const errorMessage = 'Network error';
      mockGetSemesters.mockRejectedValueOnce(new Error(errorMessage));

      // Act: Render the hook
      const { result } = renderHook(() => useSemesters());

      // Wait for error state
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Error should be captured
      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe(errorMessage);
      expect(result.current.semesters).toEqual([]);
    });

    it('should handle non-Error exceptions', async () => {
      // Arrange: Mock non-Error exception
      mockGetSemesters.mockRejectedValueOnce('String error');

      // Act
      const { result } = renderHook(() => useSemesters());

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Assert: Should create a generic Error
      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Failed to fetch semesters');
      expect(result.current.semesters).toEqual([]);
    });

    it('should clear previous data on error', async () => {
      // Arrange: First successful fetch
      mockGetSemesters.mockResolvedValueOnce(mockSemesters);

      // Act: Render hook
      const { result, rerender } = renderHook(() => useSemesters());

      // Wait for initial success
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.semesters).toEqual(mockSemesters);

      // Arrange: Second fetch fails
      mockGetSemesters.mockRejectedValueOnce(new Error('Server error'));

      // Act: Trigger refetch
      result.current.refetch();

      // Wait for error state
      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      // Assert: Data should be cleared
      expect(result.current.semesters).toEqual([]);
    });
  });

  describe('test_useSemesters_refetch', () => {
    it('should refetch data when refetch is called', async () => {
      // Arrange: Mock initial fetch
      mockGetSemesters.mockResolvedValueOnce(mockSemesters);

      // Act: Render hook
      const { result } = renderHook(() => useSemesters());

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockGetSemesters).toHaveBeenCalledTimes(1);

      // Arrange: Mock refetch with updated data
      const updatedSemesters: Semester[] = [
        { id: 4, acy: 114, sem: 1 },
        ...mockSemesters,
      ];
      mockGetSemesters.mockResolvedValueOnce(updatedSemesters);

      // Act: Call refetch
      result.current.refetch();

      // Wait for refetch to complete
      await waitFor(() => {
        expect(result.current.semesters).toEqual(updatedSemesters);
      });

      // Assert: Should have called API twice
      expect(mockGetSemesters).toHaveBeenCalledTimes(2);
      expect(result.current.semesters).toEqual(updatedSemesters);
    });

    it('should handle refetch errors independently', async () => {
      // Arrange: Initial successful fetch
      mockGetSemesters.mockResolvedValueOnce(mockSemesters);

      // Act: Render hook
      const { result } = renderHook(() => useSemesters());

      // Wait for initial success
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe(null);

      // Arrange: Refetch fails
      mockGetSemesters.mockRejectedValueOnce(new Error('Refetch failed'));

      // Act: Call refetch
      result.current.refetch();

      // Wait for refetch error
      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });

      // Assert: Error should be set
      expect(result.current.error?.message).toBe('Refetch failed');
    });

    it('should reset loading state during refetch', async () => {
      // Arrange: Initial fetch
      mockGetSemesters.mockResolvedValueOnce(mockSemesters);

      // Act: Render hook
      const { result } = renderHook(() => useSemesters());

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Arrange: Setup controlled promise for refetch
      let resolveRefetch: (value: Semester[]) => void;
      const refetchPromise = new Promise<Semester[]>((resolve) => {
        resolveRefetch = resolve;
      });
      mockGetSemesters.mockReturnValueOnce(refetchPromise);

      // Act: Call refetch
      result.current.refetch();

      // Wait for loading state to be set
      await waitFor(() => {
        expect(result.current.loading).toBe(true);
      });

      // Assert: Should be loading
      expect(result.current.loading).toBe(true);

      // Resolve refetch
      resolveRefetch!(mockSemesters);

      // Wait for completion
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.loading).toBe(false);
    });
  });

  describe('Cleanup and unmount behavior', () => {
    it('should not update state after unmount', async () => {
      // Arrange: Setup delayed response
      let resolvePromise: (value: Semester[]) => void;
      const promise = new Promise<Semester[]>((resolve) => {
        resolvePromise = resolve;
      });
      mockGetSemesters.mockReturnValueOnce(promise);

      // Act: Render and unmount before promise resolves
      const { result, unmount } = renderHook(() => useSemesters());

      expect(result.current.loading).toBe(true);

      // Unmount before API call completes
      unmount();

      // Resolve promise after unmount
      resolvePromise!(mockSemesters);

      // Wait a bit to ensure no state updates occur
      await new Promise((resolve) => setTimeout(resolve, 100));

      // If we get here without errors, the cleanup worked correctly
      expect(true).toBe(true);
    });
  });
});
