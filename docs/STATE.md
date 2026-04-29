# Project State

**Last updated:** 2026-04-29
**Branch:** main (Phase 3 merged at v0.3.0)

## Done

### Phase 1 (v0.1.0)
- Flask app, all 9 SQLAlchemy models, auth, assessment workspace, admin review, Excel export
- DoD ZT + CISA ZT framework fixtures

### Phase 2 (v0.2.0)
- Privacy scrub pipeline + Anthropic API integration + gap finding generation

### Phase 3 (v0.3.0)
- HTMX auto-save (per-activity blur → POST → inline "Saved" indicator)
- Rate limiting: login (5/15 min), regenerate (10/min)
- SharePoint service: Graph API client-credentials auth, folder create, file upload
- Finalize → SharePoint: both Excel files + response snapshot + audit CSVs
- scripts/backup_db.py: nightly DB backup with 30-day retention prune
- Admin session countdown timer in navbar
- 102 tests passing

## In Progress
- Nothing

## Blocked
- Nothing

## Next Up (Phase 4)
1. **CISA ZT framework UI parity** — the fixture exists; routes/templates need to handle `cisa_zt` maturity states (traditional/initial/advanced/optimal vs DoD's not_met/partial/target/advanced)
2. **Audit log view** — admin page showing the full audit_log for an assessment
3. **Sensitive terms UI** — let admin add/remove extra sensitive terms on an assessment
4. Stale-finding marking already works; ensure it's visible across all views

## Phase 5 (hardening)
- spaCy NER pass (Layer 2b of scrub — deferred from Phase 2)
- Structured logging / Application Insights
- GitHub Actions deploy automation
- HTTPS force-redirect in Flask (App Service provides HTTPS by default)

## Known Issues / Tech Debt
- Admin route `_require_admin()` returns redirect — should be a decorator
- smoke_test.sh uses inline Python instead of `flask run` (bash backgrounding issue in container)
