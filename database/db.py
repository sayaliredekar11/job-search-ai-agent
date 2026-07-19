import json
import os
import sqlite3
from contextlib import contextmanager

# database/app.db, next to this file, regardless of the current working directory
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "app.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")


@contextmanager
def get_connection():
    """Yields a sqlite3 connection with foreign keys enabled and row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Creates the database file and all tables if they don't already exist.
    Safe to call on every app startup (app.py)."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    with get_connection() as conn:
        conn.executescript(schema)


# Resumes  (src/pdf_reader.py output)

def save_resume(filename, resume_text):
    """Persists an uploaded resume's extracted text. Returns the new resume id."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO resumes (filename, resume_text) VALUES (?, ?)",
            (filename, resume_text),
        )
        return cur.lastrowid


def get_resume(resume_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_resumes():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, uploaded_at FROM resumes ORDER BY uploaded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


# Searches  (app.py search form)

def save_search(job_title, location, employment_filter, company_filter, query_string):
    """Persists one search submission. Returns the new search id."""
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO searches
               (job_title, location, employment_filter, company_filter, query_string)
               VALUES (?, ?, ?, ?, ?)""",
            (job_title, location, employment_filter, company_filter, query_string),
        )
        return cur.lastrowid


def get_recent_searches(limit=20):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM searches ORDER BY searched_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# Jobs  (src/jobs.py search_jobs() results, real or MOCK_JOBS fallback)

def save_job(job, search_id=None):
    """Persists (or updates) a single job dict as returned by search_jobs().

    job_id is UNIQUE, so re-saving the same job (e.g. re-running a search)
    updates the existing row instead of duplicating it. Returns the local
    integer primary key (jobs.id), which other tables reference.
    """
    job_id = job.get("job_id")
    employment_types = json.dumps(job.get("job_employment_types") or [])

    with get_connection() as conn:
        conn.execute(
            """INSERT INTO jobs (
                    job_id, job_title, employer_name, job_city,
                    job_employment_type, job_employment_types, job_apply_link,
                    job_min_salary, job_max_salary, job_description, search_id
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(job_id) DO UPDATE SET
                    job_title=excluded.job_title,
                    employer_name=excluded.employer_name,
                    job_city=excluded.job_city,
                    job_employment_type=excluded.job_employment_type,
                    job_employment_types=excluded.job_employment_types,
                    job_apply_link=excluded.job_apply_link,
                    job_min_salary=excluded.job_min_salary,
                    job_max_salary=excluded.job_max_salary,
                    job_description=excluded.job_description,
                    search_id=excluded.search_id
            """,
            (
                job_id,
                job.get("job_title"),
                job.get("employer_name"),
                job.get("job_city"),
                job.get("job_employment_type"),
                employment_types,
                job.get("job_apply_link"),
                job.get("job_min_salary"),
                job.get("job_max_salary"),
                job.get("job_description"),
                search_id,
            ),
        )
        row = conn.execute(
            "SELECT id FROM jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
        return row["id"]


def get_jobs_for_search(search_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE search_id = ? ORDER BY id", (search_id,)
        ).fetchall()
        jobs = []
        for r in rows:
            d = dict(r)
            d["job_employment_types"] = json.loads(d["job_employment_types"] or "[]")
            jobs.append(d)
        return jobs


def get_job_by_local_id(local_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (local_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["job_employment_types"] = json.loads(d["job_employment_types"] or "[]")
        return d


# Job analysis  (src/ai.py analyze_job() -> "Analyze with AI" button)

def save_job_analysis(job_local_id, analysis_text):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO job_analysis (job_id, analysis_text) VALUES (?, ?)",
            (job_local_id, analysis_text),
        )
        return cur.lastrowid


def get_analysis_history_for_job(job_local_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM job_analysis WHERE job_id = ? ORDER BY analyzed_at DESC",
            (job_local_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# Resume-fit matches  (src/ai.py analyze_resume_match() -> "Analyze Resume Fit")

def save_resume_match(resume_id, job_local_id, match_score, analysis_text):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO resume_match (resume_id, job_id, match_score, analysis_text)
               VALUES (?, ?, ?, ?)""",
            (resume_id, job_local_id, match_score, analysis_text),
        )
        return cur.lastrowid


def get_resume_match_history(resume_id):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT rm.*, j.job_title, j.employer_name
               FROM resume_match rm
               JOIN jobs j ON j.id = rm.job_id
               WHERE rm.resume_id = ?
               ORDER BY rm.analyzed_at DESC""",
            (resume_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_top_matches_for_resume(resume_id, limit=5):
    """Best-scoring jobs for a given resume, useful for a 'top matches' view."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT rm.match_score, rm.analyzed_at, j.job_title, j.employer_name, j.job_apply_link
               FROM resume_match rm
               JOIN jobs j ON j.id = rm.job_id
               WHERE rm.resume_id = ? AND rm.match_score IS NOT NULL
               ORDER BY rm.match_score DESC
               LIMIT ?""",
            (resume_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    
def save_chat_message(role, content, resume_id=None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_messages (resume_id, role, content) VALUES (?, ?, ?)",
            (resume_id, role, content),
        )


def get_chat_history(resume_id=None):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content FROM chat_messages WHERE resume_id IS ? ORDER BY id",
            (resume_id,),
        ).fetchall()
        return [dict(r) for r in rows]

if __name__ == "__main__":
    # Quick manual sanity check: `python database/db.py`
    init_db()
    print(f"Database initialized at {DB_PATH}")





