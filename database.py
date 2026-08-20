"""
database.py
-----------
Lightweight persistence layer for the Meeting Summarizer.

Uses SQLite (Python's built-in `sqlite3` module — no extra dependency)
to store every processed meeting: filename, timestamp, transcript, and
summary. This satisfies the assignment's "Backend to store & process
data" requirement without introducing any new package.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "meetings.db"


@contextmanager
def get_connection():
    """Yield a SQLite connection and guarantee it's closed afterward."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Create the meetings table if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                transcript TEXT NOT NULL,
                summary TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_meeting(filename: str, transcript: str, summary: str) -> int:
    """Insert a processed meeting and return its new row id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO meetings (filename, created_at, transcript, summary)
            VALUES (?, ?, ?, ?)
            """,
            (filename, datetime.now().isoformat(timespec="seconds"), transcript, summary),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_meetings():
    """Return all meetings, most recent first (id, filename, created_at only)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, created_at FROM meetings ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_meeting(meeting_id: int):
    """Return the full record (including transcript/summary) for one meeting."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
        ).fetchone()
        return dict(row) if row else None


def delete_meeting(meeting_id: int):
    """Remove a single meeting record."""
    with get_connection() as conn:
        conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
        conn.commit()
