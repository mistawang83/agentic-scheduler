import sqlite3
import os

if not os.path.exists("storage"):
    os.makedirs("storage")

conn = sqlite3.connect("storage/memory.db") 
cursor = conn.cursor()

cursor.execute("""
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
    conn = sqlite3.connect("storage/memory.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO conversation (role, message) VALUES (?, ?)",
        (role, message)
    )

    conn.commit()
    conn.close()

def load_conversation():
    conn = sqlite3.connect("storage/memory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT role, message, timestamp FROM conversation ORDER BY id")
    rows = cursor.fetchall()

    conn.close()
    return rows
