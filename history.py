"""Persist and retrieve recipe recommendation runs in a local SQLite database."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipe_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at TEXT NOT NULL,
    search TEXT NOT NULL,
    max_prep_minutes INTEGER NOT NULL,
    max_calories INTEGER NOT NULL,
    recipes_returned INTEGER NOT NULL,
    recommendations INTEGER NOT NULL,
    top_name TEXT,
    top_prep_minutes INTEGER,
    top_calories INTEGER,
    processed_path TEXT NOT NULL
)
"""


def connect_database(path: Path) -> sqlite3.Connection:
    """Open the run-history database and create its schema when necessary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    connection.commit()
    return connection


def record_run(
    path: Path,
    summary: dict[str, Any],
    processed_path: Path,
    recorded_at: datetime | None = None,
) -> int:
    """Store one processed result and return its generated history identifier."""
    timestamp = recorded_at or datetime.now(UTC)
    top = summary["recommendations"][0] if summary["recommendations"] else {}
    values = (
        timestamp.isoformat(),
        str(summary["query"]["search"]),
        int(summary["recommendation_limits"]["max_prep_minutes"]),
        int(summary["recommendation_limits"]["max_calories"]),
        int(summary["counts"]["recipes_returned"]),
        int(summary["counts"]["recommendations"]),
        top.get("name"),
        top.get("prep_time_minutes"),
        top.get("calories"),
        str(processed_path),
    )
    with connect_database(path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO recipe_runs (
                recorded_at, search, max_prep_minutes, max_calories,
                recipes_returned, recommendations, top_name,
                top_prep_minutes, top_calories, processed_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        return int(cursor.lastrowid)


def list_recent_runs(path: Path, limit: int = 10) -> list[dict[str, Any]]:
    """Return newest saved runs as dictionaries, or an empty list if absent."""
    if limit < 1:
        raise ValueError("history limit must be at least 1")
    if not path.exists():
        return []
    with connect_database(path) as connection:
        rows = connection.execute(
            "SELECT * FROM recipe_runs ORDER BY recorded_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
