from datetime import UTC, datetime
from pathlib import Path

from ro_ai_agent.memory import (
    add_learned_faq,
    add_policy_rule,
    enqueue_learning,
    fetch_last,
    init_memory,
    list_learning_queue,
    list_policy_rules,
    save_message,
)


def test_memory_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "mem.db"
    init_memory(db)
    save_message(db, "user", "salut", datetime.now(UTC).isoformat())
    rows = fetch_last(db, 1)
    assert rows
    assert rows[0][0] == "user"


def test_learning_queue_and_policy(tmp_path: Path) -> None:
    db = tmp_path / "mem.db"
    init_memory(db)
    enqueue_learning(db, "ce stii sa spui?", datetime.now(UTC).isoformat())
    items = list_learning_queue(db)
    assert items
    add_learned_faq(db, "ce stii sa spui?", "pot raspunde", datetime.now(UTC).isoformat())
    add_policy_rule(db, "secret", "deny")
    rules = list_policy_rules(db)
    assert rules
