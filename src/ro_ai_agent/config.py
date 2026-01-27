from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class AgentConfig:
    min_similarity: float = 0.35
    enable_voice: bool = False


def load_config(path: Path) -> AgentConfig:
    if not path.exists():
        return AgentConfig()
    data = json.loads(path.read_text(encoding="utf-8"))
    return AgentConfig(
        min_similarity=float(data.get("min_similarity", 0.35)),
        enable_voice=bool(data.get("enable_voice", False)),
    )
