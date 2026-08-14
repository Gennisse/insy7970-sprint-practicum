$ErrorActionPreference = "Stop"

Write-Host "Checking formatting..."
uv run ruff format --check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Checking lint..."
uv run ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running tests..."
uv run pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Building portable distributions..."
uv build --no-sources
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
