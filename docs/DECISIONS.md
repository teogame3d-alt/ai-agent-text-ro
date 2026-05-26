# Design Decisions

- The project is an AI Agent concept: it can accept user questions, store unknown items for review, learn approved answers, and follow explicit behavior rules.
- The current MVP uses deterministic matching so the learning path remains explainable and testable.
- Intent matching uses lightweight vectorization (no heavy ML dependencies).
- Memory is SQLite to ensure persistence and easy portability.
- User-approved answers are stored separately from built-in intents, which makes learned behavior auditable.
- Optional voice support is isolated in `tts.py`.
