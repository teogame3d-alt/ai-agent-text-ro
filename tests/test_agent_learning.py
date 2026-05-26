from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ro_ai_agent.engine import AgentEngine
from ro_ai_agent.memory import add_learned_faq, list_learning_queue


def test_agent_learns_user_approved_answer(tmp_path: Path) -> None:
    """Unknown questions are queued, then approved answers become reusable knowledge."""

    data_dir = Path(__file__).resolve().parents[1] / "data"
    memory_db = tmp_path / "memory.db"
    engine = AgentEngine.from_paths(
        data_dir / "intents_ro.json",
        data_dir / "config.json",
        memory_db,
    )

    unknown_question = "protocol nimbus pentru stilul meu personal"
    first_reply, _score = engine.respond(unknown_question)

    assert first_reply == "Nu sunt sigur. Poti reformula?"
    assert list_learning_queue(memory_db)

    approved_answer = "Agentul poate fi ghidat prin raspunsuri aprobate si reguli explicite."
    add_learned_faq(
        memory_db,
        unknown_question,
        approved_answer,
        datetime.now(UTC).isoformat(),
    )

    second_reply, _score = engine.respond("nimbus pentru stilul meu")

    assert second_reply == approved_answer
