from pathlib import Path

from ro_ai_agent.pipeline import IntentIndex, load_intents


def test_match_intent(tmp_path: Path) -> None:
    data = {
        "greet": {"examples": ["salut"], "response": "ok"},
        "hours": {"examples": ["program"], "response": "ok"},
    }
    p = tmp_path / "intents.json"
    p.write_text(__import__("json").dumps(data), encoding="utf-8")
    intents = load_intents(p)
    index = IntentIndex(intents)
    intent, score = index.match("salut")
    assert intent is not None
    assert intent.name == "greet"
    assert score > 0.0
