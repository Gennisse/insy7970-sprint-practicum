from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a CSV file.")
    parser.add_argument("csv_path", help="Path to the CSV file to inspect")
    parser.add_argument(
        "--head",
        type=int,
        default=5,
        help="Number of example rows to show",
    )
    return parser.parse_args()


def read_csv_rows(csv_path: Path) -> tuple[list[str], list[list[str]]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration:
            return [], []

        rows = [row for row in reader]
        return headers, rows


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    if not headers:
        return "(no data)"

    column_count = len(headers)
    normalized_rows = [row[:column_count] + [""] * max(0, column_count - len(row)) for row in rows]
    widths = [len(header) for header in headers]

    for row in normalized_rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def format_row(values: Iterable[str]) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    lines = [format_row(headers), "-+-".join("-" * width for width in widths)]
    lines.extend(format_row(row) for row in normalized_rows)
    return "\n".join(lines)


def inspect_csv(csv_path: Path, head: int) -> str:
    if head < 0:
        raise ValueError("--head must be zero or greater")

    headers, rows = read_csv_rows(csv_path)
    row_count = len(rows)
    preview_rows = rows[:head]

    lines = [f"File: {csv_path}", f"Row count: {row_count}"]
    if headers:
        lines.append("Column names: " + ", ".join(headers))
    else:
        lines.append("Column names: (none)")

    lines.append("")
    lines.append(f"Example rows (first {min(head, row_count)} of {row_count}):")

    if not preview_rows:
        lines.append("(no example rows to show)")
    else:
        lines.append(format_table(headers, preview_rows))
        if row_count < head:
            lines.append("")
            lines.append(f"Requested {head} rows, but only {row_count} were available.")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv_path)

    try:
        report = inspect_csv(csv_path, args.head)
    except FileNotFoundError:
        print(f"Error: file not found: {csv_path}")
        raise SystemExit(1)
    except IsADirectoryError:
        print(f"Error: expected a CSV file, but found a directory: {csv_path}")
        raise SystemExit(1)
    except ValueError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    print(report)


if __name__ == "__main__":
    main()
