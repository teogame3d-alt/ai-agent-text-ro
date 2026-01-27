from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, load_config
from .memory import (
    add_policy_rule,
    enqueue_learning,
    init_memory,
    list_learned_faq,
    list_policy_rules,
    save_message,
)
from .pipeline import IntentIndex, load_intents
from .faq import FaqIndex, load_faq, tokenize
from .learning import LearnedEntry, LearnedIndex


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
        policy_action = self._check_policy(text)
        if policy_action == "deny":
            reply = "Nu pot raspunde la aceasta intrebare."
            score = 0.0
            self._persist(text, reply)
            return reply, score

        intent, score = self.index.match(text)
        if intent is not None and score >= self.config.min_similarity:
            reply = intent.response
        else:
            reply = self._fallback(text)

        self._persist(text, reply)
        return reply, score

    def _fallback(self, text: str) -> str:
        text_l = text.lower()
        if any(k in text_l for k in ["ajutor", "help", "ce stii", "capabilitati", "ce poti"]):
            return self._capabilities()
        learned = self._learned_match(text)
        if learned:
            return learned
        faq_reply = self.faq.match(text)
        if faq_reply:
            return faq_reply
        enqueue_learning(self.memory_db, text, datetime.now(timezone.utc).isoformat())
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

    def _persist(self, text: str, reply: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        save_message(self.memory_db, "user", text, now)
        save_message(self.memory_db, "assistant", reply, now)

    def _learned_match(self, text: str) -> str | None:
        entries = [LearnedEntry(q, r) for q, r in list_learned_faq(self.memory_db)]
        return LearnedIndex(entries).match(text)

    def _check_policy(self, text: str) -> str | None:
        tokens = tokenize(text)
        for keyword, action in list_policy_rules(self.memory_db):
            if keyword.lower() in tokens:
                return action
        return None

    def add_policy_keyword(self, keyword: str, action: str) -> None:
        add_policy_rule(self.memory_db, keyword, action)
