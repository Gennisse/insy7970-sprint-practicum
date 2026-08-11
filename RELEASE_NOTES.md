# Weeknight Recipe Scout 1.0.0

Weeknight Recipe Scout 1.0.0 is the portfolio-ready release for busy home cooks who want practical recipe comparisons within time and calorie limits.

## Highlights

- Fetches real Recipe API data and preserves raw and processed evidence.
- Validates provider data before ranking or saving trusted results.
- Ranks only recipes with complete prep-time and calorie measurements.
- Presents comparisons in an interactive Streamlit dashboard and a reproducible Quarto PDF.
- Adds SQLite recommendation history shared by the CLI and dashboard.
- Installs the `weeknight-recipe-scout` command from a standard wheel.
- Runs formatting, lint, tests, and package builds through one local script and GitHub Actions.

## Verification

- 9 fixture-backed tests pass without a live API call.
- Ruff formatting and lint checks pass.
- `uv build --no-sources` creates both standard distributions.
- The wheel installs and its console command runs in an isolated virtual environment.
- The Quarto PDF renders with the Python interpreter restored by `uv sync` and passes visual inspection.

## Known limitations

- Live searches require a Recipe API key and network access.
- Recommendation quality is limited to the provider's returned page and available measurements.
- SQLite history is local to one installation and does not yet perform schema migrations.
