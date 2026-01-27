from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


WORD_RE = re.compile(r"[a-zA-Z0-9_]+", re.ASCII)


@dataclass(frozen=True)
class FaqEntry:
    keywords: list[str]
    response: str


class FaqIndex:
    def __init__(self, entries: list[FaqEntry]) -> None:
        self.entries = entries

    def match(self, text: str) -> str | None:
        tokens = {t.lower() for t in WORD_RE.findall(text)}
        for entry in self.entries:
            if any(k.lower() in tokens for k in entry.keywords):
                return entry.response
        return None


def load_faq(path: Path) -> FaqIndex:
    if not path.exists():
        return FaqIndex([])
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = [FaqEntry(d["keywords"], d["response"]) for d in data]
    return FaqIndex(entries)
