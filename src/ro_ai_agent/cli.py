from __future__ import annotations

"""RO: Entry point CLI pentru agent; util in PyCharm/VS Code run config.
EN: CLI entry point for the agent; IDE-friendly for quick runs.
"""

from pathlib import Path

from .engine import AgentEngine
from .memory import fetch_last
from .tts import speak


def main() -> None:
    """RO: Ruleaza bucla de chat in terminal.
    EN: Run a terminal chat loop.
    """
    base = Path(__file__).resolve().parents[2]
    data_path = base / "data" / "intents_ro.json"
    cfg_path = base / "data" / "config.json"
    memory_db = base / "data" / "memory.db"

    engine = AgentEngine.from_paths(data_path, cfg_path, memory_db)

    print("AI Agent Text RO. Type 'exit' to quit.")
    while True:
        text = input("> ").strip()
        if text.lower() in {"exit", "quit"}:
            break

        reply, score = engine.respond(text)
        print(reply)
        print(f"(confidence: {score:.2f})")

        if engine.config.enable_voice:
            try:
                speak(reply)
            except Exception as exc:
                print(f"TTS error: {exc}")

    print("Last messages:")
    for role, content, ts in fetch_last(memory_db, 5):
        print(f"{ts} | {role}: {content}")


if __name__ == "__main__":
    main()
