# Final Course Project Reflection

Release: https://github.com/Gennisse/insy7970-sprint-practicum/releases/tag/v1.0.0

## What I taught myself beyond the floor

I taught myself how to use SQLite as durable application state rather than treating every API search as a disposable event. It fit Weeknight Recipe Scout because a busy cook benefits from seeing recent searches, constraints, and top recommendations across sessions. I designed a small schema, used parameterized statements and transactions, connected each history row to its processed JSON evidence, and integrated the same persistence behavior into the CLI and dashboard.

## How I learned it

I worked from Python's `sqlite3` documentation, used Codex to help translate the user need into a focused schema and test plan, and reviewed the implementation through isolated tests and the rendered dashboard flow. I also used the course's established pattern: keep shared behavior outside the interface, verify it without a live API, document the data contract, and inspect the complete package before release.

## Hardest, most surprising, and next

The hardest part was discovering how many environments a “reproducible” project actually crosses: the local `uv` environment, Quarto's Jupyter interpreter, GitHub Actions, and an isolated wheel installation. The most surprising issue was Quarto selecting a Python kernel outside the restored environment even when the report command was launched through `uv`. Fixing that required an explicit wrapper that pins `QUARTO_PYTHON`. Next, I would learn scheduled collection and schema migrations so history could grow safely over time and support comparisons across a larger, genuinely longitudinal dataset.

## Constructive course feedback

The repeated cycle of specification, implementation, evidence, documentation, and release worked well because each lecture improved the same project instead of creating disconnected exercises. The public pull-request practicum was especially useful because it made reviewability concrete. The most difficult part was that a few requirements changed late, especially the shift from PyPI publishing to GitHub Release assets. I would publish the final packaging and release contract earlier and provide one small clean-room installation example so students can test the exact handoff path before the last week.
