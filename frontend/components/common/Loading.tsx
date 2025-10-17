/**
 * Loading Component
 *
 * Displays loading state with spinner animation.
 * Features:
 * - Animated spinner
 * - Customizable message
 * - Full-screen overlay option
 * - Responsive design
 * - Tailwind CSS styling with animations
 *
 * @example
 * ```tsx
 * // Basic usage
 * <Loading />
 *
 * // With custom message
 * <Loading message="Loading courses..." />
 *
 * // Full-screen overlay
 * <Loading message="Processing..." fullScreen />
 * ```
 */

import React from 'react';

/**
 * Props for the Loading component
 */
interface LoadingProps {
  /** Optional custom loading message (default: "Loading...") */
  message?: string;
  /** Whether to display as full-screen overlay (default: false) */
  fullScreen?: boolean;
}

/**
 * Loading component with animated spinner
 *
 * @param {LoadingProps} props - Component props
 * @returns {JSX.Element} The rendered loading component
 */
const Loading: React.FC<LoadingProps> = ({ message = 'Loading...', fullScreen = false }) => {
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl p-8 flex flex-col items-center space-y-4">
          <Spinner size="large" />
          <p className="text-gray-700 font-medium text-lg">{message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 space-y-4">
      <Spinner />
      <p className="text-gray-600 font-medium">{message}</p>
    </div>
  );
};

/**
 * Props for the Spinner component
 */
interface SpinnerProps {
  /** Size of the spinner (default: "medium") */
  size?: 'small' | 'medium' | 'large';
}

/**
 * Animated spinner component
 *
 * @param {SpinnerProps} props - Component props
 * @returns {JSX.Element} The rendered spinner
 */
const Spinner: React.FC<SpinnerProps> = ({ size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-10 h-10',
    large: 'w-16 h-16',
  };

  return (
    <div className="relative">
      {/* Outer spinning circle */}
      <div
        className={`${sizeClasses[size]} border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin`}
      />
    </div>
  );
};

/**
 * Inline loading component for use within content
 *
 * @example
 * ```tsx
 * <InlineLoading />
 * ```
 */
export const InlineLoading: React.FC<{ message?: string }> = ({ message }) => {
  return (
    <div className="flex items-center space-x-3 text-gray-600">
      <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
      {message && <span className="text-sm">{message}</span>}
    </div>
  );
};

/**
 * Skeleton loading for text content
 *
 * @example
 * ```tsx
 * <SkeletonText lines={3} />
 * ```
 */
export const SkeletonText: React.FC<{ lines?: number }> = ({ lines = 1 }) => {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="h-4 bg-gray-200 rounded animate-pulse"
          style={{ width: index === lines - 1 ? '80%' : '100%' }}
        />
      ))}
    </div>
  );
};

/**
 * Skeleton loading for rectangular content (images, cards, etc.)
 *
 * @example
 * ```tsx
 * <SkeletonBox className="h-48" />
 * ```
 */
export const SkeletonBox: React.FC<{ className?: string }> = ({ className = '' }) => {
  return <div className={`bg-gray-200 rounded animate-pulse ${className}`} />;
};

export default Loading;
