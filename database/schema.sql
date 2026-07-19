-- Schema for Job Search AI Agent
-- Mirrors the data actually produced/consumed by src/jobs.py, src/pdf_reader.py,
-- and src/ai.py so search history, resumes, and AI analyses can be persisted
-- across Streamlit sessions instead of living only in st.session_state.

PRAGMA foreign_keys = ON;

-- One row per resume uploaded via the sidebar PDF uploader (src/pdf_reader.py)
CREATE TABLE IF NOT EXISTS resumes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    filename      TEXT NOT NULL,
    resume_text   TEXT NOT NULL,
    uploaded_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One row per user search (job_title + location + filters), from app.py
CREATE TABLE IF NOT EXISTS searches (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title           TEXT,
    location             TEXT,
    employment_filter    TEXT,
    company_filter       TEXT,
    query_string          TEXT,
    searched_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One row per job result returned by search_jobs() in src/jobs.py
-- (real JSearch/RapidAPI results or MOCK_JOBS fallback), fields match
-- the dict keys used throughout jobs.py / ui.py.
CREATE TABLE IF NOT EXISTS jobs (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id                TEXT UNIQUE,           -- e.g. "mock_1" or JSearch job_id
    job_title             TEXT,
    employer_name         TEXT,
    job_city              TEXT,
    job_employment_type   TEXT,                  -- human readable, e.g. "Full-time"
    job_employment_types  TEXT,                   -- JSON array, e.g. ["FULLTIME"]
    job_apply_link        TEXT,
    job_min_salary        INTEGER,
    job_max_salary         INTEGER,
    job_description        TEXT,
    search_id               INTEGER,              -- which search returned this job
    fetched_at               TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (search_id) REFERENCES searches (id) ON DELETE SET NULL
);

-- Results of analyze_job() in src/ai.py ("Analyze with AI" button)
CREATE TABLE IF NOT EXISTS job_analysis (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL,
    analysis_text    TEXT NOT NULL,
    analyzed_at       TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);

-- Results of analyze_resume_match() in src/ai.py ("Analyze Resume Fit" button)
-- Stores both the raw markdown and the parsed match score for querying/history.
CREATE TABLE IF NOT EXISTS resume_match (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id          INTEGER NOT NULL,
    job_id               INTEGER NOT NULL,
    match_score           INTEGER,               -- parsed 0-100 score, nullable if parse fails
    analysis_text          TEXT NOT NULL,          -- full markdown returned by Gemini
    analyzed_at             TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id    INTEGER,
    role         TEXT NOT NULL,   -- "user" or "model"
    content      TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_resume_id ON chat_messages (resume_id);


CREATE INDEX IF NOT EXISTS idx_jobs_search_id ON jobs (search_id);
CREATE INDEX IF NOT EXISTS idx_job_analysis_job_id ON job_analysis (job_id);
CREATE INDEX IF NOT EXISTS idx_resume_match_resume_id ON resume_match (resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_match_job_id ON resume_match (job_id);
