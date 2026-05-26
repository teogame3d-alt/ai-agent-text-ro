from __future__ import annotations

"""RO: Pipeline determinist pentru matching intent-uri (BoW + cosine).
EN: Deterministic intent matching pipeline (BoW + cosine similarity).
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


WORD_RE = re.compile(r"[a-zA-Z0-9_]+", re.ASCII)


@dataclass(frozen=True)
class Intent:
    """RO: Defineste un intent: nume, exemple, raspuns.
    EN: Intent definition: name, examples, response.
    """
    name: str
    examples: list[str]
    response: str


class IntentIndex:
    """RO: Vectorizeaza exemplele si face potrivirea cu textul.
    EN: Vectorizes examples and matches input text.
    """
    def __init__(self, intents: Iterable[Intent]):
        self.intents = list(intents)
        self.vocab = self._build_vocab(self.intents)
        self.idf = self._build_idf(self.intents)
        self.matrix = self._vectorize_examples(self.intents)

    def _build_vocab(self, intents: list[Intent]) -> dict[str, int]:
        """RO: Construieste vocabularul din exemple.
        EN: Build a token vocabulary from examples.
        """
        vocab = {}
        for intent in intents:
            for ex in intent.examples:
                for token in WORD_RE.findall(ex.lower()):
                    if token not in vocab:
                        vocab[token] = len(vocab)
        return vocab

    def _vectorize(self, text: str) -> np.ndarray:
        """RO: Transforma textul intr-un vector normalizat.
        EN: Turn text into a normalized vector.
        """
        vec = np.zeros(len(self.vocab), dtype=float)
        for token in WORD_RE.findall(text.lower()):
            if token in self.vocab:
                vec[self.vocab[token]] += 1.0
        if self.idf.size:
            vec = vec * self.idf
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def _vectorize_examples(self, intents: list[Intent]) -> np.ndarray:
        """RO: Vectorizeaza toate exemplele pentru matching rapid.
        EN: Vectorize all examples for fast matching.
        """
        rows = []
        for intent in intents:
            for ex in intent.examples:
                rows.append(self._vectorize(ex))
        return np.vstack(rows) if rows else np.zeros((0, len(self.vocab)))

    def _build_idf(self, intents: list[Intent]) -> np.ndarray:
        """RO: Calculeaza IDF pentru vocabular, pe baza exemplarelor.
        EN: Compute IDF over the examples corpus.
        """
        if not self.vocab:
            return np.zeros(0, dtype=float)
        docs = []
        for intent in intents:
            for ex in intent.examples:
                docs.append(set(WORD_RE.findall(ex.lower())))
        if not docs:
            return np.ones(len(self.vocab), dtype=float)
        df = np.zeros(len(self.vocab), dtype=float)
        for d in docs:
            for token in d:
                idx = self.vocab.get(token)
                if idx is not None:
                    df[idx] += 1.0
        n_docs = float(len(docs))
        idf = np.log((1.0 + n_docs) / (1.0 + df)) + 1.0
        return idf

    def match(self, text: str) -> tuple[Intent | None, float]:
        """RO: Gaseste intentul cel mai apropiat si scorul.
        EN: Find the closest intent and its score.
        """
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
    """RO: Incarca intenturile din JSON.
    EN: Load intents from JSON.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    intents = []
    for name, payload in data.items():
        intents.append(Intent(name, payload["examples"], payload["response"]))
    return intents
