"""Behavior and documentation-contract tests for Weeknight Recipe Scout."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import main

FIXTURE = Path(__file__).parent / "fixtures" / "recipe_response_success.json"


def load_fixture() -> dict[str, object]:
    """Load the committed provider-shaped test response."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_build_recipe_url_and_bounds() -> None:
    """URL encoding preserves all supported provider query parameters."""
    url = main.build_recipe_url("chicken", "tomato,basil", 2, 7)
    assert "ingredients=tomato%2Cbasil" in url and "page=2" in url and "per_page=7" in url
    with pytest.raises(ValueError, match="between 1 and 50"):
        main.build_recipe_url("chicken", "", 1, 51)


def test_summarize_ranks_weeknight_matches() -> None:
    """Only recipes within both limits appear, ordered by prep time."""
    response = main.validate_recipe_payload(load_fixture())
    summary = main.summarize_payload(response, {"search": "chicken", "ingredients": "", "page": 1, "per_page": 2}, max_prep=30, max_calories=600)
    assert summary["counts"]["recipes_returned"] == 2
    assert summary["counts"]["recommendations"] == 1
    assert summary["recommendations"][0]["name"] == "Chicken Pasta"
    assert summary["recommendations"][0]["recommendation_rank"] == 1


def test_recommendations_exclude_missing_measurements() -> None:
    """Unknown prep time or calories never become an unearned recommendation."""
    recipes = [{"name": "Unknown", "prep_time_minutes": None, "calories": 200}, {"name": "Fast", "prep_time_minutes": 10, "calories": 300}]
    assert [item["name"] for item in main.recommend_recipes(recipes, 30, 600)] == ["Fast"]


def test_validation_rejects_missing_data() -> None:
    """A response without the required data list fails validation."""
    with pytest.raises(ValidationError):
        main.validate_recipe_payload({"links": {}, "meta": {}})


def test_cli_help_names_the_user_filters(capsys: pytest.CaptureFixture[str]) -> None:
    """The point-of-use help stays aligned with the core comparison feature."""
    with pytest.raises(SystemExit) as exc_info:
        main.parse_args(["--help"])
    assert exc_info.value.code == 0
    help_text = capsys.readouterr().out
    assert "--max-prep" in help_text and "--max-calories" in help_text


def test_data_dictionary_covers_processed_fields() -> None:
    """Every stable top-level processed field is named in the data dictionary."""
    dictionary = Path("docs/data-dictionary.md").read_text(encoding="utf-8")
    for field in ["query", "recommendation_limits", "counts", "recommendations", "recipes", "links", "meta"]:
        assert f"`{field}`" in dictionary
