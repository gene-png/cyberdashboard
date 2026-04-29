# Project State

**Last updated:** 2026-04-29
**Branch:** feat/phase1-skeleton (ready to merge to main)

## Done (Phase 1)

- Full Flask app with all 9 SQLAlchemy models
- DoD ZT and CISA ZT framework JSON fixtures
- Auth: Flask-Login + admin password gate (15-min timeout)
- Dashboard, new assessment wizard
- Assessment workspace: tool inventory, pillar responses, submit flow
- Admin review: scoring, finalize, reopen
- Excel export: customer + consultant reports (openpyxl)
- 27 pytest tests — all passing
- Smoke test — passing
- CSRF on all forms, bleach input sanitization

## In Progress

- Nothing

## Blocked

- Nothing

## Next Up (Phase 2)

1. **Anthropic API integration** — ai_service.py, prompt builder per spec §6.1
2. **Privacy scrub pipeline** — scrub_service.py: token map, regex layer, rehydrate
3. **Gap finding generation** — identify gaps, call AI, store scrubbed/rehydrated in gap_finding
4. **Per-finding regeneration** — admin "Regenerate" button, audit log
5. **AI guidance in Excel export** — wire rehydrated_response into Gap Register sheet

## Phase 3 (after Phase 2)
- HTMX auto-save on response forms
- SharePoint integration via Microsoft Graph API
- DB backup job (nightly export to SharePoint)

## Phase 4
- CISA ZT framework UI (fixture exists, needs route/template parity)
- Reopen-for-revision stale-finding marking
- Audit log views in UI

## Known Issues / Tech Debt
- Admin route `_require_admin()` returns a redirect object but callers must check if the return value is not None — brittle; should use a decorator instead (low priority for Phase 1)
- No rate limiting yet on login (Flask-Limiter installed, not wired up)
- spaCy NER not implemented (Phase 2 scope)
