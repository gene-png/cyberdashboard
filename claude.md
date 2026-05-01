# Project: Zero Trust Maturity Assessment Dashboard

## Source of truth (READ-ONLY)
The spec lives at:
`./spec/Zero Trust Maturity Assessment Dashboard.docx`

Use `pandoc spec/*.docx -t plain` to read it. Refer back as needed.
This file is reference material — do not edit, move, or delete it.

## Hard rules — file access
- All work happens inside this repo (`/workspace`).
- The `./spec/` folder is read-only — never modify, write to, or delete from it.
- You are running inside a Docker container; nothing exists outside `/workspace` from your perspective, and that is correct.
- If asked to "save" or "export" anything, it goes in this repo, not anywhere else.

## Continuity between sessions
You have no memory between sessions except this file and what's in the repo. Treat the repo as your second brain.

**At the START of every session:**
1. Read this file (CLAUDE.md).
2. Read `docs/STATE.md` — current status, what's in flight, what's next.
3. Read the latest entries in `docs/decisions/`.
4. Run `git log --oneline -20` and `git status`.
5. Run `pytest -q` to confirm the codebase is in a known-good state.

**At the END of every session, or before any significant pause:**
1. Update `docs/STATE.md` with: done, in progress, blocked, next up.
2. Add an entry to `docs/decisions/` for any non-obvious choice made.
3. Update `CHANGELOG.md` under `## [Unreleased]`.
4. Commit and push — uncommitted work is lost work.

**If your context is filling up,** proactively write a handoff note to `docs/STATE.md` and tell the user to start a fresh session.

## Version control — work like a real developer
- Commit early and often with semantic messages: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- Feature branches per piece of work: `feat/scoring-engine`, `feat/dashboard-ui`, etc.
- Merge to `main` only when tests pass.
- Tag releases with semver: `v0.1.0`, `v0.2.0`, `v1.0.0`.
- **Push after every commit.** Treat unpushed work as work that doesn't exist.
- For each tagged release, snapshot a readable copy under `releases/v0.1.0/` etc.

## Stack
- Python 3.11+, Flask, SQLite (or whatever the spec calls for).
- Virtual environment at `./.venv` (gitignored, set up by the container).
- Pin all dependencies in `requirements.txt`.
- Tests with `pytest`, organized under `tests/`.
- Run Flask with `flask --app app run --host=0.0.0.0 --port=5000` (host 0.0.0.0 is required for the container's port forwarding to work).

## Repo layout
```
/
├── app/                    # Flask app
├── tests/                  # pytest suite
├── spec/                   # READ-ONLY source spec (gitignored)
├── docs/
│   ├── STATE.md            # current project state, rewritten each session
│   ├── plans/              # one .md per task, written before coding
│   └── decisions/          # ADRs for non-obvious choices
├── releases/               # human-readable snapshots per tagged version
├── scripts/                # utility scripts (smoke test, seed data, etc.)
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── .gitignore
└── CLAUDE.md
```

## Workflow for every task
1. Write a short plan in `docs/plans/<task-slug>.md` before coding.
2. Write failing tests with pytest first.
3. Implement until tests pass.
4. After every change, run:
   - `pytest -q`
   - `scripts/smoke_test.sh` (boots Flask, hits each route, asserts 200, kills the server)
5. If anything fails, debug and iterate **without asking** — only ask if blocked on a real ambiguity in the spec.
6. Update `CHANGELOG.md` under `## [Unreleased]`.
7. Commit when a logical chunk is done. Push.
8. When a milestone is reached, merge to `main`, tag, snapshot to `releases/`.

## About this file
Keep `CLAUDE.md` under ~200 lines. It loads into context every session, so brevity matters. If guidance grows past a few lines on any topic, move it into `docs/` and reference it here with a one-liner.