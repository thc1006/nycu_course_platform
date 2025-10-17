# NYCU Course Platform - User Guide

[![Production Status](https://img.shields.io/badge/status-production-success)](https://nymu.com.tw)
[![Courses](https://img.shields.io/badge/courses-70,239-blue)](https://nymu.com.tw)
[![HTTPS](https://img.shields.io/badge/https-enabled-green)](https://nymu.com.tw)

A comprehensive course browsing and scheduling platform for National Yang Ming Chiao Tung University (NYCU), featuring 70,239+ courses across 9 academic semesters.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Browsing Courses](#browsing-courses)
- [Filtering and Search](#filtering-and-search)
- [Managing Your Schedule](#managing-your-schedule)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

## Overview

The NYCU Course Platform is a modern web application designed to help students browse, search, and plan their course schedules efficiently. With support for over 70,000 courses spanning multiple semesters, the platform provides powerful filtering and search capabilities optimized for large-scale course catalogs.

**Platform Details:**
- **Production URL:** https://nymu.com.tw
- **Total Courses:** 70,239
- **Semesters:** 110-1 through 114-1 (9 semesters)
- **Server:** 31.41.34.19
- **Technology:** Next.js 14, React 18, FastAPI, SQLite

## Features

### Core Features

- **Course Browsing:** Browse through 70,000+ courses with efficient pagination
- **Advanced Filtering:** Filter by semester, department, teacher, and credits
- **Real-time Search:** Fast search across course names and numbers
- **Personal Schedule:** Add courses to your personal schedule planner
- **Conflict Detection:** Automatic detection of time conflicts in your schedule
- **Responsive Design:** Works seamlessly on desktop, tablet, and mobile devices
- **Dark Mode:** Switch between light and dark themes for comfortable viewing
- **Internationalization:** Support for English and Traditional Chinese

### Performance Features

- **Optimized for Scale:** Handles 70K+ courses with instant search results
- **Pagination:** Load courses in manageable chunks for better performance
- **Caching:** Smart caching for faster subsequent page loads
- **Rate Limiting:** Protected API endpoints ensure fair usage

## Getting Started

### Accessing the Platform

1. **Visit the Platform:**
   - Navigate to https://nymu.com.tw in your web browser
   - The platform works best on modern browsers (Chrome, Firefox, Safari, Edge)

2. **Browser Requirements:**
   - JavaScript must be enabled
   - Cookies enabled for saving preferences
   - LocalStorage enabled for schedule management

3. **First Visit:**
   - You'll land on the home page with the course explorer
   - No login required - start browsing immediately
   - Your preferences (dark mode, language) are saved automatically

### Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Header                             │
│  [Logo]  Home  Schedule  Browse     [Lang] [Theme]     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Course Explorer                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Filters:                                        │   │
│  │ [Semester Dropdown ▼]                          │   │
│  │ [Search: Course name or number...]             │   │
│  │ [Department Filter]                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Results: Showing 50 of 70,239 courses                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │ CS1001 - Introduction to Computer Science      │   │
│  │ Dr. Smith • 3 credits • Mon 10:00-12:00       │   │
│  │ [Add to Schedule] [View Details]               │   │
│  └─────────────────────────────────────────────────┘   │
│  [Load More...]                                         │
└─────────────────────────────────────────────────────────┘
```

## Browsing Courses

### Browse All Courses

1. **Navigate to Home Page:**
   - Click "Home" in the navigation bar or visit https://nymu.com.tw
   - You'll see the course explorer with default view

2. **Scroll Through Courses:**
   - Courses are loaded in batches of 50 for optimal performance
   - Click "Load More" at the bottom to fetch additional courses
   - Keep scrolling until you find what you're looking for

3. **Understanding Course Cards:**
   Each course card displays:
   - **Course Number:** Unique identifier (e.g., CS1001)
   - **Course Name:** Full title of the course
   - **Instructor:** Professor or teacher name
   - **Credits:** Number of credits (e.g., 3.0)
   - **Department:** Department code (e.g., CS, MATH)
   - **Schedule:** Time and location information

### Browse by Semester

Given the platform contains 70,239 courses, filtering by semester is essential:

1. **Select Semester:**
   ```
   Available Semesters:
   - 110-1 (Fall 2021)
   - 110-2 (Spring 2022)
   - 111-1 (Fall 2022)
   - 111-2 (Spring 2023)
   - 112-1 (Fall 2023)
   - 112-2 (Spring 2024)
   - 113-1 (Fall 2024)
   - 113-2 (Spring 2025)
   - 114-1 (Fall 2025)
   ```

2. **Understanding Semester Codes:**
   - **Format:** `[Academic Year]-[Semester]`
   - **Academic Year:** 110 = 2021, 113 = 2024, etc.
   - **Semester:** 1 = Fall, 2 = Spring

3. **Filter Results:**
   - Select year and semester from dropdown
   - Results update automatically
   - Clear filter to see all courses

### Performance Tips for Large Catalogs

When browsing 70K+ courses:

- **Always use filters:** Start with semester or department filter
- **Be specific with search:** Use specific keywords instead of browsing all
- **Use pagination wisely:** Load only what you need
- **Bookmark frequently used filters:** Save URLs with filter parameters

## Filtering and Search

### Basic Search

1. **Search by Course Name:**
   ```
   Examples:
   - "Introduction to Computer Science"
   - "Calculus"
   - "English Composition"
   ```

2. **Search by Course Number:**
   ```
   Examples:
   - "CS1001"
   - "MATH2201"
   - "ENG101"
   ```

3. **Search Tips:**
   - Search is case-insensitive
   - Partial matches are supported
   - Use quotes for exact phrases
   - Searches across 70K+ courses instantly

### Department Filter

Filter courses by academic department:

1. **Select Department:**
   - Click the department filter dropdown
   - Choose from available departments:
     - CS (Computer Science)
     - MATH (Mathematics)
     - ENG (Engineering)
     - PHYS (Physics)
     - And many more...

2. **Department Filter Benefits:**
   - Narrow down from 70K courses to department-specific list
   - See all offerings from a specific department
   - Combine with semester filter for focused results

### Advanced Filtering

Access advanced filtering on the Browse page:

1. **Navigate to Browse:**
   - Click "Browse" in the main navigation
   - Access advanced filter sidebar

2. **Available Filters:**

   **Semester Selection:**
   - Select multiple semesters simultaneously
   - Compare course offerings across terms

   **Department Filter:**
   - Filter by one or multiple departments
   - Cross-departmental course discovery

   **Credit Range:**
   - Minimum credits: 0-10
   - Maximum credits: 0-10
   - Find courses matching credit requirements

   **Instructor Filter:**
   - Search by professor name
   - Find all courses taught by specific instructors

   **Keyword Search:**
   - Search across multiple fields
   - Supports multiple keywords

3. **Combining Filters:**
   ```
   Example: Find all CS courses worth 3 credits in Fall 2024:
   - Semester: 113-1
   - Department: CS
   - Credits: 3.0 - 3.0
   - Results: Filtered list
   ```

### Search Performance

Optimized for 70,239 courses:
- **Initial Search:** < 100ms response time
- **Filtered Search:** < 50ms response time
- **Pagination:** Instant page loads
- **Real-time Updates:** As you type

## Managing Your Schedule

### Adding Courses to Schedule

1. **Find a Course:**
   - Use search and filters to locate desired course
   - Review course details (time, location, credits)

2. **Add to Schedule:**
   - Click "Add to Schedule" button on course card
   - Confirmation message appears
   - Course saved to browser's local storage

3. **View Your Schedule:**
   - Click "Schedule" in navigation bar
   - See all added courses in calendar view

### Schedule Grid View

Your schedule is displayed in a weekly calendar format:

```
Time    Mon         Tue         Wed         Thu         Fri
08:00
09:00   CS1001                  CS1001
10:00   Room A101              Room A101
11:00
12:00
13:00               MATH2201                MATH2201
14:00               Room B201               Room B201
15:00
```

### Conflict Detection

The platform automatically detects scheduling conflicts:

1. **Time Conflicts:**
   - When adding a course that overlaps with existing courses
   - Visual indicator shows conflicting courses in red
   - Warning message displays conflict details

2. **Resolving Conflicts:**
   - Remove one of the conflicting courses
   - Or choose a different section/time slot
   - System prevents double-booking

### Exporting Your Schedule

1. **Export Options:**
   - **iCalendar (.ics):** Import to Google Calendar, Outlook
   - **PDF:** Print or save for offline reference
   - **Image:** Share on social media

2. **Export Process:**
   - Navigate to Schedule page
   - Click "Export" button
   - Choose format
   - Download file

## FAQ

### General Questions

**Q: How many courses are available on the platform?**

A: The platform contains 70,239 courses spanning 9 academic semesters (110-1 through 114-1).

**Q: Do I need to create an account?**

A: No account is required. The platform is fully accessible without registration. Your schedule is saved in your browser's local storage.

**Q: Is the platform mobile-friendly?**

A: Yes! The platform is fully responsive and works on smartphones, tablets, and desktops.

**Q: How often is course data updated?**

A: Course data is maintained and updated regularly. The current production deployment includes verified course information.

### Search and Filtering

**Q: Why aren't my search results showing?**

A: With 70K+ courses, try these troubleshooting steps:
1. Clear your filters - click "Clear all filters"
2. Check spelling of search terms
3. Try broader search terms
4. Ensure semester filter isn't too restrictive

**Q: How can I search for courses by a specific professor?**

A: Use the teacher filter in the search box or navigate to Browse page for advanced filtering by instructor name.

**Q: Can I search across multiple semesters?**

A: Yes, on the Browse page, use the advanced filter to select multiple semesters simultaneously.

### Schedule Management

**Q: Where is my schedule saved?**

A: Your schedule is saved in your browser's local storage. It persists across sessions but is browser-specific.

**Q: Can I access my schedule on different devices?**

A: Currently, schedules are saved locally per browser. Export your schedule to access on multiple devices.

**Q: What happens if I clear my browser data?**

A: Your saved schedule will be lost. We recommend periodically exporting your schedule as backup.

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Courses Not Loading

**Symptoms:**
- Blank course list
- Loading spinner never stops
- Error message appears

**Solutions:**
1. Check Internet Connection
2. Verify API Status: Visit https://nymu.com.tw/health
3. Clear Browser Cache
4. Try Different Browser

#### Issue 2: Search Returns No Results

**Symptoms:**
- Search appears to work but shows "No courses found"

**Solutions:**
1. Verify filters aren't too restrictive
2. Clear all filters and try again
3. Check search syntax
4. Test with known course number

#### Issue 3: Schedule Not Saving

**Symptoms:**
- Added courses disappear after page refresh

**Solutions:**
1. Check Local Storage is enabled
2. Ensure browser isn't in private/incognito mode
3. Try different browser
4. Export schedule as backup

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| IE 11 | - | ❌ Not Supported |

## Support

### Getting Help

- **Documentation:** This guide and [API Documentation](API.md)
- **Status Page:** https://nymu.com.tw/health
- **Report Issues:** Contact system administrator

### System Requirements

**Minimum:**
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+)
- Internet connection (1 Mbps+)
- JavaScript enabled
- LocalStorage enabled

**Recommended:**
- Broadband internet (5 Mbps+)
- Desktop or laptop computer
- Screen resolution: 1920x1080
- 4GB+ RAM

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
**Total Courses:** 70,239
**Production Status:** Active
