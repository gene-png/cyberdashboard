# Project: Zero Trust Maturity Assessment Dashboard

## Source of truth
The spec lives in ./spec.pdf. Read it first and build from it.

## Stack
- Python 3.11+, Flask, SQLite (or whatever fits the spec)
- Use a venv at ./.venv
- Pin deps in requirements.txt

## Workflow you should follow
1. Write a short plan from the spec before coding.
2. Write failing tests with pytest first.
3. Implement until tests pass.
4. After every change, run: `pytest -q` and `flask --app app run` against
   a smoke-test script that hits each route and checks status 200.
5. If anything fails, debug and iterate without asking — only ask if you're
   blocked on a real ambiguity in the spec.
6. Keep a CHANGELOG.md as you go so I can review what you did.