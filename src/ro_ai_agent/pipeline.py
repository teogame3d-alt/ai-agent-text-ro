from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


WORD_RE = re.compile(r"[a-zA-Z0-9_]+", re.ASCII)


@dataclass(frozen=True)
class Intent:
    name: str
    examples: list[str]
    response: str


class IntentIndex:
    def __init__(self, intents: Iterable[Intent]):
        self.intents = list(intents)
        self.vocab = self._build_vocab(self.intents)
        self.matrix = self._vectorize_examples(self.intents)

    def _build_vocab(self, intents: list[Intent]) -> dict[str, int]:
        vocab = {}
        for intent in intents:
            for ex in intent.examples:
                for token in WORD_RE.findall(ex.lower()):
                    if token not in vocab:
                        vocab[token] = len(vocab)
        return vocab

    def _vectorize(self, text: str) -> np.ndarray:
        vec = np.zeros(len(self.vocab), dtype=float)
        for token in WORD_RE.findall(text.lower()):
            if token in self.vocab:
                vec[self.vocab[token]] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def _vectorize_examples(self, intents: list[Intent]) -> np.ndarray:
        rows = []
        for intent in intents:
            for ex in intent.examples:
                rows.append(self._vectorize(ex))
        return np.vstack(rows) if rows else np.zeros((0, len(self.vocab)))

    def match(self, text: str) -> tuple[Intent | None, float]:
        if not self.intents:
            return None, 0.0
        vec = self._vectorize(text)
        if vec.sum() == 0:
            return None, 0.0
        scores = self.matrix @ vec
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        intent_idx = 0
        for intent in self.intents:
            for _ in intent.examples:
                if intent_idx == best_idx:
                    return intent, best_score
                intent_idx += 1
        return None, best_score


def load_intents(path: Path) -> list[Intent]:
    data = json.loads(path.read_text(encoding="utf-8"))
    intents = []
    for name, payload in data.items():
        intents.append(Intent(name, payload["examples"], payload["response"]))
    return intents
