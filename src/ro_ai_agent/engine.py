from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, load_config
from .memory import init_memory, save_message
from .pipeline import IntentIndex, load_intents


@dataclass
class AgentEngine:
    index: IntentIndex
    config: AgentConfig
    memory_db: Path

    @classmethod
    def from_paths(cls, intents_path: Path, config_path: Path, memory_db: Path) -> "AgentEngine":
        config = load_config(config_path)
        intents = load_intents(intents_path)
        index = IntentIndex(intents)
        init_memory(memory_db)
        return cls(index=index, config=config, memory_db=memory_db)

    def respond(self, text: str) -> str:
        intent, score = self.index.match(text)
        if intent is None or score < self.config.min_similarity:
            reply = "Nu sunt sigur. Poti reformula?"
        else:
            reply = intent.response

        now = datetime.now(timezone.utc).isoformat()
        save_message(self.memory_db, "user", text, now)
        save_message(self.memory_db, "assistant", reply, now)
        return reply
