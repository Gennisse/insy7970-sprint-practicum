# Weeknight Recipe Scout 1.1.0

Weeknight Recipe Scout 1.1.0 is the final portfolio release for busy home cooks who want practical, explainable recipe comparisons.

## Highlights

- Preserves six real Recipe API responses and validated processed evidence.
- Provides a reproducible 54-recipe offline snapshot without requiring an API key.
- Filters by food choice, required ingredients, dietary tags, preparation time, and calories.
- Compares cook time, total time, protein, servings, cuisine, difficulty, and instruction count.
- Shows ingredients and complete provider instructions for the selected recipe.
- Persists recent recommendation decisions in SQLite.
- Includes a protein-focused Quarto report with a table, figure, interpretation, and provenance.
- Runs formatting, lint, 12 offline tests, and package builds locally and in GitHub Actions.

## Verification

- `uv sync --locked`
- `uv run pytest`
- `uv run streamlit run streamlit_app.py`
- `uv run python scripts/render_report.py`
- `uv build --no-sources`

## Known limitations

- Live searches require a Recipe API key and network access.
- The saved snapshot contains the first page of six searches retrieved on August 13, 2026.
- Provider nutrition and dietary tags are informational and are not medical advice.
- SQLite history is local to one installation and does not yet perform schema migrations.
