-- Migration: Create schedules and schedule_courses tables
-- Date: 2025-10-17
-- Description: Add course scheduling (timetable) feature

-- Create schedules table
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    acy INTEGER NOT NULL CHECK (acy > 0),
    sem INTEGER NOT NULL CHECK (sem >= 1 AND sem <= 2),
    user_id VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for schedules
CREATE INDEX IF NOT EXISTS idx_schedules_user_id ON schedules (user_id);
CREATE INDEX IF NOT EXISTS idx_schedules_acy ON schedules (acy);
CREATE INDEX IF NOT EXISTS idx_schedules_sem ON schedules (sem);

-- Create schedule_courses table (association table)
CREATE TABLE IF NOT EXISTS schedule_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    color VARCHAR,
    notes VARCHAR,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
    UNIQUE (schedule_id, course_id)
);

-- Create indexes for schedule_courses
CREATE INDEX IF NOT EXISTS idx_schedule_courses_schedule_id ON schedule_courses (schedule_id);
CREATE INDEX IF NOT EXISTS idx_schedule_courses_course_id ON schedule_courses (course_id);
