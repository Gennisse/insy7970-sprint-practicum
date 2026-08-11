#!/usr/bin/env bash
set -e

echo "Checking formatting..."
uv run ruff format --check .

echo "Checking lint..."
uv run ruff check .

echo "Running tests..."
uv run pytest

echo "Building portable distributions..."
uv build --no-sources
