# NYCU Course Platform — Project Guide

This file serves as a comprehensive guide for working on the **NYCU Course Platform** project.  It has two primary goals:

1.  **Project Documentation** — explain how to set up, run, and extend the codebase.  This includes details about the scraping pipeline, database schema, backend API, and frontend application.
2.  **Claude Code Integration** — capture the best practices recommended by Anthropic for using Claude Code.  By following these practices and keeping this document up‑to‑date, developers can maximize productivity and ensure Claude has the right context when assisting with the project.

## Overview

The NYCU Course Platform aims to provide a fast, searchable interface for students to explore course offerings at National Yang Ming Chiao Tung University.  It was inspired by the "NDHU 東華查課拉" site and follows a similar architectural pattern:

- **Data extraction**: a Playwright‑based scraper enumerates every academic year and semester, pulls a list of course numbers, and fetches each course's detailed syllabus page.  Parsed data are stored in a relational database.
- **Database layer**: a small SQLite (or Postgres) database stores semesters and courses.  The schema is defined in `data/schema.sql`.
- **Backend API**: a FastAPI service exposes REST endpoints to query semesters, list courses with filters, and fetch individual course details.
- **Frontend application**: a Next.js 14 + TypeScript web app provides a user interface for browsing semesters, searching courses, viewing detailed syllabi, and (in future iterations) building personal schedules.  The frontend proxies API calls to the backend via a rewrite defined in `next.config.js`.

## Getting Started

1.  **Clone the repository** and navigate into the `nycu_course_platform` directory.
2.  **Set up Python** — create a virtual environment and install dependencies for the scraper and backend:

    ```bash
    cd scraper
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ../backend
    pip install -r requirements.txt
    ```

3.  **Configure environment variables** (optional).  You can set `DATABASE_URL` to point to a Postgres database.  By default, the backend uses a local SQLite file `nycu_courses.db` in the project root.

4.  **Run the scraper** — the scraper is designed to iterate over academic years and semesters, discover all course numbers via Playwright automation, and fetch detailed syllabi.  The results are saved to `scraper/data/courses.json` and imported into the database via the import script:

    ```bash
    cd scraper
    # The first run downloads Playwright browsers
    playwright install
    python scraper.py
    cd ..
    python scripts/import_data.py
    ```

5.  **Start the backend API** — launch the FastAPI server:

    ```bash
    uvicorn backend.app:app --reload --port 8000
    ```

6.  **Install Node.js dependencies for the frontend** and run the development server:

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

7.  **Open the application** at `http://localhost:3000` and begin exploring courses.  When you select a semester, the frontend issues calls to `http://localhost:8000/semesters` and `http://localhost:8000/courses` via the configured rewrite.

## Data Pipeline Details

The scraper uses Playwright to simulate user interactions with the official NYCU timetable site.  For each semester defined in the `config.py` file, it opens the search form, enumerates departments/filters, and collects all course numbers.  It then constructs syllabus URLs of the form:

```
https://timetable.nycu.edu.tw/?r=main%2Fcrsoutline&Acy=<YEAR>&Sem=<SEM>&CrsNo=<COURSE_NUMBER>
```

Each syllabus page is parsed with BeautifulSoup to extract structured data: course name, permanent number, credits, category (required/elective), instructor(s), day/time/classroom codes, objectives, evaluation methods, references, weekly schedule, and any attachments.  The scraper respects polite crawling practices by throttling requests and following the university’s published guidelines on automated access.

After the scrape completes, run the `import_data.py` script from the `scripts` folder to load the resulting JSON into the database.  The schema in `data/schema.sql` defines `semesters` and `courses` tables and can be migrated to Postgres if desired.

## Backend API

The FastAPI service (`backend/app.py`) provides three main endpoints:

| Path | Method | Description |
| --- | --- | --- |
| `/semesters` | `GET` | Returns a list of available semesters (academic year + semester) sorted by year descending. |
| `/courses` | `GET` | Accepts optional query parameters (`acy`, `sem`, `dept`, `teacher`, `q`) and returns a list of courses that match the filters.  The response is limited to 200 courses by default. |
| `/courses/{course_id}` | `GET` | Returns the full details of a single course, including any long text fields. |

You can extend the API with additional endpoints (e.g. search by keywords, fuzzy matching) or adopt GraphQL for more flexible queries.

## Frontend Overview

The frontend lives in `frontend/` and is built with Next.js 14, TypeScript, and Tailwind CSS.  It demonstrates a few core features:

1.  **Semester selector** — a dropdown populated from the `/semesters` endpoint.  When you choose a semester, the frontend fetches all courses for that term via the `/courses` endpoint.
2.  **Course list** — displays course cards with names, course numbers, and instructor names.  Each card links to a dedicated course page.
3.  **Course details page** — fetches a single course by ID and renders the full description.  Long text fields are injected into the DOM via `dangerouslySetInnerHTML`; sanitization libraries can be added if necessary.
4.  **Schedule builder (placeholder)** — the `schedule.tsx` page provides a foundation for future schedule planning.  In subsequent iterations, you can implement drag‑and‑drop, clash detection, and .ics export.

`next.config.js` defines a rewrite so that any `/api/*` request from the frontend is transparently proxied to the backend on port 8000.  For production deployment, update this destination to your hosted API.

## Using Claude Code with This Project

Anthropic’s **Claude Code** is a command‑line tool that provides agentic coding assistance.  According to Anthropic’s engineering guidelines, you can customize how Claude interacts with your codebase by creating a `CLAUDE.md` file at the root of your repository【617913250936872†L48-L59】.  This file should document common commands, code style preferences, workflow tips, and any project‑specific quirks.  When you run Claude Code, it automatically pulls in the contents of `CLAUDE.md` and uses them to guide the assistant’s behaviour【617913250936872†L48-L59】.

Key recommendations from Anthropic’s best practices include:

- **Document commands and workflows** — list useful scripts (e.g. `npm run dev`, `uvicorn backend.app:app`), code style conventions (e.g. use ES modules, destructure imports), and repository etiquette in your `CLAUDE.md`【617913250936872†L50-L75】.  This helps Claude understand how to build, test, and run your project.
- **Iterate on your CLAUDE.md** — treat this file as a living prompt.  Regularly refine the instructions to improve Claude’s adherence to your preferred workflows and coding standards【617913250936872†L99-L105】.
- **Curate allowed tools** — Claude Code uses a conservative allow‑list of tools for safety.  You can customize this allow‑list via your `.claude/settings.json` or the `--allowedTools` CLI flag to permit commands like `git`, `docker`, or your own scripts【617913250936872†L118-L134】.

In addition to these general guidelines, you might add sections to your `CLAUDE.md` explaining the structure of the scraper, details of the database schema, the API endpoints, and frontend development conventions.  When you run Claude Code inside the `nycu_course_platform` folder, it will automatically ingest your `CLADE.md` and provide contextually aware assistance.

## Contributing and Future Work

- **Enhance the scraper** — integrate fallback strategies such as enumerating possible course numbers or reading course lists from third‑party sources to handle semesters where search results are incomplete.
- **Improve the database** — normalize instructors, classrooms, and scheduling into separate tables.  Index frequently queried fields (e.g. course names, departments) for faster lookup.
- **Add authentication and personalization** — implement user accounts so students can save schedules to the cloud.  Consider using Supabase Auth or an OAuth provider supported by NYCU.
- **Deploy serverless** — migrate the API to serverless platforms like Vercel Functions or Cloudflare Workers.  Use serverless databases (Neon, Supabase) and edge caching to improve latency.  With the provided API rewrite, the frontend can remain unchanged.
- **Accessibility and internationalization** — follow accessibility best practices (e.g. ARIA labels) and support multiple languages (Chinese, English) as found on the official timetable site.

## Disclaimer

This project is for educational purposes.  Always respect the target website’s terms of service and robots.txt; implement appropriate throttling and caching when scraping.  The scraper assumes that the NYCU timetable site continues to provide syllabi via query parameters for at least the years 99–114, as observed in 2025【617913250936872†L14-L34】.  If the university updates their systems or restricts access, adapt the pipeline accordingly.
