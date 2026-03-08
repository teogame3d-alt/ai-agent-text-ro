# Mentor Notes

## Why this project exists
I wanted to show an explainable alternative to black-box chat systems: deterministic intent matching with clear fallback rules.

## Technical decisions
- Chose TF-IDF/cosine style intent matching for transparency and reproducibility.
- Added SQLite memory and learning queue to model practical product behavior.
- Kept policy checks explicit (`allow/deny`) for safe-response control.

## Build vs polish
- Build phase: engine, memory, pipeline, UI, tests, CI.
- Polish phase: screenshot updates, README restructuring, recruiter-focused flow.

## What I learned
- Explainability matters in QA and product contexts.
- Configuration-driven systems are easier to tune and maintain.
