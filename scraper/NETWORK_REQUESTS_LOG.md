# NYCU Timetable Network Requests Log

This document contains all network requests captured during the Playwright browser automation session.

## Initial Page Load

**URL:** `https://timetable.nycu.edu.tw/?Acy=113&Sem=1`

### Static Resources

```
[GET] https://timetable.nycu.edu.tw/?Acy=113&Sem=1
Status: 200 OK

[GET] https://timetable.nycu.edu.tw/public/css/timetable.css?token=f5ca54982e324e433e0d47232803485371d5f85a7b8bc00f915dd317814c1bfa
Status: 200 OK

[GET] https://timetable.nycu.edu.tw/public/css/jquery-impromptu.css
Status: 200 OK

[GET] https://timetable.nycu.edu.tw/public/js/jquery-3.6.0.min.js
Status: 200 OK

[GET] https://timetable.nycu.edu.tw/public/js/jquery-impromptu.min.js
Status: 200 OK

[GET] https://timetable.nycu.edu.tw/public/js/timetable.js?token=f5ca54982e324e433e0d47232803485371d5f85a7b8bc00f915dd317814c1bfa
Status: 200 OK
```

## AJAX Requests (During Page Load)

These requests are made automatically when the page loads to populate the form dropdowns and get initial data:

```
[POST] https://timetable.nycu.edu.tw/?r=main/get_default_lang
Status: 200 OK
Purpose: Get the default language setting

[POST] https://timetable.nycu.edu.tw/?r=main/getViewHtmlContents
Status: 200 OK
Purpose: Get HTML content for the view

[POST] https://timetable.nycu.edu.tw/?r=main/get_time_code
Status: 200 OK
Purpose: Get time slot codes and definitions

[POST] https://timetable.nycu.edu.tw/?r=main/get_acysem
Status: 200 OK
Purpose: Get available academic years and semesters

[POST] https://timetable.nycu.edu.tw/?r=main/get_type
Status: 200 OK
Purpose: Get course type options (Undergraduate, Graduate, etc.)

[POST] https://timetable.nycu.edu.tw/?r=main/get_category
Status: 200 OK
Purpose: Get course category options

[POST] https://timetable.nycu.edu.tw/?r=main/get_college
Status: 200 OK
Purpose: Get list of colleges

[POST] https://timetable.nycu.edu.tw/?r=main/get_dep
Status: 200 OK
Purpose: Get list of departments based on selected college

[POST] https://timetable.nycu.edu.tw/?r=main/get_group
Status: 200 OK
Purpose: Get group options

[POST] https://timetable.nycu.edu.tw/?r=main/get_grade
Status: 200 OK
Purpose: Get grade/year options

[POST] https://timetable.nycu.edu.tw/?r=main/get_class
Status: 200 OK
Purpose: Get class options

[POST] https://timetable.nycu.edu.tw/?r=main/getCouserTypeCampus
Status: 200 OK
Purpose: Get course type and campus options

[POST] https://timetable.nycu.edu.tw/?r=main/get_classroom_code
Status: 200 OK
Purpose: Get classroom code definitions

[POST] https://timetable.nycu.edu.tw/?r=main/getViewHtmlContents
Status: 200 OK
Purpose: Get view HTML content (called again)
```

## Additional Resources

```
[GET] https://timetable.nycu.edu.tw/public/images/icon_add.png
Status: 200 OK
Purpose: UI icon
```

## After Clicking "Search" Button

These are the critical requests made when the user clicks the "Search" button:

```
[POST] https://timetable.nycu.edu.tw/?r=main/get_cos_list
Status: 200 OK
Purpose: **PRIMARY ENDPOINT** - Get the actual course list data in JSON format

[GET] https://timetable.nycu.edu.tw/public/images/ajax-loader.gif
Status: 200 OK
Purpose: Loading indicator image

[POST] https://timetable.nycu.edu.tw/?r=main/getViewHtmlContents
Status: 200 OK
Purpose: Convert the JSON course data into HTML table format for display
```

## Request Headers for AJAX Calls

Based on the JavaScript code analysis, AJAX requests should include:

```
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
Accept: application/json, text/javascript, */*; q=0.01
```

## Failed Requests

```
[GET] https://timetable.nycu.edu.tw/favicon.ico
Status: 404 Not Found
(This is expected - the site doesn't have a favicon)
```

## Request Sequence Summary

### Phase 1: Initial Load
1. Main HTML page
2. CSS files
3. JavaScript files

### Phase 2: Data Population (Automatic)
4-17. Multiple POST requests to populate form dropdowns and get metadata

### Phase 3: Course Search (User Action)
18. `get_cos_list` - Fetch course data (JSON)
19. `getViewHtmlContents` - Render course data as HTML

## Key Observations

1. **All AJAX requests use POST method** even though some might logically be GET requests
2. **The `get_cos_list` endpoint is the most important** - it returns the actual course data
3. **Two-step rendering process:** JSON data is fetched first, then converted to HTML
4. **Cascading dropdowns:** Department dropdown depends on college selection, which triggers new AJAX calls
5. **No authentication required:** All requests work without login/cookies
6. **URL structure:** All endpoints use query parameter `?r=main/<endpoint_name>`

## Total Requests

- Static resources: 7 requests
- AJAX calls (initial): 13 requests
- AJAX calls (search): 2 requests
- Images: 2 requests
- **Total: 24 successful requests**
