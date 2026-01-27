from pathlib import Path
from datetime import datetime, timezone

from ro_ai_agent.memory import init_memory, save_message, fetch_last


def test_memory_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "mem.db"
    init_memory(db)
    save_message(db, "user", "salut", datetime.now(timezone.utc).isoformat())
    rows = fetch_last(db, 1)
    assert rows
    assert rows[0][0] == "user"
