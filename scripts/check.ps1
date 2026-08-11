$ErrorActionPreference = "Stop"

Write-Host "Checking formatting..."
uv run ruff format --check .

Write-Host "Checking lint..."
uv run ruff check .

Write-Host "Running tests..."
uv run pytest

Write-Host "Building portable distributions..."
uv build --no-sources
