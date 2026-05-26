# Engineering Notes

## Why this project exists
I wanted to show a personal AI Agent that can learn from the user while staying understandable: unknown questions go into a learning queue, approved answers become reusable knowledge, and policy rules shape behavior.

## Technical decisions
- Chose TF-IDF/cosine style intent matching for transparency and reproducibility.
- Added SQLite memory and learning queue to model practical product behavior.
- Kept policy checks explicit (`allow/deny`) for safe-response control.
- Kept learned answers visible and testable instead of hiding behavior in an external service.

## Build vs polish
- Build phase: engine, memory, pipeline, UI, tests, CI.
- Polish phase: screenshot updates, README restructuring, and a clearer review path.

## What I learned
- Agent behavior needs both learning and boundaries.
- Explainability matters when a system adapts to user input.
- Configuration-driven systems are easier to tune and maintain.
