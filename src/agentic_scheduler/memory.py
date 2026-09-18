import sqlite3

from agentic_scheduler.config import MEMORY_DB


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(MEMORY_DB)


def init_db():
    MEMORY_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,        -- "user" or "agent"
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def save_message(role, message):
    conn = _connect()
    conn.execute(
        "INSERT INTO conversation (role, message) VALUES (?, ?)",
        (role, message)
    )
    conn.commit()
    conn.close()


def load_conversation():
    conn = _connect()
    rows = conn.execute(
        "SELECT role, message, timestamp FROM conversation ORDER BY id"
    ).fetchall()
    conn.close()
    return rows
