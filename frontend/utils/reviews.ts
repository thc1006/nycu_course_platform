/**
 * Reviews & Ratings Utility
 * Handles review validation, rating calculations, sorting, and filtering
 */

interface Review {
  id?: number
  courseId: number
  userId?: string
  rating: number
  text: string
  helpful?: number
  unhelpful?: number
  date?: Date
  [key: string]: any
}

interface ReviewData {
  courseId?: number
  rating: number
  text: string
}

/**
 * Validate review data
 * - Rating must be between 1-5
 * - Text must be non-empty
 * - CourseId is required
 */
export function validateReview(data: any): boolean {
  if (typeof data !== 'object' || data === null) {
    return false
  }

  const { rating, text, courseId } = data

  // Validate rating (1-5)
  if (typeof rating !== 'number' || rating < 1 || rating > 5) {
    return false
  }

  // Validate text (non-empty string)
  if (typeof text !== 'string' || text.trim().length === 0) {
    return false
  }

  // Validate courseId (required)
  if (courseId === undefined || courseId === null) {
    return false
  }

  return true
}

/**
 * Calculate average rating from reviews
 * - Returns 0 for empty array
 * - Rounds to 1 decimal place
 */
export function calculateAverageRating(reviews: any[]): number {
  if (!Array.isArray(reviews) || reviews.length === 0) {
    return 0
  }

  const sum = reviews.reduce((acc, review) => {
    const rating = review.rating
    return acc + (typeof rating === 'number' ? rating : 0)
  }, 0)

  const average = sum / reviews.length

  // Round to 1 decimal place
  return Math.round(average * 10) / 10
}

/**
 * Sort reviews by helpfulness ratio (helpful / (helpful + unhelpful))
 * Sorts in descending order (most helpful first)
 * Maintains original order for equal helpfulness
 */
export function sortReviewsByHelpfulness(reviews: any[]): any[] {
  if (!Array.isArray(reviews)) {
    return []
  }

  // Create a copy to avoid mutating original array
  const reviewsCopy = [...reviews]

  return reviewsCopy.sort((a, b) => {
    const ratioA = calculateHelpfulnessRatio(a)
    const ratioB = calculateHelpfulnessRatio(b)

    // Sort descending (higher ratio first)
    return ratioB - ratioA
  })
}

/**
 * Filter reviews by rating
 * Supports three filter modes:
 * 1. Exact match: filterReviewsByRating(reviews, 5)
 * 2. Minimum rating: filterReviewsByRating(reviews, 4, 'gte')
 * 3. Range: filterReviewsByRating(reviews, [3, 4])
 */
export function filterReviewsByRating(
  reviews: any[],
  rating: number | [number, number],
  mode?: 'gte' | 'lte' | 'exact'
): any[] {
  if (!Array.isArray(reviews)) {
    return []
  }

  // Range mode: array of [min, max]
  if (Array.isArray(rating)) {
    const [min, max] = rating
    return reviews.filter((review) => {
      const r = review.rating
      return typeof r === 'number' && r >= min && r <= max
    })
  }

  // Determine filter mode
  if (mode === 'gte') {
    // Greater than or equal to
    return reviews.filter((review) => {
      const r = review.rating
      return typeof r === 'number' && r >= rating
    })
  }

  if (mode === 'lte') {
    // Less than or equal to
    return reviews.filter((review) => {
      const r = review.rating
      return typeof r === 'number' && r <= rating
    })
  }

  // Default: exact match
  return reviews.filter((review) => review.rating === rating)
}

/**
 * Helper: Calculate helpfulness ratio
 * If helpful and unhelpful are 0, return 0
 */
function calculateHelpfulnessRatio(review: any): number {
  const helpful = review.helpful || 0
  const unhelpful = review.unhelpful || 0

  const total = helpful + unhelpful

  if (total === 0) {
    return 0
  }

  return helpful / total
}
