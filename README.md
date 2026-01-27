# AI Agent Text RO

A Romanian text agent with a deterministic pipeline, config-driven behavior,
persistence, and tests. This is not an LLM; it is a clean, explainable system
suitable for product and QA workflows.

![Flow](docs/images/agent_flow.png)

## Features
- Romanian intent matching (bag-of-words + cosine similarity)
- Config and data-driven responses
- SQLite memory (conversation history)
- FAQ fallback for unknown intents
- Learning queue (human-in-the-loop)
- Policy allow/deny rules (safe responses)
- Optional TTS (Google gTTS online + pyttsx3 offline fallback)
- Unit tests for intent matching and memory

## Quick Start
```bash
python -m venv .venv
.venv\Scripts\python -m pip install -U pip
.venv\Scripts\python -m pip install -e .[dev]
.venv\Scripts\python -m ro_ai_agent
```

## UI (PyQt6)
```bash
.venv\Scripts\python -m ro_ai_agent.ui_app
```

## Optional Voice
```bash
.venv\Scripts\python -m pip install -e .[voice]
```
Then in config, set `enable_voice = true`.

## Config
`data/config.json` controls thresholds and voice behavior.

## FAQ
`data/faq_ro.json` adds keyword-based fallback answers when no intent matches.

## Learning & Policy
- Unknown questions are saved to a learning queue in SQLite.
- You can approve answers in the UI (Teach tab) and the agent learns them.
- You can add deny keywords to block specific topics.

## Tests
```bash
.venv\Scripts\python -m pytest
```

## Design Decisions
See `docs/DECISIONS.md`.

## Hiring Checklist
- Deterministic, explainable pipeline
- Config-driven behavior
- Persistent memory (SQLite)
- Tests for matching + storage
