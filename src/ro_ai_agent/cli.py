from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import load_config
from .memory import fetch_last, init_memory, save_message
from .pipeline import IntentIndex, load_intents
from .tts import speak


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    data_path = base / "data" / "intents_ro.json"
    cfg_path = base / "data" / "config.json"
    memory_db = base / "data" / "memory.db"

    cfg = load_config(cfg_path)
    intents = load_intents(data_path)
    index = IntentIndex(intents)
    init_memory(memory_db)

    print("AI Agent Text RO. Type 'exit' to quit.")
    while True:
        text = input("> ").strip()
        if text.lower() in {"exit", "quit"}:
            break

        intent, score = index.match(text)
        if intent is None or score < cfg.min_similarity:
            reply = "Nu sunt sigur. Poti reformula?"
        else:
            reply = intent.response

        now = datetime.now(timezone.utc).isoformat()
        save_message(memory_db, "user", text, now)
        save_message(memory_db, "assistant", reply, now)
        print(reply)

        if cfg.enable_voice:
            try:
                speak(reply)
            except Exception as exc:
                print(f"TTS error: {exc}")

    print("Last messages:")
    for role, content, ts in fetch_last(memory_db, 5):
        print(f"{ts} | {role}: {content}")


if __name__ == "__main__":
    main()
