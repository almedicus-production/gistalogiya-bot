import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            lang TEXT DEFAULT 'uz',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_user_lang(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "uz"

def set_user_lang(user_id: int, lang: str, username: str = "", first_name: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (user_id, username, first_name, lang)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang, username = excluded.username, first_name = excluded.first_name
    """, (user_id, username, first_name, lang))
    conn.commit()
    conn.close()

def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT lang, COUNT(*) FROM users GROUP BY lang")
    by_lang = dict(cur.fetchall())

    cur.execute("SELECT COUNT(*) FROM users WHERE date(created_at) = date('now')")
    today_users = cur.fetchone()[0]

    conn.close()
    return {
        "total": total_users,
        "by_lang": by_lang,
        "today": today_users
    }
