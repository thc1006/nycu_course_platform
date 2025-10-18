/**
 * Badge Component
 *
 * NDHU Design System Compliant Badge Component
 * Used for labeling, categorizing, and highlighting content
 *
 * Variants:
 * - success: Emerald-500 for successful states
 * - warning: Amber-500 for warning states
 * - error: Red-500 for error states
 * - info: Indigo-500 for informational states
 * - default: Gray for neutral states
 * - accent: Rose-500 for accent/highlight
 *
 * @example
 * ```tsx
 * <Badge variant="success">Completed</Badge>
 * <Badge variant="warning">Pending</Badge>
 * <Badge variant="error">Failed</Badge>
 * <Badge variant="info">New</Badge>
 * ```
 */

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold transition-colors duration-200",
  {
    variants: {
      variant: {
        // Success: Emerald for completed/positive states
        success:
          "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300 border border-emerald-200/50 dark:border-emerald-700/50",
        // Warning: Amber for warning states
        warning:
          "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300 border border-amber-200/50 dark:border-amber-700/50",
        // Error: Red for error/destructive states
        error:
          "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border border-red-200/50 dark:border-red-700/50",
        // Info: Indigo for informational states
        info: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300 border border-indigo-200/50 dark:border-indigo-700/50",
        // Default: Gray for neutral states
        default:
          "bg-gray-100 text-gray-800 dark:bg-gray-800/50 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50",
        // Accent: Rose for accent/highlight
        accent:
          "bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300 border border-rose-200/50 dark:border-rose-700/50",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        default: "px-3 py-1 text-xs",
        lg: "px-4 py-1.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

/**
 * Badge component for labeling and categorizing content
 * @param variant - Badge color variant (success, warning, error, info, default, accent)
 * @param size - Badge size preset (sm, default, lg)
 * @param className - Additional CSS classes
 */
function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size, className }))} {...props} />
  )
}

export { Badge, badgeVariants }
