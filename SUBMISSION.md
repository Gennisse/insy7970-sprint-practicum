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
- To check the implementation shape, I compared the Sprint 2 spec against the existing Sprint 1 behavior, reread the repo scaffold, and verified that the new theme stayed tied to one coherent feature area instead of drifting into unrelated analytics. The main finding was that the existing project still only has the starter scaffold, so Sprint 2 should extend the summary output before adding anything more advanced.
- Sprint 2 commit: `542c3e2` (`Update submission notes with sprint commit`)
- Sprint 2 was pushed to GitHub successfully on `origin/main` after the commit.
- Sprint 2 definition of done was not fully met yet in code because the repository still contains the starter CLI; the spec now defines the next implementation target clearly.

## Workflow reflection

## Practicum feedback

## Unresolved question
