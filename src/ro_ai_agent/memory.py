from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def init_memory(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def save_message(db_path: Path, role: str, content: str, created_at: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO messages(role, content, created_at) VALUES(?,?,?)",
            (role, content, created_at),
        )
        conn.commit()


def fetch_last(db_path: Path, limit: int = 5) -> list[tuple[str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]
