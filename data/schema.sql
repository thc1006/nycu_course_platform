-- Schema for NYCU course database

-- Table of semesters (academic year & semester).  This table can be
-- referenced by courses.  A composite unique index ensures that each
-- (acy, sem) pair appears only once.
CREATE TABLE IF NOT EXISTS semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acy INTEGER NOT NULL,
    sem INTEGER NOT NULL,
    UNIQUE(acy, sem)
);

-- Table of courses.  Each row corresponds to a single course offering.
-- The semester_id column references the semesters table, linking
-- courses to their academic year and semester.
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL,
    crs_no TEXT NOT NULL,
    permanent_crs_no TEXT,
    name TEXT NOT NULL,
    credits REAL,
    required TEXT,
    teacher TEXT,
    dept TEXT,
    day_codes TEXT,
    time_codes TEXT,
    classroom_codes TEXT,
    url TEXT,
    details TEXT,
    FOREIGN KEY(semester_id) REFERENCES semesters(id)
);