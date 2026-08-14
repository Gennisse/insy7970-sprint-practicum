# Weeknight Recipe Scout

Weeknight Recipe Scout helps busy home cooks compare Recipe API results against practical constraints: available prep time, a calorie ceiling, ingredient preferences, and dietary needs. It saves the original response for provenance, validates the provider schema, creates a stable processed summary, and ranks only recipes with complete measurements that meet both limits. The dashboard also compares cook and total time, protein per serving, servings, cuisine, difficulty, dietary tags, ingredients, and provider instructions.

## Fastest path to a result

1. Install [uv](https://docs.astral.sh/uv/) and Python 3.11 or newer.
2. Run `uv sync --locked`.
3. Copy `.env.example` to `.env` and replace the placeholder value for `RECIPE_API_KEY` with your own Recipe API key.
4. Run:

   ```powershell
   uv run weeknight-recipe-scout --search chicken --max-prep 30 --max-calories 650
   ```

The command prints the top qualifying recipe, writes a timestamped raw response under `data/raw/`, writes a processed comparison under `data/processed/`, and records the decision in `data/weeknight-recipe-scout.sqlite3`.

## Dashboard

Start the interactive comparison:

```powershell
uv run streamlit run streamlit_app.py
```

Set the meal idea, desired ingredients, maximum prep time, and maximum calories in the sidebar. The table ranks qualifying recipes by shortest prep time and then lowest calories. Recipes missing either measurement stay in the saved results but are not recommended.

The dashboard also shows the five most recent searches and top picks from SQLite, giving a busy cook a useful memory across sessions. Select **Load saved API snapshot** to explore 54 recipes retrieved from Recipe API on August 13, 2026, without an API key or network request. The committed CSV records its source search and retrieval timestamp, and the matching raw and processed responses are preserved under `data/raw/` and `data/processed/`. Select **Search live Recipe API** when a key is configured. Recipe selections and details persist during the current browser session.

Rebuild the saved snapshot from the six committed processed files with:

```powershell
uv run python scripts/build_sample_snapshot.py data/processed/chicken-page1-20260813T061831Z.processed.json data/processed/salmon-page1-20260813T061832Z.processed.json data/processed/vegetarian-page1-20260813T061832Z.processed.json data/processed/pasta-page1-20260813T061833Z.processed.json data/processed/turkey-page1-20260813T061833Z.processed.json data/processed/beef-page1-20260813T061834Z.processed.json --output data/sample/weeknight-recipes.csv
```

## Configuration

| Environment variable | Purpose | Default |
|---|---|---|
| `RECIPE_API_KEY` | Recipe API bearer token; required for live requests | none |
| `RECIPE_SEARCH` | Search term | `chicken` |
| `RECIPE_INGREDIENTS` | Comma-separated provider ingredient filter | empty |
| `RECIPE_PAGE` | Positive result page | `1` |
| `RECIPE_PER_PAGE` | Results per page, 1-50 | `10` |
| `MAX_PREP_MINUTES` | Recommendation prep-time ceiling | `30` |
| `MAX_CALORIES` | Recommendation calorie ceiling | `650` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` | `INFO` |
| `LOG_FILE` | File-log path; an empty value disables it | `logs/weeknight-recipe-scout.log` |
| `RECIPE_HISTORY_DB` | SQLite file used for recommendation history | `data/weeknight-recipe-scout.sqlite3` |

CLI flags override these defaults for the current run. See every option with `uv run weeknight-recipe-scout --help`. Use `--no-history` for an unrecorded request or `--show-history` to inspect saved picks without calling the API. Never commit `.env` or a real API key.

## Tests

```powershell
uv run pytest
```

Tests use the committed provider-shaped fixture and never contact Recipe API.

Run the complete local release check in Git Bash or another Bash terminal:

```bash
bash scripts/check.sh
```

On Windows PowerShell, run the equivalent contract:

```powershell
.\scripts\check.ps1
```

GitHub Actions runs the same formatting, lint, test, and build contract after every push and pull request.

## Build and install the package

Build the exact version declared in `pyproject.toml`:

```powershell
uv build --no-sources
```

This creates a wheel and source archive under `dist/`. Install the wheel as a command-line tool:

```powershell
uv tool install dist/weeknight_recipe_scout-1.1.0-py3-none-any.whl
weeknight-recipe-scout --help
```

The submitted wheel and source archive are attached to the versioned GitHub Release linked from the final reflection.

## Reproducible report

The authoritative source is [`reports/weeknight-recipe-report.qmd`](reports/weeknight-recipe-report.qmd), and the inspected output is [`reports/weeknight-recipe-report.pdf`](reports/weeknight-recipe-report.pdf). After `uv sync`, install [Quarto](https://quarto.org/docs/get-started/) and TinyTeX once, then rebuild with:

```powershell
uv run python scripts/render_report.py
```

The wrapper sets Quarto's `QUARTO_PYTHON` to the interpreter restored by `uv sync`, preventing Quarto from selecting an unrelated system Jupyter kernel. The report uses the committed 54-recipe API snapshot, calls the same loading and recommendation functions as the dashboard, and requires no API key or network request. It compares protein per serving while enforcing preparation-time, total-time, and calorie limits. If Quarto is not on `PATH`, set `QUARTO_BIN` to its executable path before running the wrapper.

## Inputs and outputs

- Input: Recipe API JSON from `GET /api/v1/recipes`, filtered by search, ingredients, page, and page size.
- Raw output: exact provider response at `data/raw/<search>-page<page>-<UTC timestamp>.raw.json`.
- Processed output: normalized recipes, limits, counts, and ranked matches at `data/processed/<search>-page<page>-<UTC timestamp>.processed.json`.
- History output: one SQLite row per recorded decision, including limits, counts, top pick, and processed-file provenance.
- Runtime evidence: terminal messages and an optional file under `logs/`.

The [data dictionary](docs/data-dictionary.md) defines every stable processed field, provenance, units, missing-value rules, and transformations.

## Common failures

- `RECIPE_API_KEY is missing`: create `.env` from `.env.example` and add your key.
- HTTP 401 or 403: confirm the key is current and authorized; do not paste it into an issue or log.
- API could not be reached: check the network and provider status, then retry.
- Unexpected data: the provider response no longer matches the validated schema; retain the error and inspect the raw provider behavior before changing models.
- No qualifying recipes: broaden the search or increase a limit. Missing prep time or calories intentionally prevents a recommendation.
- PDF render fails: run `quarto check`; confirm Quarto, TinyTeX, and the `uv` environment are installed.
- SQLite write fails: confirm the parent directory is writable or pass `--database` with another local path.

## Project guide

- [`docs/data-dictionary.md`](docs/data-dictionary.md): processed JSON contract.
- [`history.py`](history.py): SQLite persistence and recent-run queries.
- [`reports/weeknight-recipe-report.qmd`](reports/weeknight-recipe-report.qmd): authoritative report source.
- [`AGENTS.md`](AGENTS.md): durable setup, navigation, and source-of-truth guidance.
- [`LICENSE`](LICENSE): MIT license.

Recipe data comes from [Recipe API](https://recipeapi.io/docs/). Provider terms and data quality remain the provider's responsibility.
