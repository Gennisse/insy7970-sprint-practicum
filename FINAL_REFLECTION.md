# Final Course Project Reflection

Release: https://github.com/Gennisse/insy7970-sprint-practicum/releases/tag/v1.1.0

## What I taught myself beyond the floor

I taught myself how to use SQLite as durable application state rather than treating every API search as a disposable event. It fit Weeknight Recipe Scout because a busy cook benefits from seeing recent searches, constraints, and top recommendations across sessions. I designed a small schema, used parameterized statements and transactions, connected each history row to its processed JSON evidence, and integrated the same persistence behavior into the CLI and dashboard.

I also deepened the data pipeline by preserving real Recipe API responses and creating a reproducible offline snapshot. The dashboard now compares preparation time, cooking time, total time, calories, protein, servings, dietary tags, ingredients, and provider instructions without requiring a grader to supply an API key.

## How I learned it

I worked from Python's `sqlite3` documentation and the Recipe API documentation, used Codex to translate user needs into a focused schema and test plan, and reviewed the implementation through isolated tests, live API evidence, the rendered dashboard, and the Quarto PDF. I followed the course pattern of keeping shared behavior outside the interface, validating provider data, documenting the data contract, and inspecting the complete package before release.

## Hardest, most surprising, and next

The hardest part was discovering how many environments a reproducible project crosses: the local `uv` environment, Quarto's Jupyter interpreter, GitHub Actions, and an isolated wheel installation. The most surprising issues were Quarto selecting a Python kernel outside the restored environment and the live API using different field names than the original fixture. Fixing them required an explicit report wrapper and validated aliases for preparation time and calories per serving. Next, I would learn scheduled collection and database schema migrations so the history could grow safely into a longitudinal comparison dataset.

## Constructive course feedback

The repeated cycle of specification, implementation, evidence, documentation, and release worked well because each lecture improved the same project instead of creating disconnected exercises. The public pull-request practicum was especially useful because it made reviewability concrete. The most difficult part was that a few requirements changed late, especially the shift from PyPI publishing to GitHub Release assets. I would publish the final packaging contract earlier and provide one clean-room installation example so students can test the exact handoff path before the final week.
