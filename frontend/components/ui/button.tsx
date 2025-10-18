/**
 * Button Component Library
 *
 * NDHU Design System Compliant Button Component
 * Supports multiple variants and sizes with full accessibility support
 *
 * Variants:
 * - primary: Indigo-600 main action buttons (default)
 * - secondary: Gray secondary actions
 * - ghost: Transparent with hover background
 * - outline: Bordered buttons for less important actions
 * - danger: Red error/destructive actions
 *
 * Sizes:
 * - sm: Small button (h-8)
 * - default: Regular button (h-10)
 * - lg: Large button (h-12)
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="lg">Click me</Button>
 * <Button variant="outline" disabled>Disabled</Button>
 * <Button variant="ghost">Ghost Button</Button>
 * ```
 */

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95",
  {
    variants: {
      variant: {
        // Primary: Indigo-600 main action buttons (NDHU primary color)
        primary:
          "bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700 shadow-md hover:shadow-lg focus-visible:ring-indigo-500",
        // Secondary: Gray alternative actions
        secondary:
          "bg-gray-200 text-gray-900 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 shadow-sm hover:shadow-md",
        // Ghost: Transparent with hover background
        ghost:
          "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-gray-100 focus-visible:ring-gray-400",
        // Outline: Bordered style
        outline:
          "border-2 border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-900/50 focus-visible:ring-gray-500",
        // Danger: Destructive actions (Red)
        danger:
          "bg-red-500 text-white hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 shadow-md hover:shadow-lg focus-visible:ring-red-500",
        // Accent: Rose accent color
        accent:
          "bg-rose-500 text-white hover:bg-rose-600 dark:bg-rose-600 dark:hover:bg-rose-700 shadow-md hover:shadow-lg focus-visible:ring-rose-500",
        // Success: Emerald for success states
        success:
          "bg-emerald-500 text-white hover:bg-emerald-600 dark:bg-emerald-600 dark:hover:bg-emerald-700 shadow-md hover:shadow-lg focus-visible:ring-emerald-500",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        default: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
        xl: "h-14 px-8 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

/**
 * Button component with multiple variants and sizes
 * @param variant - Button style variant
 * @param size - Button size preset
 * @param className - Additional CSS classes
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
)
Button.displayName = "Button"

export { Button, buttonVariants }
