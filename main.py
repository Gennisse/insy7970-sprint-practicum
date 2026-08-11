"""Fetch, validate, analyze, and save recipe data for busy weeknight cooks."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from history import list_recent_runs, record_run

BASE_URL = "https://recipeapi.io/api/v1/recipes"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
LOGGER_NAME = "weeknight_recipe_scout"


class RecipeItem(BaseModel):
    """A recipe returned by Recipe API; unrecognized provider fields are retained."""

    model_config = ConfigDict(extra="allow")
    id: int | str | None = None
    name: str | None = None
    description: str | None = None
    cuisine: str | None = None
    difficulty: str | None = None
    meal_type: str | None = None
    prep_time_minutes: int | None = None
    calories: int | None = None
    ingredients: list[Any] = Field(default_factory=list)
    instructions: list[Any] = Field(default_factory=list)


class RecipeLinks(BaseModel):
    """Pagination links supplied by Recipe API."""

    model_config = ConfigDict(extra="allow")
    first: str | None = None
    last: str | None = None
    prev: str | None = None
    next: str | None = None


class RecipeMeta(BaseModel):
    """Pagination and language metadata supplied by Recipe API."""

    model_config = ConfigDict(extra="allow")
    current_page: int | None = None
    last_page: int | None = None
    per_page: int | None = None
    total: int | None = None
    path: str | None = None
    language: str | None = None


class RecipeResponse(BaseModel):
    """Validated top-level Recipe API response."""

    model_config = ConfigDict(extra="allow")
    data: list[RecipeItem]
    links: RecipeLinks
    meta: RecipeMeta


def load_dotenv_file(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE pairs without overwriting existing environment values."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI options, using environment variables as defaults."""
    parser = argparse.ArgumentParser(
        description="Find and save recipes, then rank practical weeknight options.",
        epilog="Example: uv run weeknight-recipe-scout --search chicken --max-prep 30 --max-calories 650",
    )
    parser.add_argument(
        "--search",
        default=os.getenv("RECIPE_SEARCH", "chicken"),
        help="Recipe search term (default: chicken)",
    )
    parser.add_argument(
        "--ingredients",
        default=os.getenv("RECIPE_INGREDIENTS", ""),
        help="Comma-separated required ingredients",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=int(os.getenv("RECIPE_PAGE", "1")),
        help="Positive result page (default: 1)",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=int(os.getenv("RECIPE_PER_PAGE", "10")),
        help="Recipes requested, 1-50 (default: 10)",
    )
    parser.add_argument(
        "--max-prep",
        type=int,
        default=int(os.getenv("MAX_PREP_MINUTES", "30")),
        help="Maximum prep minutes for recommendations (default: 30)",
    )
    parser.add_argument(
        "--max-calories",
        type=int,
        default=int(os.getenv("MAX_CALORIES", "650")),
        help="Maximum calories for recommendations (default: 650)",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("RECIPE_API_KEY", ""),
        help="Recipe API key; prefer RECIPE_API_KEY in .env",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging threshold (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default=os.getenv("LOG_FILE", "logs/weeknight-recipe-scout.log"),
        help="Log destination; pass an empty value to disable",
    )
    parser.add_argument(
        "--database",
        default=os.getenv("RECIPE_HISTORY_DB", "data/weeknight-recipe-scout.sqlite3"),
        help="SQLite run-history path",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Do not save this run to SQLite history",
    )
    parser.add_argument(
        "--show-history",
        action="store_true",
        help="Print recent saved recommendation runs without calling the API",
    )
    return parser.parse_args(argv)


def slugify(value: str) -> str:
    """Return a filesystem-safe lowercase slug, or ``recipes`` when empty."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "recipes"


def build_recipe_url(search: str, ingredients: str, page: int, per_page: int) -> str:
    """Build a Recipe API URL, raising ``ValueError`` for invalid paging inputs."""
    if page < 1:
        raise ValueError("--page must be 1 or greater")
    if not 1 <= per_page <= 50:
        raise ValueError("--per-page must be between 1 and 50")
    params: dict[str, Any] = {"search": search, "page": page, "per_page": per_page}
    if ingredients.strip():
        params["ingredients"] = ingredients
    return f"{BASE_URL}?{urlencode(params)}"


def fetch_json(url: str, api_key: str) -> tuple[str, dict[str, Any]]:
    """Fetch JSON from Recipe API and return both raw text and decoded content."""
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "weeknight-recipe-scout/1.0",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        raw_text = response.read().decode("utf-8")
    return raw_text, json.loads(raw_text)


def validate_recipe_payload(payload: dict[str, Any]) -> RecipeResponse:
    """Validate provider content, raising Pydantic ``ValidationError`` on drift."""
    return RecipeResponse.model_validate(payload)


def normalize_recipe(recipe: RecipeItem) -> dict[str, Any]:
    """Convert a provider recipe into the stable processed-output schema."""
    ingredients = recipe.ingredients if isinstance(recipe.ingredients, list) else []
    instructions = recipe.instructions if isinstance(recipe.instructions, list) else []
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "cuisine": recipe.cuisine,
        "difficulty": recipe.difficulty,
        "meal_type": recipe.meal_type,
        "prep_time_minutes": recipe.prep_time_minutes,
        "calories": recipe.calories,
        "ingredients": ingredients[:10],
        "instruction_count": len(instructions),
    }


def recommend_recipes(
    recipes: Sequence[dict[str, Any]], max_prep: int, max_calories: int
) -> list[dict[str, Any]]:
    """Filter complete recipes to user limits and rank fastest, then lowest calorie."""
    if max_prep < 0 or max_calories < 0:
        raise ValueError("recommendation limits must be zero or greater")
    eligible = [
        dict(recipe)
        for recipe in recipes
        if isinstance(recipe.get("prep_time_minutes"), int)
        and isinstance(recipe.get("calories"), int)
        and recipe["prep_time_minutes"] <= max_prep
        and recipe["calories"] <= max_calories
    ]
    eligible.sort(
        key=lambda recipe: (
            recipe["prep_time_minutes"],
            recipe["calories"],
            str(recipe.get("name") or ""),
        )
    )
    for rank, recipe in enumerate(eligible, start=1):
        recipe["recommendation_rank"] = rank
    return eligible


def summarize_payload(
    response: RecipeResponse,
    query: dict[str, Any],
    max_prep: int = 30,
    max_calories: int = 650,
) -> dict[str, Any]:
    """Create the processed summary and user-specific weeknight recommendations."""
    normalized = [normalize_recipe(recipe) for recipe in response.data]
    recommendations = recommend_recipes(normalized, max_prep, max_calories)
    return {
        "query": query,
        "recommendation_limits": {
            "max_prep_minutes": max_prep,
            "max_calories": max_calories,
        },
        "counts": {
            "recipes_returned": len(normalized),
            "recommendations": len(recommendations),
            "current_page": response.meta.current_page,
            "last_page": response.meta.last_page,
            "per_page": response.meta.per_page,
            "total": response.meta.total,
        },
        "recommendations": recommendations,
        "recipes": normalized,
        "links": {
            "first": response.links.first,
            "last": response.links.last,
            "prev": response.links.prev,
            "next": response.links.next,
        },
        "meta": {"path": response.meta.path, "language": response.meta.language},
    }


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write indented, key-sorted JSON, creating parent directories as needed."""
    write_text(path, json.dumps(payload, indent=2, sort_keys=True))


def make_output_stem(search: str, page: int, fetched_at: datetime) -> str:
    """Build the timestamped base name used for raw and processed files."""
    return f"{slugify(search)}-page{page}-{fetched_at.strftime('%Y%m%dT%H%M%SZ')}"


def configure_logging(log_level: str, log_file: str | None) -> logging.Logger:
    """Configure terminal logging and, when requested, a UTF-8 file log."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()
    root.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    return logging.getLogger(LOGGER_NAME)


def print_summary(
    summary: dict[str, Any], raw_path: Path, processed_path: Path
) -> None:
    """Print paths and a concise recommendation result for a completed run."""
    counts = summary["counts"]
    print(f"Recipes returned: {counts['recipes_returned']}")
    print(f"Weeknight matches: {counts['recommendations']}")
    if summary["recommendations"]:
        best = summary["recommendations"][0]
        print(
            f"Top pick: {best['name']} ({best['prep_time_minutes']} min, {best['calories']} calories)"
        )
    print(f"Raw response: {raw_path}")
    print(f"Processed summary: {processed_path}")


def run(
    api_key: str,
    search: str,
    ingredients: str,
    page: int,
    per_page: int,
    max_prep: int = 30,
    max_calories: int = 650,
    logger: logging.Logger | None = None,
) -> tuple[dict[str, Any], Path, Path]:
    """Fetch one page, validate it, save evidence, and return its summary and paths."""
    logger = logger or logging.getLogger(LOGGER_NAME)
    if not api_key:
        raise RuntimeError(
            "RECIPE_API_KEY is missing. Put it in .env or pass --api-key."
        )
    query = {
        "search": search,
        "ingredients": ingredients,
        "page": page,
        "per_page": per_page,
    }
    url = build_recipe_url(search, ingredients, page, per_page)
    logger.info("Fetching recipes: %s", query)
    fetched_at = datetime.now(UTC)
    raw_text, payload = fetch_json(url, api_key)
    response = validate_recipe_payload(payload)
    output_stem = make_output_stem(search, page, fetched_at)
    raw_path = RAW_DIR / f"{output_stem}.raw.json"
    processed_path = PROCESSED_DIR / f"{output_stem}.processed.json"
    summary = summarize_payload(response, query, max_prep, max_calories)
    write_text(raw_path, raw_text)
    write_json(processed_path, summary)
    logger.info("Wrote raw response to %s and summary to %s", raw_path, processed_path)
    return summary, raw_path, processed_path


def main() -> int:
    """Run the command-line application and translate expected failures into messages."""
    load_dotenv_file()
    args = parse_args()
    logger = configure_logging(args.log_level, args.log_file)
    database_path = Path(args.database)
    if args.show_history:
        history = list_recent_runs(database_path)
        if not history:
            print(f"No saved runs in {database_path}.")
        for item in history:
            top = item["top_name"] or "no qualifying recipe"
            print(f"{item['recorded_at']} | {item['search']} | {top}")
        return 0
    try:
        summary, raw_path, processed_path = run(
            args.api_key,
            args.search,
            args.ingredients,
            args.page,
            args.per_page,
            args.max_prep,
            args.max_calories,
            logger,
        )
        print_summary(summary, raw_path, processed_path)
        if not args.no_history:
            history_id = record_run(database_path, summary, processed_path)
            print(f"History record: {history_id} in {database_path}")
        return 0
    except HTTPError as exc:
        logger.error("Recipe API request failed with HTTP %s", exc.code)
        print(
            f"Error: Recipe API returned HTTP {exc.code}. Check the key, query, and service status."
        )
    except URLError as exc:
        logger.error("Recipe API request could not be reached: %s", exc.reason)
        print(f"Error: Recipe API could not be reached: {exc.reason}")
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.error("Recipe API response was unusable: %s", exc)
        print(f"Error: Recipe API returned unexpected data: {exc}")
    except (RuntimeError, ValueError) as exc:
        logger.error("Configuration error: %s", exc)
        print(f"Error: {exc}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
