/**
 * Error Component
 *
 * Displays error messages with retry functionality.
 * Features:
 * - Error icon with visual feedback
 * - Customizable error message
 * - Optional retry button
 * - Different variants (error, warning, info)
 * - Responsive design
 * - Tailwind CSS styling
 *
 * @example
 * ```tsx
 * // Basic usage
 * <Error message="Failed to load courses" />
 *
 * // With retry handler
 * <Error
 *   message="Failed to load data"
 *   onRetry={() => fetchData()}
 * />
 *
 * // Warning variant
 * <Error
 *   message="Some data may be outdated"
 *   variant="warning"
 * />
 * ```
 */

import React from 'react';

/**
 * Props for the Error component
 */
interface ErrorProps {
  /** Error message to display */
  message: string;
  /** Optional callback function for retry button */
  onRetry?: () => void;
  /** Visual variant of the error display (default: "error") */
  variant?: 'error' | 'warning' | 'info';
  /** Optional additional details to display */
  details?: string;
}

/**
 * Error component with icon, message, and optional retry button
 *
 * @param {ErrorProps} props - Component props
 * @returns {JSX.Element} The rendered error component
 */
const Error: React.FC<ErrorProps> = ({
  message,
  onRetry,
  variant = 'error',
  details,
}) => {
  const variantStyles = {
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'text-red-500',
      text: 'text-red-800',
      button: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'text-yellow-500',
      text: 'text-yellow-800',
      button: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500',
    },
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-500',
      text: 'text-blue-800',
      button: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    },
  };

  const styles = variantStyles[variant];

  return (
    <div className={`rounded-lg border-2 ${styles.container} p-6 my-4`}>
      <div className="flex items-start space-x-4">
        {/* Error Icon */}
        <div className={`flex-shrink-0 ${styles.icon}`}>
          {variant === 'error' && (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
          {variant === 'warning' && (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          )}
          {variant === 'info' && (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className={`text-lg font-semibold mb-2 ${styles.text}`}>
            {variant === 'error' && 'Error'}
            {variant === 'warning' && 'Warning'}
            {variant === 'info' && 'Information'}
          </h3>
          <p className={`text-sm mb-3 ${styles.text}`}>{message}</p>

          {details && (
            <details className="mt-2">
              <summary className={`text-sm font-medium cursor-pointer ${styles.text} hover:underline`}>
                View details
              </summary>
              <pre className={`mt-2 text-xs p-3 rounded bg-white overflow-x-auto ${styles.text}`}>
                {details}
              </pre>
            </details>
          )}

          {/* Retry Button */}
          {onRetry && (
            <button
              onClick={onRetry}
              className={`mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${styles.button} focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors`}
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Inline error component for compact error display
 *
 * @example
 * ```tsx
 * <InlineError message="Invalid input" />
 * ```
 */
export const InlineError: React.FC<{ message: string }> = ({ message }) => {
  return (
    <div className="flex items-center space-x-2 text-red-600 text-sm">
      <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>{message}</span>
    </div>
  );
};

/**
 * Error boundary fallback component
 *
 * @example
 * ```tsx
 * <ErrorFallback error={error} resetError={reset} />
 * ```
 */
export const ErrorFallback: React.FC<{
  error: Error;
  resetError?: () => void;
}> = ({ error, resetError }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full">
        <Error
          message="Something went wrong"
          details={error.message}
          onRetry={resetError}
          variant="error"
        />
      </div>
    </div>
  );
};

export default Error;
