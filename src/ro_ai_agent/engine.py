from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, load_config
from .memory import init_memory, save_message
from .pipeline import IntentIndex, load_intents
from .faq import FaqIndex, load_faq


@dataclass
class AgentEngine:
    index: IntentIndex
    config: AgentConfig
    memory_db: Path
    faq: FaqIndex

    @classmethod
    def from_paths(cls, intents_path: Path, config_path: Path, memory_db: Path) -> "AgentEngine":
        config = load_config(config_path)
        intents = load_intents(intents_path)
        index = IntentIndex(intents)
        init_memory(memory_db)
        faq_path = intents_path.parent / "faq_ro.json"
        faq = load_faq(faq_path)
        return cls(index=index, config=config, memory_db=memory_db, faq=faq)

    def respond(self, text: str) -> tuple[str, float]:
        intent, score = self.index.match(text)
        if intent is not None and score >= self.config.min_similarity:
            reply = intent.response
        else:
            reply = self._fallback(text)

        now = datetime.now(timezone.utc).isoformat()
        save_message(self.memory_db, "user", text, now)
        save_message(self.memory_db, "assistant", reply, now)
        return reply, score

    def _fallback(self, text: str) -> str:
        text_l = text.lower()
        if any(k in text_l for k in ["ajutor", "help", "ce stii", "capabilitati", "ce poti"]):
            return self._capabilities()
        faq_reply = self.faq.match(text)
        if faq_reply:
            return faq_reply
        return "Nu sunt sigur. Poti reformula?"

    def _capabilities(self) -> str:
        names = [intent.name for intent in self.index.intents]
        examples = [intent.examples[0] for intent in self.index.intents if intent.examples]
        return (
            "Pot raspunde la intenturi: "
            + ", ".join(names)
            + ". Incearca: "
            + "; ".join(examples)
        )
