from __future__ import annotations

"""RO: Index minimal pentru FAQ, bazat pe tokeni si cuvinte-cheie.
EN: Minimal FAQ index based on token matching and keywords.
"""

from dataclasses import dataclass
from pathlib import Path
import json
import re


WORD_RE = re.compile(r"[a-zA-Z0-9_]+", re.ASCII)


def tokenize(text: str) -> set[str]:
    """RO: Tokenizare simpla, fara dependinte NLP grele.
    EN: Lightweight tokenization without heavy NLP deps.
    """
    return {t.lower() for t in WORD_RE.findall(text)}


@dataclass(frozen=True)
class FaqEntry:
    """RO: Un entry FAQ cu keywords si raspuns.
    EN: One FAQ entry with keywords and a response.
    """
    keywords: list[str]
    response: str


class FaqIndex:
    """RO: Cauta raspunsul FAQ pe baza de cuvinte-cheie.
    EN: Finds FAQ answers using keyword presence.
    """
    def __init__(self, entries: list[FaqEntry]) -> None:
        self.entries = entries

    def match(self, text: str) -> str | None:
        """RO: Returneaza primul raspuns care are un keyword in text.
        EN: Return the first response whose keyword appears in text.
        """
        tokens = tokenize(text)
        for entry in self.entries:
            if any(k.lower() in tokens for k in entry.keywords):
                return entry.response
        return None


def load_faq(path: Path) -> FaqIndex:
    """RO: Incarca FAQ din JSON; daca lipseste, index gol.
    EN: Load FAQ from JSON; return empty index if missing.
    """
    if not path.exists():
        return FaqIndex([])
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = [FaqEntry(d["keywords"], d["response"]) for d in data]
    return FaqIndex(entries)
