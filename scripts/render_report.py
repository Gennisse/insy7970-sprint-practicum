"""Render the Quarto PDF with the active project Python environment."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_SOURCE = PROJECT_ROOT / "reports" / "weeknight-recipe-report.qmd"


def find_quarto(environment: Mapping[str, str] = os.environ) -> str:
    """Return the configured Quarto executable or raise an actionable error."""
    configured = environment.get("QUARTO_BIN")
    executable = configured or shutil.which("quarto")
    if executable is None:
        raise RuntimeError(
            "Quarto was not found. Install Quarto and confirm `quarto --version` works."
        )
    return executable


def build_command(quarto: str) -> list[str]:
    """Build the fixed command that renders the authoritative report to PDF."""
    return [quarto, "render", str(REPORT_SOURCE), "--to", "pdf"]


def render_report(environment: Mapping[str, str] = os.environ) -> int:
    """Run Quarto with ``QUARTO_PYTHON`` fixed to this Python interpreter."""
    render_environment = dict(environment)
    render_environment["QUARTO_PYTHON"] = sys.executable
    completed = subprocess.run(
        build_command(find_quarto(environment)),
        cwd=PROJECT_ROOT,
        env=render_environment,
        check=False,
    )
    return completed.returncode


def main(argv: Sequence[str] | None = None) -> int:
    """Render the report and translate missing-tool configuration into an error."""
    del argv  # Reserved for future report-build options.
    try:
        return render_report()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
