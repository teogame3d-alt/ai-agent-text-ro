from __future__ import annotations

"""RO: Configuratie simpla pentru praguri si optiuni runtime.
EN: Small config for thresholds and runtime options.
"""

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class AgentConfig:
    """RO: Setari esentiale pentru agent.
    EN: Essential agent settings.
    """
    min_similarity: float = 0.35
    enable_voice: bool = False


def load_config(path: Path) -> AgentConfig:
    """RO: Incarca config din JSON, cu valori default.
    EN: Load config from JSON with defaults.
    """
    if not path.exists():
        return AgentConfig()
    data = json.loads(path.read_text(encoding="utf-8"))
    return AgentConfig(
        min_similarity=float(data.get("min_similarity", 0.35)),
        enable_voice=bool(data.get("enable_voice", False)),
    )
