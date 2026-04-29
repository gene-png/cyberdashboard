# Project State

**Last updated:** 2026-04-29
**Branch:** main (Phase 4 merged at v0.4.0)

## Done

### Phase 1 (v0.1.0)
- Flask app, all 9 SQLAlchemy models, auth, assessment workspace, admin review, Excel export
- DoD ZT + CISA ZT framework fixtures

### Phase 2 (v0.2.0)
- Privacy scrub pipeline + Anthropic API integration + gap finding generation

### Phase 3 (v0.3.0)
- HTMX auto-save (per-activity change → POST → inline "Saved" indicator)
- Rate limiting: login (5/15 min), regenerate (10/min)
- SharePoint service: Graph API client-credentials auth, folder create, file upload
- Finalize → SharePoint: both Excel files + response snapshot + audit CSVs
- scripts/backup_db.py: nightly DB backup with 30-day retention prune
- Admin session countdown timer in navbar
- 102 tests passing

### Phase 4 (v0.4.0)
- CISA ZT framework fully verified end-to-end (pillar page, HTMX auto-save, Excel, report generator)
- Excel service now framework-agnostic: `gap_large`/`gap_small` keys, generic column headers
- Admin audit log view: `/admin/assessments/{id}/audit` — full log table, newest-first, with username
- Sensitive terms management UI: `/admin/assessments/{id}/terms` — add/deactivate terms with audit trail
- 130 tests passing

## In Progress
- Nothing

## Blocked
- Nothing

## Next Up (Phase 5 — hardening)
1. spaCy NER pass (Layer 2b of scrub — deferred from Phase 2)
2. Structured logging / Application Insights
3. GitHub Actions deploy automation
4. HTTPS force-redirect

## Known Issues / Tech Debt
- Admin route `_require_admin()` returns redirect — should be a decorator
- smoke_test.sh uses inline Python thread instead of `flask run` (bash backgrounding issue in container)
