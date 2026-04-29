# Project State

**Last updated:** 2026-04-29
**Branch:** main (Phase 2 merged at v0.2.0)

## Done

### Phase 1 (v0.1.0)
- Flask app, all 9 SQLAlchemy models, auth, assessment workspace, admin review, Excel export
- DoD ZT + CISA ZT framework fixtures

### Phase 2 (v0.2.0)
- Privacy scrub pipeline: token map (Layer 1) + regex scrub (Layer 2) + rehydration (Layer 3)
- Word-boundary-safe token replacement (prevents partial-word false matches)
- ai_service.py: prompt builder, prompt injection defense, Anthropic API client
- report_generator.py: generate_findings (batch) + regenerate_finding (single)
- Severity formula: gap_size × pillar_weight → critical/high/medium/low
- Admin findings page with stale indicators and per-finding regenerate
- Placeholder mode when no API key set
- 77 tests passing

## In Progress
- Nothing

## Blocked
- Nothing

## Next Up (Phase 3)
1. **HTMX auto-save** on pillar response forms (replaces manual submit per pillar)
2. **Admin password gate timeout** — improve UX so timeout doesn't silently drop form data
3. **SharePoint integration** — Microsoft Graph API upload of Excel files on finalization
4. **DB nightly backup** to SharePoint
5. **Rate limiting** — Flask-Limiter on login + regenerate endpoints

## Phase 4
- CISA ZT framework UI parity (fixture exists, routes/templates need it)
- Reopen-for-revision stale-finding marking
- Audit log views in UI

## Phase 5 (hardening)
- spaCy NER pass (Layer 2b of scrub pipeline — deferred from Phase 2)
- Application Insights / structured logging
- Deploy automation from GitHub Actions

## Known Issues / Tech Debt
- Admin route `_require_admin()` returns redirect — brittle pattern; should be a decorator
- No rate limiting yet on login/regenerate endpoints
- spaCy NER not implemented (Phase 5)
- HTMX auto-save not yet wired (Phase 3)
