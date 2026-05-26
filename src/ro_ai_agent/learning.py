from __future__ import annotations

"""RO: Matching simplu pentru raspunsuri invatate manual.
EN: Simple matching for human-learned answers.
"""

from dataclasses import dataclass
from typing import Iterable

from .faq import tokenize


@dataclass(frozen=True)
class LearnedEntry:
    """RO: Intrebare + raspuns invatat.
    EN: Learned question/answer pair.
    """
    question: str
    response: str


class LearnedIndex:
    """RO: Index bazat pe suprapunerea de tokeni.
    EN: Index based on token overlap.
    """
    def __init__(self, entries: Iterable[LearnedEntry]) -> None:
        self.entries = list(entries)

    def match(self, text: str) -> str | None:
        """RO: Alege raspunsul cu cea mai mare intersectie de tokeni.
        EN: Pick the response with the highest token overlap.
        """
        if not self.entries:
            return None
        tokens = tokenize(text)
        best_score = 0
        best_response = None
        for entry in self.entries:
            q_tokens = tokenize(entry.question)
            overlap = len(tokens & q_tokens)
            if overlap > best_score:
                best_score = overlap
                best_response = entry.response
        if best_score > 0:
            return best_response
        return None
