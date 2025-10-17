import {
  validateReview,
  calculateAverageRating,
  sortReviewsByHelpfulness,
  filterReviewsByRating,
} from '@/utils/reviews'

describe('Reviews Utils', () => {
  const mockReviews = [
    {
      id: 1,
      courseId: 1,
      userId: 'user1',
      rating: 5,
      text: 'Great course!',
      helpful: 10,
      unhelpful: 2,
      date: new Date('2025-01-01'),
    },
    {
      id: 2,
      courseId: 1,
      userId: 'user2',
      rating: 3,
      text: 'Average content',
      helpful: 5,
      unhelpful: 3,
      date: new Date('2025-01-02'),
    },
    {
      id: 3,
      courseId: 1,
      userId: 'user3',
      rating: 4,
      text: 'Good course',
      helpful: 8,
      unhelpful: 1,
      date: new Date('2025-01-03'),
    },
  ]

  describe('validateReview', () => {
    it('validates correct review data', () => {
      const isValid = validateReview({
        courseId: 1,
        rating: 5,
        text: 'Great course!',
      })
      expect(isValid).toBe(true)
    })

    it('requires rating between 1-5', () => {
      const invalidLow = validateReview({
        courseId: 1,
        rating: 0,
        text: 'Test',
      })
      expect(invalidLow).toBe(false)

      const invalidHigh = validateReview({
        courseId: 1,
        rating: 6,
        text: 'Test',
      })
      expect(invalidHigh).toBe(false)
    })

    it('requires non-empty text', () => {
      const isValid = validateReview({
        courseId: 1,
        rating: 5,
        text: '',
      })
      expect(isValid).toBe(false)
    })

    it('requires courseId', () => {
      const isValid = validateReview({
        courseId: undefined,
        rating: 5,
        text: 'Test',
      })
      expect(isValid).toBe(false)
    })
  })

  describe('calculateAverageRating', () => {
    it('calculates average rating', () => {
      const average = calculateAverageRating(mockReviews)
      expect(average).toBe(4) // (5+3+4)/3
    })

    it('returns 0 for empty reviews', () => {
      const average = calculateAverageRating([])
      expect(average).toBe(0)
    })

    it('rounds to 1 decimal', () => {
      const reviews = [
        { rating: 4.5 },
        { rating: 4.6 },
        { rating: 4.7 },
      ]
      const average = calculateAverageRating(reviews)
      expect(average).toBeCloseTo(4.6, 1)
    })
  })

  describe('sortReviewsByHelpfulness', () => {
    it('sorts by helpfulness ratio', () => {
      const sorted = sortReviewsByHelpfulness(mockReviews)
      const ratios = sorted.map(r => r.helpful / (r.helpful + r.unhelpful))
      for (let i = 1; i < ratios.length; i++) {
        expect(ratios[i]).toBeLessThanOrEqual(ratios[i - 1])
      }
    })

    it('maintains original order for equal helpfulness', () => {
      const reviews = [
        { id: 1, helpful: 5, unhelpful: 5 },
        { id: 2, helpful: 3, unhelpful: 3 },
      ]
      const sorted = sortReviewsByHelpfulness(reviews)
      expect(sorted[0].id).toBe(1)
    })
  })

  describe('filterReviewsByRating', () => {
    it('filters by exact rating', () => {
      const filtered = filterReviewsByRating(mockReviews, 5)
      expect(filtered.length).toBe(1)
      expect(filtered[0].rating).toBe(5)
    })

    it('filters by minimum rating', () => {
      const filtered = filterReviewsByRating(mockReviews, 4, 'gte')
      expect(filtered.length).toBe(2)
      expect(filtered.every(r => r.rating >= 4)).toBe(true)
    })

    it('filters by range', () => {
      const filtered = filterReviewsByRating(mockReviews, [3, 4])
      expect(filtered.length).toBe(2)
      expect(filtered.every(r => r.rating >= 3 && r.rating <= 4)).toBe(true)
    })

    it('returns empty array if no matches', () => {
      const filtered = filterReviewsByRating(mockReviews, 1)
      expect(filtered.length).toBe(0)
    })
  })
})
