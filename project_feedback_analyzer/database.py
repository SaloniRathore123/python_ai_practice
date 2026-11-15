import sqlite3

DB_FILE = "feedback.db"

def init_db():
    """Initialize the SQLite database and create the feedback table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT NOT NULL,
            label TEXT NOT NULL,
            score INTEGER NOT NULL,
            theme TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def save_feedback(review, label, score, theme):
    """Save feedback to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (review, label, score, theme) VALUES (?, ?, ?, ?)",
        (review, label, score, theme),
    )
    conn.commit()
    conn.close()

def load_feedback_history():
    """Load feedback history from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT review, label, score, theme FROM feedback ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"text": row[0], "label": row[1], "score": row[2], "theme": row[3]} for row in rows]