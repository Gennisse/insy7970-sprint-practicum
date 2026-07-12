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

- Sprint 2 theme: preview example rows with a `--head N` option while keeping the Sprint 1 summary behavior.
- Codex prompt used before editing `sprint2.md`: `Update docs/specs/sprint2.md so Sprint 2 focuses on previewing example rows from the CSV. Keep the spec concise, include a new theme, 3-5 user requirements, and make sure it still builds on Sprint 1 behavior. Do not edit code yet.`
- To check the implementation, I ran the CLI on `data/test.csv` with `--head 3` and reviewed the output to make sure it still showed the row count and column names from Sprint 1 while adding a readable example-row table. I also ran the test suite with `python -m unittest discover` and confirmed it passed after adding coverage for row counting, short previews, and quoted commas.
- Sprint 2 commit: `05379ba` (`Implement Sprint 2 row preview`)
- Sprint 2 was pushed to GitHub successfully on `origin/main` after the commit.
- Sprint 2 definition of done was met because the CLI now accepts `--head N`, preserves the Sprint 1 summary, prints a readable preview, and handles short files cleanly.

## Workflow reflection

Git helped me see and control changes by making each sprint a clear commit history instead of one large edit. Starting with a problem statement and user requirements kept Codex focused on the user-facing behavior first, which made the Sprint 1 and Sprint 2 specs much easier to keep small and realistic. Codex added a few things I would not have written as quickly on my own, especially the explicit error-handling requirement in Sprint 1 and the short-file preview behavior in Sprint 2.

Before committing, I inspected `git status`, reviewed the diff, and ran the tool on the sample CSV so I could compare the real output with the tests. That check caught the one issue where `unittest discover` did not find the tests until I added the package file, which showed why running and verifying the project matters before pushing. If I did a third sprint, I would likely keep the same structure but narrow the scope even more and spend less time on output formatting.

## Practicum feedback

The most useful part of the practicum was the repeated loop of spec, implementation, inspection, and commit, because it made progress feel controlled and easy to review. The most confusing part was the moving target around where each reflection note should live, but once the sections were clear, the instructions were straightforward enough to follow.

## Unresolved question

None at this stage.
