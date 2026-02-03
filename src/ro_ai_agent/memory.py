from __future__ import annotations

"""RO: Persistenta SQLite pentru mesaje, invatare si reguli de politica.
EN: SQLite persistence for messages, learning queue, and policy rules.
"""

import sqlite3
from pathlib import Path
import json

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
    """RO: Creeaza structura DB daca nu exista.
    EN: Create DB schema if it does not exist.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def save_message(db_path: Path, role: str, content: str, created_at: str) -> None:
    """RO: Salveaza un mesaj din conversatie.
    EN: Store a conversation message.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO messages(role, content, created_at) VALUES(?,?,?)",
            (role, content, created_at),
        )
        conn.commit()


def fetch_last(db_path: Path, limit: int = 5) -> list[tuple[str, str, str]]:
    """RO: Ia ultimele N mesaje pentru recapitulare.
    EN: Fetch last N messages for a quick recap.
    """
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]


def enqueue_learning(db_path: Path, question: str, created_at: str) -> None:
    """RO: Adauga o intrebare necunoscuta in coada de invatare.
    EN: Queue an unknown question for human review.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO learning_queue(question, status, created_at) VALUES(?,?,?)",
            (question, "pending", created_at),
        )
        conn.commit()


def list_learning_queue(db_path: Path) -> list[tuple[int, str, str, str]]:
    """RO: Listeaza intrebarile aflate in coada de invatare.
    EN: List all learning-queue items.
    """
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, question, status, created_at FROM learning_queue ORDER BY id DESC"
        ).fetchall()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def mark_learning(db_path: Path, item_id: int, status: str) -> None:
    """RO: Marcheaza un item ca approved/denied.
    EN: Mark a learning item as approved/denied.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE learning_queue SET status=? WHERE id=?", (status, item_id))
        conn.commit()


def add_learned_faq(db_path: Path, question: str, response: str, created_at: str) -> None:
    """RO: Salveaza un raspuns invatat manual.
    EN: Store a human-approved answer.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO learned_faq(question, response, created_at) VALUES(?,?,?)",
            (question, response, created_at),
        )
        conn.commit()


def append_learned_json(db_path: Path, question: str, response: str, created_at: str, lang: str) -> None:
    """RO: Pastreaza o urma vizibila in JSON (audit pentru invatare).
    EN: Keep a visible JSON audit trail for learned items.
    """
    path = db_path.parent / "learned_faq.json"
    entry = {
        "lang": lang,
        "question": question,
        "response": response,
        "created_at": created_at,
    }
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                data.append(entry)
            else:
                data = [entry]
        except Exception:
            data = [entry]
    else:
        data = [entry]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_learned_faq(db_path: Path) -> list[tuple[str, str]]:
    """RO: Listeaza toate raspunsurile invatate.
    EN: List all learned FAQ entries.
    """
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT question, response FROM learned_faq").fetchall()
    return [(r[0], r[1]) for r in rows]


def add_policy_rule(db_path: Path, keyword: str, action: str) -> None:
    """RO: Adauga o regula simpla allow/deny.
    EN: Add a simple allow/deny rule.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO policy_rules(keyword, action) VALUES(?,?)",
            (keyword, action),
        )
        conn.commit()


def list_policy_rules(db_path: Path) -> list[tuple[str, str]]:
    """RO: Intoarce toate regulile active.
    EN: Return all active policy rules.
    """
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT keyword, action FROM policy_rules").fetchall()
    return [(r[0], r[1]) for r in rows]
