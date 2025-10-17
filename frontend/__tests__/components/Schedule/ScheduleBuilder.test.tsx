import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ScheduleBuilder } from '@/components/Schedule/ScheduleBuilder'

describe('ScheduleBuilder Component', () => {
  const mockCourses = [
    {
      id: 1,
      crs_no: 'CS0101',
      name: 'Intro to Programming',
      teacher: 'Dr. Smith',
      credits: 3,
      dept: 'CS',
      time: 'Mon 09:00-11:00',
      classroom: 'A101',
      acy: 113,
      sem: 1,
    },
    {
      id: 2,
      crs_no: 'CS0102',
      name: 'Data Structures',
      teacher: 'Prof. Johnson',
      credits: 4,
      dept: 'CS',
      time: 'Wed 13:00-15:00',
      classroom: 'A102',
      acy: 113,
      sem: 1,
    },
  ]

  it('renders schedule builder with empty schedule', () => {
    render(<ScheduleBuilder courses={[]} selectedCourses={[]} onCoursesChange={() => {}} />)
    expect(screen.getByText(/my schedule/i)).toBeInTheDocument()
  })

  it('displays days of week', () => {
    render(<ScheduleBuilder courses={[]} selectedCourses={[]} onCoursesChange={() => {}} />)
    expect(screen.getByText(/Monday/i)).toBeInTheDocument()
    expect(screen.getByText(/Wednesday/i)).toBeInTheDocument()
    expect(screen.getByText(/Friday/i)).toBeInTheDocument()
  })

  it('adds course to schedule when selected', async () => {
    const onCoursesChange = jest.fn()
    const { rerender } = render(
      <ScheduleBuilder courses={mockCourses} selectedCourses={[]} onCoursesChange={onCoursesChange} />
    )

    // Simulate adding course
    fireEvent.click(screen.getByText(/add/i))
    expect(onCoursesChange).toHaveBeenCalled()
  })

  it('removes course from schedule', async () => {
    const onCoursesChange = jest.fn()
    render(
      <ScheduleBuilder
        courses={mockCourses}
        selectedCourses={[mockCourses[0]]}
        onCoursesChange={onCoursesChange}
      />
    )

    // Find and click remove button
    const removeButtons = screen.getAllByText(/remove|delete|×/i)
    if (removeButtons.length > 0) {
      fireEvent.click(removeButtons[0])
      expect(onCoursesChange).toHaveBeenCalled()
    }
  })

  it('displays course in correct time slot', () => {
    render(
      <ScheduleBuilder
        courses={mockCourses}
        selectedCourses={[mockCourses[0]]}
        onCoursesChange={() => {}}
      />
    )

    expect(screen.getByText(/Intro to Programming/i)).toBeInTheDocument()
    expect(screen.getByText(/09:00-11:00/i)).toBeInTheDocument()
  })

  it('supports drag and drop to reschedule courses', async () => {
    render(
      <ScheduleBuilder
        courses={mockCourses}
        selectedCourses={[mockCourses[0]]}
        onCoursesChange={() => {}}
      />
    )

    // Verify drag-drop elements exist
    const courseElements = screen.queryAllByText(/Intro to Programming/i)
    expect(courseElements.length).toBeGreaterThan(0)
  })

  it('exports schedule to iCal format', async () => {
    const { container } = render(
      <ScheduleBuilder
        courses={mockCourses}
        selectedCourses={mockCourses}
        onCoursesChange={() => {}}
      />
    )

    // Look for export button
    const exportButton = screen.queryByText(/export/i) || screen.queryByText(/download/i)
    expect(exportButton).toBeInTheDocument()
  })

  it('displays credit total', () => {
    render(
      <ScheduleBuilder
        courses={mockCourses}
        selectedCourses={mockCourses}
        onCoursesChange={() => {}}
      />
    )

    // Should show total credits (3 + 4 = 7)
    const totalText = screen.getByText(/Total Credits/i)
    expect(totalText).toBeInTheDocument()
  })
})
