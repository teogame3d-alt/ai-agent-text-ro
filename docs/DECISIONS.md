# Design Decisions

- The agent is deterministic and explainable. It avoids LLM opacity.
- Intent matching uses lightweight vectorization (no heavy ML dependencies).
- Memory is SQLite to ensure persistence and easy portability.
- Optional voice support is isolated in `tts.py`.
