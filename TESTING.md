# Testing Guide - NYCU Course Platform

Comprehensive testing documentation for frontend tests.

## Overview

The frontend testing stack includes:
- **Jest**: Unit and integration testing
- **React Testing Library**: Component testing
- **Playwright**: End-to-end testing

## Test Structure

```
frontend/
├── __tests__/
│   ├── unit/
│   │   ├── hooks/           # Hook tests
│   │   └── lib/             # API and utility tests
│   ├── components/          # Component tests
│   ├── pages/               # Page tests
│   └── e2e/                 # End-to-end tests
├── jest.config.js           # Jest configuration
├── jest.setup.js            # Jest setup file
└── playwright.config.ts     # Playwright configuration
```

## Running Tests

### Unit and Component Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- useSemesters.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="should fetch"
```

### E2E Tests

```bash
# Run all E2E tests
npm run e2e

# Run E2E tests with UI
npm run e2e:ui

# Run specific test file
npx playwright test home.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium

# Debug mode
npx playwright test --debug
```

## Test Files Created

### Unit Tests

1. **useSemesters.test.ts** - Tests for semester management hook
   - Successful data fetching
   - Loading state management
   - Error handling
   - Refetch functionality

2. **useCourses.test.ts** - Tests for course management hook
   - Filtering by acy, sem, dept, teacher
   - Search functionality
   - Pagination and load more
   - Error handling

3. **course.test.ts** - Tests for course API functions
   - getCourses with various parameters
   - getCourse for single course
   - searchCourses functionality
   - Utility functions (formatting, sorting, grouping)

### E2E Tests

4. **home.spec.ts** - Homepage user flows
   - Page load and initial render
   - Semester selection
   - Course search
   - Department filtering
   - Navigation to course details
   - Add to schedule functionality
   - Pagination (load more)
   - Mobile responsiveness

5. **schedule.spec.ts** - Schedule management flows
   - View schedule grid
   - Add/remove courses
   - Conflict detection
   - Export schedule
   - Clear schedule
   - LocalStorage persistence
   - Mobile view

## Writing Tests

### Unit Test Example

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useSemesters } from '@/lib/hooks/useSemesters';

jest.mock('@/lib/api/semester');

test('should fetch semesters successfully', async () => {
  const mockSemesters = [{ id: 1, acy: 113, sem: 1 }];
  mockGetSemesters.mockResolvedValueOnce(mockSemesters);

  const { result } = renderHook(() => useSemesters());

  await waitFor(() => {
    expect(result.current.loading).toBe(false);
  });

  expect(result.current.semesters).toEqual(mockSemesters);
});
```

### Component Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import CourseCard from '@/components/course/CourseCard';

test('renders course information', () => {
  const mockCourse = {
    id: 1,
    crs_no: 'CS3101',
    name: 'Intro to CS',
    teacher: 'Dr. Smith',
    credits: 3,
  };

  render(<CourseCard course={mockCourse} />);

  expect(screen.getByText('Intro to CS')).toBeInTheDocument();
  expect(screen.getByText('Dr. Smith')).toBeInTheDocument();
});
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test';

test('should navigate to course details', async ({ page }) => {
  await page.goto('/');

  const firstCourse = page.locator('.course-card').first();
  await firstCourse.click();

  await expect(page).toHaveURL(/\/course\/\d+/);
});
```

## Coverage Requirements

Current coverage thresholds (configured in jest.config.js):

- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 75%
- **Statements**: 75%

### Viewing Coverage

```bash
npm run test:coverage

# Open HTML report
open coverage/lcov-report/index.html
```

## Mocking

### API Mocking (Jest)

```typescript
// Mock entire module
jest.mock('@/lib/api/course');

// Mock specific function
const mockGetCourses = jest.fn();
jest.mock('@/lib/api/course', () => ({
  getCourses: mockGetCourses,
}));

// Mock implementation
mockGetCourses.mockResolvedValueOnce([mockCourse]);
```

### Network Mocking (Playwright)

```typescript
// Mock API response
await page.route('**/v1/courses*', route => {
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([mockCourse]),
  });
});

// Mock error
await page.route('**/v1/courses*', route => {
  route.abort('failed');
});
```

## Best Practices

### General

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One assertion per test**: Focus on single behavior
3. **Descriptive names**: Use clear test descriptions
4. **Independent tests**: Tests should not depend on each other
5. **Clean up**: Reset mocks and state between tests

### Unit Tests

1. **Test behavior, not implementation**: Focus on what, not how
2. **Mock external dependencies**: Isolate units
3. **Test edge cases**: Empty arrays, null values, errors
4. **Use waitFor**: For async operations

### Component Tests

1. **Test user interactions**: Click, type, navigate
2. **Test accessibility**: Use semantic queries
3. **Avoid implementation details**: Don't test state directly
4. **Test error states**: Loading, error, empty

### E2E Tests

1. **Test critical paths**: Focus on user journeys
2. **Use page objects**: Organize selectors
3. **Wait for elements**: Use proper waiting strategies
4. **Test across browsers**: Use Playwright projects
5. **Keep tests independent**: Can run in any order

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '22'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test -- --coverage

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Debugging Tests

### Jest

```bash
# Run tests with Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Use VS Code debugger
# Add breakpoint and use "Jest: Debug" configuration
```

### Playwright

```bash
# Run with headed browser
npx playwright test --headed

# Run with inspector
npx playwright test --debug

# Record test
npx playwright codegen http://localhost:3000
```

## Continuous Improvement

- Review test coverage regularly
- Update tests when requirements change
- Refactor tests to reduce duplication
- Add tests for bug fixes
- Monitor test execution time

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
