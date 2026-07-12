# Practicum 3 Submission

Operating system: Windows
Terminal used: Git Bash
Codex tool used: ChatGPT/Codex
GitHub repository URL: https://github.com/Gennisse/insy7970-sprint-practicum.git

## Setup notes

- Project folder path: `C:\Users\forte\insy7970-sprint-practicum`
- `uv run main.py` did not work at the starting point. It failed with:
  - `error: Failed to initialize cache at C:\Users\forte\AppData\Local\uv\cache`
  - `Caused by: failed to open file C:\Users\forte\AppData\Local\uv\cache\sdists-v9\.git: Access is denied. (os error 5)`
- `uv init` created the starter scaffold files for the project, including `main.py`, `pyproject.toml`, and `README.md`.
- `.gitignore` excludes `.venv/` and cache folders such as `__pycache__/`, `.pytest_cache/`, and `.ruff_cache/`.

## Sprint 1 summary

- Codex prompt used before editing `sprint1.md`: `Read docs/specs/sprint1.md. Help me expand this into a complete sprint spec with plan, tasks, out of scope items, and a definition of done. Do not edit code yet.`
- I defined the user requirements by keeping them short, concrete, and focused on what a user needs from the tool instead of how to implement it. I started with the required basics from the instructions and added a couple of nearby needs that fit a first CSV-inspection sprint, like showing column names and handling unreadable files. That kept the sprint realistic without making it too broad.
- One thing Codex added that helped me think more clearly was the explicit error-handling requirement for unreadable CSV files, which made the sprint scope easier to test and verify.
- Sprint 1 commit: `4a150c3` (`Add sprint specs and submission notes`)
- The Sprint 1 files are visible on GitHub at the repository URL above after the push to `origin/main` completed successfully.

## Sprint 2 summary

## Workflow reflection

## Practicum feedback

## Unresolved question
