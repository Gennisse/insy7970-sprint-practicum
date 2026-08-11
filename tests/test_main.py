"""Behavior and documentation-contract tests for Weeknight Recipe Scout."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import main
from history import list_recent_runs, record_run
from scripts import render_report

FIXTURE = Path(__file__).parent / "fixtures" / "recipe_response_success.json"


def load_fixture() -> dict[str, object]:
    """Load the committed provider-shaped test response."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_build_recipe_url_and_bounds() -> None:
    """URL encoding preserves all supported provider query parameters."""
    url = main.build_recipe_url("chicken", "tomato,basil", 2, 7)
    assert (
        "ingredients=tomato%2Cbasil" in url and "page=2" in url and "per_page=7" in url
    )
    with pytest.raises(ValueError, match="between 1 and 50"):
        main.build_recipe_url("chicken", "", 1, 51)


def test_summarize_ranks_weeknight_matches() -> None:
    """Only recipes within both limits appear, ordered by prep time."""
    response = main.validate_recipe_payload(load_fixture())
    summary = main.summarize_payload(
        response,
        {"search": "chicken", "ingredients": "", "page": 1, "per_page": 2},
        max_prep=30,
        max_calories=600,
    )
    assert summary["counts"]["recipes_returned"] == 2
    assert summary["counts"]["recommendations"] == 1
    assert summary["recommendations"][0]["name"] == "Chicken Pasta"
    assert summary["recommendations"][0]["recommendation_rank"] == 1


def test_recommendations_exclude_missing_measurements() -> None:
    """Unknown prep time or calories never become an unearned recommendation."""
    recipes = [
        {"name": "Unknown", "prep_time_minutes": None, "calories": 200},
        {"name": "Fast", "prep_time_minutes": 10, "calories": 300},
    ]
    assert [item["name"] for item in main.recommend_recipes(recipes, 30, 600)] == [
        "Fast"
    ]


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
    for field in [
        "query",
        "recommendation_limits",
        "counts",
        "recommendations",
        "recipes",
        "links",
        "meta",
    ]:
        assert f"`{field}`" in dictionary


def test_report_wrapper_pins_quarto_to_active_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The documented build cannot silently select a system Python kernel."""
    observed: dict[str, object] = {}

    def fake_run(
        command: Sequence[str],
        *,
        cwd: Path,
        env: dict[str, str],
        check: bool,
    ) -> SimpleNamespace:
        observed.update(command=command, cwd=cwd, env=env, check=check)
        return type("Completed", (), {"returncode": 0})()

    monkeypatch.setattr(render_report.subprocess, "run", fake_run)

    result = render_report.render_report({"QUARTO_BIN": "quarto-test"})

    assert result == 0
    assert observed["command"] == [
        "quarto-test",
        "render",
        str(render_report.REPORT_SOURCE),
        "--to",
        "pdf",
    ]
    assert observed["cwd"] == render_report.PROJECT_ROOT
    assert observed["env"]["QUARTO_PYTHON"] == render_report.sys.executable
    assert observed["check"] is False


def test_sqlite_history_records_and_orders_runs(tmp_path: Path) -> None:
    """Recommendation history persists the decision context and newest top pick."""
    response = main.validate_recipe_payload(load_fixture())
    summary = main.summarize_payload(
        response,
        {"search": "chicken", "ingredients": "", "page": 1, "per_page": 2},
        max_prep=30,
        max_calories=600,
    )
    database = tmp_path / "history.sqlite3"

    history_id = record_run(database, summary, Path("processed.json"))
    rows = list_recent_runs(database)

    assert history_id == 1
    assert rows[0]["search"] == "chicken"
    assert rows[0]["top_name"] == "Chicken Pasta"
    assert rows[0]["max_prep_minutes"] == 30


def test_history_requires_positive_limit(tmp_path: Path) -> None:
    """Invalid history limits fail before opening a database."""
    with pytest.raises(ValueError, match="at least 1"):
        list_recent_runs(tmp_path / "history.sqlite3", limit=0)
