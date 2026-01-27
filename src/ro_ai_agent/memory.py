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

CREATE TABLE IF NOT EXISTS learning_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learned_faq (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question TEXT NOT NULL,
  response TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policy_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword TEXT NOT NULL,
  action TEXT NOT NULL
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


def enqueue_learning(db_path: Path, question: str, created_at: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO learning_queue(question, status, created_at) VALUES(?,?,?)",
            (question, "pending", created_at),
        )
        conn.commit()


def list_learning_queue(db_path: Path) -> list[tuple[int, str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, question, status, created_at FROM learning_queue ORDER BY id DESC"
        ).fetchall()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def mark_learning(db_path: Path, item_id: int, status: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE learning_queue SET status=? WHERE id=?", (status, item_id))
        conn.commit()


def add_learned_faq(db_path: Path, question: str, response: str, created_at: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO learned_faq(question, response, created_at) VALUES(?,?,?)",
            (question, response, created_at),
        )
        conn.commit()


def list_learned_faq(db_path: Path) -> list[tuple[str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT question, response FROM learned_faq").fetchall()
    return [(r[0], r[1]) for r in rows]


def add_policy_rule(db_path: Path, keyword: str, action: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO policy_rules(keyword, action) VALUES(?,?)",
            (keyword, action),
        )
        conn.commit()


def list_policy_rules(db_path: Path) -> list[tuple[str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT keyword, action FROM policy_rules").fetchall()
    return [(r[0], r[1]) for r in rows]
