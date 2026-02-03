from __future__ import annotations

"""RO: Motorul principal al agentului text; combina intenturi, reguli si memorie.
EN: Core text-agent engine; ties intents, policy rules, and persistence together.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import AgentConfig, load_config
from .lang import detect_lang
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
    """RO: Expune API-ul de raspuns si pastreaza dependintele agentului.
    EN: Public API for responses and a home for the agent's dependencies.
    """
    index: IntentIndex
    config: AgentConfig
    memory_db: Path
    faq: FaqIndex
    index_en: IntentIndex
    faq_en: FaqIndex

    @classmethod
    def from_paths(cls, intents_path: Path, config_path: Path, memory_db: Path) -> "AgentEngine":
        """RO: Incarca configuratia, intenturile si initializeaza baza de date.
        EN: Load config/intents and ensure the database is ready.
        """
        config = load_config(config_path)
        intents = load_intents(intents_path)
        index = IntentIndex(intents)
        init_memory(memory_db)
        faq_path = intents_path.parent / "faq_ro.json"
        faq = load_faq(faq_path)

        intents_en_path = intents_path.parent / "intents_en.json"
        intents_en = load_intents(intents_en_path)
        index_en = IntentIndex(intents_en)
        faq_en_path = intents_path.parent / "faq_en.json"
        faq_en = load_faq(faq_en_path)

        return cls(
            index=index,
            config=config,
            memory_db=memory_db,
            faq=faq,
            index_en=index_en,
            faq_en=faq_en,
        )

    def respond(self, text: str) -> tuple[str, float]:
        """RO: Genereaza raspunsul final si scorul de potrivire.
        EN: Produce the final reply plus a similarity score.
        """
        policy_action = self._check_policy(text)
        if policy_action == "deny":
            reply = "Nu pot raspunde la aceasta intrebare."
            score = 0.0
            self._persist(text, reply)
            return reply, score

        lang = detect_lang(text) or "ro"
        if lang == "en":
            intent, score = self.index_en.match(text)
        else:
            intent, score = self.index.match(text)
        if intent is not None and score >= self.config.min_similarity:
            reply = intent.response
        else:
            reply = self._fallback(text, lang)

        self._persist(text, reply)
        return reply, score

    def _fallback(self, text: str, lang: str) -> str:
        """RO: Traseu de fallback: capabilities -> learned -> FAQ -> queue.
        EN: Fallback path: capabilities -> learned -> FAQ -> queue.
        """
        text_l = text.lower()
        if any(k in text_l for k in ["ajutor", "help", "ce stii", "capabilitati", "ce poti", "help me"]):
            return self._capabilities()
        learned = self._learned_match(text)
        if learned:
            return learned
        faq_reply = self.faq_en.match(text) if lang == "en" else self.faq.match(text)
        if faq_reply:
            return faq_reply
        enqueue_learning(self.memory_db, text, datetime.now(timezone.utc).isoformat())
        return "Nu sunt sigur. Poti reformula?"

    def _capabilities(self) -> str:
        """RO: Explica pe scurt ce intenturi sunt disponibile.
        EN: Short overview of available intents.
        """
        names = [intent.name for intent in self.index.intents]
        examples = [intent.examples[0] for intent in self.index.intents if intent.examples]
        return (
            "Pot raspunde la intenturi: "
            + ", ".join(names)
            + ". Incearca: "
            + "; ".join(examples)
        )

    def _persist(self, text: str, reply: str) -> None:
        """RO: Pastreaza dialogul in SQLite cu timestamp UTC.
        EN: Persist the dialog to SQLite with UTC timestamps.
        """
        now = datetime.now(timezone.utc).isoformat()
        save_message(self.memory_db, "user", text, now)
        save_message(self.memory_db, "assistant", reply, now)

    def _learned_match(self, text: str) -> str | None:
        """RO: Cauta raspunsuri invatate manual (human-in-the-loop).
        EN: Try answers learned by a human in the loop.
        """
        entries = [LearnedEntry(q, r) for q, r in list_learned_faq(self.memory_db)]
        return LearnedIndex(entries).match(text)

    def _check_policy(self, text: str) -> str | None:
        """RO: Aplica reguli simple allow/deny pe tokeni.
        EN: Apply simple allow/deny keyword rules.
        """
        tokens = tokenize(text)
        for keyword, action in list_policy_rules(self.memory_db):
            if keyword.lower() in tokens:
                return action
        return None

    def add_policy_keyword(self, keyword: str, action: str) -> None:
        """RO: Adauga o regula de politica (deny/allow) in DB.
        EN: Store a policy rule (deny/allow) in the database.
        """
        add_policy_rule(self.memory_db, keyword, action)
