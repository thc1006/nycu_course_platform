/**
 * Course Detail Page
 *
 * Dynamic route for displaying detailed information about a specific course.
 * Features:
 * - Fetch course by ID from router params
 * - Display full course information
 * - Add to schedule functionality
 * - Share course functionality
 * - Back navigation
 * - Loading, error, and 404 states
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { Header, Footer, CourseDetail, Loading, Error } from '@/components';
import { useCourse } from '@/lib/hooks/useCourses';

/**
 * Course detail page component
 */
export default function CourseDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [isInSchedule, setIsInSchedule] = useState(false);
  const [shareSuccess, setShareSuccess] = useState(false);

  // Parse course ID from query
  const courseId = id ? parseInt(id as string, 10) : null;

  // Fetch course data
  const { course, loading, error } = useCourse(courseId);

  /**
   * Check if course is already in schedule
   */
  useEffect(() => {
    if (courseId) {
      const schedule = JSON.parse(localStorage.getItem('schedule') || '[]');
      setIsInSchedule(schedule.includes(courseId));
    }
  }, [courseId]);

  /**
   * Add course to schedule
   */
  const handleAddToSchedule = () => {
    if (!courseId) return;

    const schedule = JSON.parse(localStorage.getItem('schedule') || '[]');

    if (!schedule.includes(courseId)) {
      schedule.push(courseId);
      localStorage.setItem('schedule', JSON.stringify(schedule));
      setIsInSchedule(true);
      alert('Course added to schedule!');
    }
  };

  /**
   * Remove course from schedule
   */
  const handleRemoveFromSchedule = () => {
    if (!courseId) return;

    const schedule = JSON.parse(localStorage.getItem('schedule') || '[]');
    const updatedSchedule = schedule.filter((id: number) => id !== courseId);
    localStorage.setItem('schedule', JSON.stringify(updatedSchedule));
    setIsInSchedule(false);
    alert('Course removed from schedule!');
  };

  /**
   * Share course
   */
  const handleShare = async () => {
    const url = window.location.href;

    // Try to use native share API if available
    if (navigator.share) {
      try {
        await navigator.share({
          title: course?.name || 'NYCU Course',
          text: `Check out this course: ${course?.name}`,
          url,
        });
      } catch (err) {
        // User cancelled share or error occurred
        console.log('Share cancelled or failed:', err);
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(url);
        setShareSuccess(true);
        setTimeout(() => setShareSuccess(false), 3000);
      } catch (err) {
        alert('Failed to copy link');
      }
    }
  };

  /**
   * Navigate back
   */
  const handleBack = () => {
    router.back();
  };

  // Loading state
  if (loading) {
    return (
      <>
        <Head>
          <title>Loading Course... - NYCU Course Platform</title>
        </Head>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Header />
          <main className="flex-1 container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
              <Loading message="Loading course details..." />
            </div>
          </main>
          <Footer />
        </div>
      </>
    );
  }

  // Error state
  if (error) {
    return (
      <>
        <Head>
          <title>Error - NYCU Course Platform</title>
        </Head>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Header />
          <main className="flex-1 container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
              <Error
                message="Failed to load course details"
                onRetry={() => router.reload()}
              />
              <div className="mt-6 text-center">
                <Link href="/" className="text-blue-600 hover:text-blue-700 font-medium">
                  Return to Home
                  
                </Link>
              </div>
            </div>
          </main>
          <Footer />
        </div>
      </>
    );
  }

  // 404 state - course not found
  if (!course) {
    return (
      <>
        <Head>
          <title>Course Not Found - NYCU Course Platform</title>
        </Head>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Header />
          <main className="flex-1 container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto text-center py-12">
              <svg
                className="w-24 h-24 mx-auto text-gray-300 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Course Not Found
              </h1>
              <p className="text-gray-600 mb-6">
                The course you are looking for does not exist or has been removed.
              </p>
              <div className="space-x-4">
                <button
                  onClick={handleBack}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    className="mr-2 w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 19l-7-7m0 0l7-7m-7 7h18"
                    />
                  </svg>
                  Go Back
                </button>
                <Link href="/" className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                  Browse Courses
                  
                </Link>
              </div>
            </div>
          </main>
          <Footer />
        </div>
      </>
    );
  }

  // Success state - display course
  return (
    <>
      <Head>
        <title>{course.name || 'Course Details'} - NYCU Course Platform</title>
        <meta
          name="description"
          content={`${course.name} - ${course.teacher || 'NYCU'} - ${course.credits} credits`}
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />

        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* Back Button */}
            <button
              onClick={handleBack}
              className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium mb-6 transition"
            >
              <svg
                className="mr-2 w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Back
            </button>

            {/* Action Buttons */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="flex flex-wrap gap-4">
                {/* Add/Remove from Schedule Button */}
                {isInSchedule ? (
                  <button
                    onClick={handleRemoveFromSchedule}
                    className="inline-flex items-center px-6 py-3 border border-red-300 text-base font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition"
                  >
                    <svg
                      className="mr-2 w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                    Remove from Schedule
                  </button>
                ) : (
                  <button
                    onClick={handleAddToSchedule}
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                  >
                    <svg
                      className="mr-2 w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                    Add to Schedule
                  </button>
                )}

                {/* Share Button */}
                <button
                  onClick={handleShare}
                  className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                >
                  <svg
                    className="mr-2 w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
                    />
                  </svg>
                  {shareSuccess ? 'Link Copied!' : 'Share'}
                </button>

                {/* View Schedule Button */}
                <Link href="/schedule" className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition">
                  <svg
                      className="mr-2 w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    View Schedule
                </Link>
              </div>

              {/* Share Success Message */}
              {shareSuccess && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm text-green-800">
                    Link copied to clipboard! Share it with your friends.
                  </p>
                </div>
              )}
            </div>

            {/* Course Detail Component */}
            <CourseDetail course={course} />
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
