"""Build the dashboard CSV from validated, processed Recipe API snapshots."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse processed input paths and the CSV output path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def retrieval_time(path: Path) -> str:
    """Extract an ISO-like UTC timestamp from a processed snapshot filename."""
    match = re.search(r"(\d{8}T\d{6}Z)", path.name)
    return match.group(1) if match else "unknown"


def build_snapshot(inputs: list[Path], output: Path) -> int:
    """Merge and deduplicate processed recipes, then write a portable CSV."""
    rows: dict[str, dict[str, Any]] = {}
    for path in inputs:
        summary = json.loads(path.read_text(encoding="utf-8"))
        source_search = str(summary["query"]["search"])
        for recipe in summary["recipes"]:
            key = str(recipe.get("id") or recipe.get("name"))
            rows.setdefault(
                key,
                {
                    **recipe,
                    "source_search": source_search,
                    "retrieved_at_utc": retrieval_time(path),
                },
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "name",
        "description",
        "cuisine",
        "difficulty",
        "meal_type",
        "prep_time_minutes",
        "cook_time_minutes",
        "total_time_minutes",
        "calories",
        "protein_grams",
        "servings",
        "dietary_tags",
        "ingredients",
        "instructions",
        "instruction_count",
        "source_search",
        "retrieved_at_utc",
    ]
    with output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        for recipe in rows.values():
            recipe = dict(recipe)
            recipe["ingredients"] = "|".join(recipe.get("ingredients") or [])
            recipe["instructions"] = "|".join(recipe.get("instructions") or [])
            recipe["dietary_tags"] = "|".join(recipe.get("dietary_tags") or [])
            writer.writerow({field: recipe.get(field) for field in fieldnames})
    return len(rows)


def main() -> int:
    """Run the snapshot builder and print the number of exported recipes."""
    args = parse_args()
    count = build_snapshot(args.inputs, args.output)
    print(f"Wrote {count} recipes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
