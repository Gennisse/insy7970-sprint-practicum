# AGENTS.md

## Purpose

Weeknight Recipe Scout fetches Recipe API results and recommends practical options for busy home cooks using prep-time and calorie limits.

## Setup and checks

- Restore the exact Python environment with `uv sync`.
- Run all tests with `uv run pytest`.
- Inspect CLI behavior with `uv run main.py --help`.
- Start the dashboard with `uv run streamlit run streamlit_app.py`.
- Rebuild the report with `uv run python scripts/render_report.py` after Quarto and TinyTeX are installed. The wrapper pins Quarto to the active `uv` interpreter.
- Tests and the report must run without a live API key or network request.

## Navigation

- `main.py`: provider models, fetching, normalization, recommendations, persistence, CLI, and reusable report logic.
- `streamlit_app.py`: user-facing interactive dashboard; keep business rules in `main.py`.
- `tests/`: behavioral tests and provider-shaped fixture.
- `docs/data-dictionary.md`: stable processed-output contract.
- `reports/weeknight-recipe-report.qmd`: authoritative report source; its PDF is generated and committed.
- `data/raw/` and `data/processed/`: live run artifacts; commit only deliberate, secret-free evidence needed for grading or reports.

## Conventions and sources of truth

- Python 3.11+, type hints on every function, concise module/class/function docstrings.
- `main.py` is the source of truth for validation, normalization, filtering, and ranking. The dashboard and report call it instead of reimplementing rules.
- Tests define expected behavior. Update tests, CLI help, dashboard copy, README, and data dictionary when behavior changes.
- The `.qmd` is the report source. Never edit the PDF by hand; revise source, code, or input and render again.
- Preserve raw API text before transformation. Never write the bearer token to source, data, logs, report metadata, or errors.
- Keep changes focused and inspect the complete diff before committing.
