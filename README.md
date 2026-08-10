# Weeknight Recipe Scout

Weeknight Recipe Scout helps busy home cooks compare Recipe API results against two practical constraints: available prep time and a calorie ceiling. It saves the original response for provenance, validates the provider schema, creates a stable processed summary, and ranks only recipes with complete measurements that meet both limits.

## Fastest path to a result

1. Install [uv](https://docs.astral.sh/uv/) and Python 3.11 or newer.
2. Run `uv sync`.
3. Copy `.env.example` to `.env` and replace the placeholder value for `RECIPE_API_KEY` with your own Recipe API key.
4. Run:

   ```powershell
   uv run main.py --search chicken --max-prep 30 --max-calories 650
   ```

The command prints the top qualifying recipe and writes a timestamped raw response under `data/raw/` plus a processed comparison under `data/processed/`.

## Dashboard

Start the interactive comparison:

```powershell
uv run streamlit run streamlit_app.py
```

Set the meal idea, desired ingredients, maximum prep time, and maximum calories in the sidebar. The table ranks qualifying recipes by shortest prep time and then lowest calories. Recipes missing either measurement stay in the saved results but are not recommended.

## Configuration

| Environment variable | Purpose | Default |
|---|---|---|
| `RECIPE_API_KEY` | Recipe API bearer token; required for live requests | none |
| `RECIPE_SEARCH` | Search term | `chicken` |
| `RECIPE_INGREDIENTS` | Comma-separated provider ingredient filter | empty |
| `RECIPE_PAGE` | Positive result page | `1` |
| `RECIPE_PER_PAGE` | Results per page, 1–50 | `10` |
| `MAX_PREP_MINUTES` | Recommendation prep-time ceiling | `30` |
| `MAX_CALORIES` | Recommendation calorie ceiling | `650` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` | `INFO` |
| `LOG_FILE` | File-log path; an empty value disables it | `logs/weeknight-recipe-scout.log` |

CLI flags override these defaults for the current run. See every option with `uv run main.py --help`. Never commit `.env` or a real API key.

## Tests

```powershell
uv run pytest
```

Tests use the committed provider-shaped fixture and never contact Recipe API.

## Reproducible report

The authoritative source is [`reports/weeknight-recipe-report.qmd`](reports/weeknight-recipe-report.qmd), and the inspected output is [`reports/weeknight-recipe-report.pdf`](reports/weeknight-recipe-report.pdf). After `uv sync`, install [Quarto](https://quarto.org/docs/get-started/) and TinyTeX once, then rebuild with:

```powershell
uv run quarto render reports/weeknight-recipe-report.qmd --to pdf
```

The report uses the committed fixture at `tests/fixtures/recipe_response_success.json`, calls the same validation and recommendation functions as the application, and requires no API key.

## Inputs and outputs

- Input: Recipe API JSON from `GET /api/v1/recipes`, filtered by search, ingredients, page, and page size.
- Raw output: exact provider response at `data/raw/<search>-page<page>-<UTC timestamp>.raw.json`.
- Processed output: normalized recipes, limits, counts, and ranked matches at `data/processed/<search>-page<page>-<UTC timestamp>.processed.json`.
- Runtime evidence: terminal messages and an optional file under `logs/`.

The [data dictionary](docs/data-dictionary.md) defines every stable processed field, provenance, units, missing-value rules, and transformations.

## Common failures

- `RECIPE_API_KEY is missing`: create `.env` from `.env.example` and add your key.
- HTTP 401 or 403: confirm the key is current and authorized; do not paste it into an issue or log.
- API could not be reached: check the network and provider status, then retry.
- Unexpected data: the provider response no longer matches the validated schema; retain the error and inspect the raw provider behavior before changing models.
- No qualifying recipes: broaden the search or increase a limit. Missing prep time or calories intentionally prevents a recommendation.
- PDF render fails: run `quarto check`; confirm Quarto, TinyTeX, and the `uv` environment are installed.

## Project guide

- [`docs/data-dictionary.md`](docs/data-dictionary.md): processed JSON contract.
- [`reports/weeknight-recipe-report.qmd`](reports/weeknight-recipe-report.qmd): authoritative report source.
- [`AGENTS.md`](AGENTS.md): durable setup, navigation, and source-of-truth guidance.
- [`LICENSE`](LICENSE): MIT license.
- [`docs/specs/`](docs/specs/): historical sprint specifications; current behavior is defined by code, tests, help, and this README.

Recipe data comes from [Recipe API](https://recipeapi.io/docs/). Provider terms and data quality remain the provider's responsibility.
