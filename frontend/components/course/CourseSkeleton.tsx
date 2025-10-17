/**
 * CourseSkeleton Component
 *
 * Loading skeleton placeholder for course cards.
 * Features:
 * - Animated shimmer effect
 * - Matches CourseCard layout
 * - Multiple skeleton cards
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * // Default 5 skeletons
 * <CourseSkeleton />
 *
 * // Custom count
 * <CourseSkeleton count={3} />
 * ```
 */

import React from 'react';

/**
 * Props for the CourseSkeleton component
 */
interface CourseSkeletonProps {
  /** Number of skeleton cards to display (default: 5) */
  count?: number;
}

/**
 * Skeleton loading component for course cards
 *
 * @param {CourseSkeletonProps} props - Component props
 * @returns {JSX.Element} The rendered skeleton loader
 */
const CourseSkeleton: React.FC<CourseSkeletonProps> = ({ count = 5 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonCard key={index} />
      ))}
    </div>
  );
};

/**
 * Individual skeleton card component
 */
const SkeletonCard: React.FC = () => {
  return (
    <div className="border-2 border-gray-200 rounded-lg p-5 shadow-sm bg-white">
      {/* Shimmer animation overlay */}
      <div className="animate-pulse">
        {/* Title area */}
        <div className="mb-3">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-2" />
          <div className="h-4 bg-gray-200 rounded w-1/3" />
        </div>

        {/* Details area */}
        <div className="space-y-2">
          {/* Teacher */}
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-200 rounded mr-2" />
            <div className="h-4 bg-gray-200 rounded flex-1" />
          </div>

          {/* Credits */}
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-200 rounded mr-2" />
            <div className="h-4 bg-gray-200 rounded w-1/4" />
          </div>

          {/* Department */}
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-200 rounded mr-2" />
            <div className="h-4 bg-gray-200 rounded w-1/3" />
          </div>
        </div>

        {/* Badges area */}
        <div className="flex gap-2 mt-3">
          <div className="h-6 bg-gray-200 rounded-full w-20" />
          <div className="h-6 bg-gray-200 rounded-full w-16" />
        </div>

        {/* Footer */}
        <div className="mt-4 pt-3 border-t border-gray-200">
          <div className="h-3 bg-gray-200 rounded w-1/4" />
        </div>
      </div>
    </div>
  );
};

/**
 * Compact skeleton for list view
 */
export const CompactCourseSkeleton: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="border rounded-lg p-4 bg-white">
          <div className="animate-pulse">
            <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * Detail page skeleton
 */
export const CourseDetailSkeleton: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Back button skeleton */}
      <div className="mb-6">
        <div className="h-5 bg-gray-200 rounded w-16 animate-pulse" />
      </div>

      {/* Main content card */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-blue-500 bg-opacity-50 rounded w-2/3 mb-2" />
            <div className="h-6 bg-blue-500 bg-opacity-50 rounded w-1/4" />
          </div>
        </div>

        {/* Details section */}
        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 animate-pulse">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                  <div className="h-5 bg-gray-200 rounded w-2/3" />
                </div>
              </div>
            ))}
          </div>

          {/* Additional details section */}
          <div className="border-t pt-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/4 mb-4" />
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={index} className="flex">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mr-4" />
                    <div className="h-4 bg-gray-200 rounded flex-1" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Table row skeleton
 */
export const TableRowSkeleton: React.FC<{ columns?: number; rows?: number }> = ({
  columns = 5,
  rows = 3,
}) => {
  return (
    <>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <tr key={rowIndex} className="border-b">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <td key={colIndex} className="px-4 py-3">
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
};

/**
 * Generic shimmer box for custom skeleton layouts
 */
export const ShimmerBox: React.FC<{
  className?: string;
  height?: string;
  width?: string;
}> = ({ className = '', height = 'h-4', width = 'w-full' }) => {
  return (
    <div
      className={`bg-gray-200 rounded animate-pulse ${height} ${width} ${className}`}
    />
  );
};

/**
 * Shimmer effect for images
 */
export const ImageSkeleton: React.FC<{
  className?: string;
  aspectRatio?: 'square' | 'video' | 'wide';
}> = ({ className = '', aspectRatio = 'video' }) => {
  const aspectClasses = {
    square: 'aspect-square',
    video: 'aspect-video',
    wide: 'aspect-[21/9]',
  };

  return (
    <div
      className={`bg-gray-200 rounded animate-pulse ${aspectClasses[aspectRatio]} ${className}`}
    >
      <div className="w-full h-full flex items-center justify-center">
        <svg
          className="w-12 h-12 text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>
    </div>
  );
};

export default CourseSkeleton;
